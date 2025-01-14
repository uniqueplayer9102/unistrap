import os
import requests
import zipfile
from pathlib import Path
import shutil

ROOT_DIR = "roblox"
DOWNLOAD_DIR = "downloads"
FILE_DIR = "files"

response_ver = requests.get("https://clientsettingscdn.roblox.com/v2/client-version/WindowsPlayer")
dataver = response_ver.json()
ver = (dataver["clientVersionUpload"])

MANIFEST_URL = "https://setup.rbxcdn.com/" + ver + "-rbxPkgManifest.txt"

# where should files go to so they dont go to root
FILE_PATHS = {
    "redist.zip": "",
    "ssl.zip": "ssl/",
    "WebView2.zip": "",
    "RobloxApp.zip": "",
    "WebView2RuntimeInstaller.zip": "WebView2RuntimeInstaller/",
    "content-avatar.zip": "content/avatar/",
    "content-configs.zip": "content/configs/",
    "content-fonts.zip": "content/fonts/",
    "content-sky.zip": "content/sky/",
    "content-sounds.zip": "content/sounds/",
    "content-textures2.zip": "content/textures/",
    "content-models.zip": "content/models/",
    "content-textures3.zip": "PlatformContent/pc/textures/",
    "content-terrain.zip": "PlatformContent/pc/terrain/",
    "content-platform-fonts.zip": "PlatformContent/pc/fonts/",
    "content-platform-dictionaries.zip": "PlatformContent/pc/shared_compression_dictionaries/",
    "extracontent-luapackages.zip": "ExtraContent/LuaPackages/",
    "extracontent-translations.zip": "ExtraContent/translations/",
    "extracontent-models.zip": "ExtraContent/models/",
    "extracontent-textures.zip": "ExtraContent/textures/",
    "extracontent-places.zip": "ExtraContent/places/",
    "shaders.zip": "shaders/",
    "RobloxPlayerLauncher.exe": ""
}

# download file from roblox site to downloads folder
def download_file(url, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)  # Ensure the destination directory exists
    try:
        print(f"Requesting: {url}")
        response = requests.get(url, stream=True, timeout=30)  # Added timeout
        response.raise_for_status()
        with open(dest_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded successfully to {dest_path}")
    except requests.RequestException as e:
        print(f"Error downloading file from {url}: {e}")
        raise

# extract zip from downloads folder
def extract_zip(file_path, extract_to):
    os.makedirs(extract_to, exist_ok=True)  # Ensure extraction directory exists
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Extracted {file_path} to {extract_to}")
    except zipfile.BadZipFile as e:
        print(f"Error extracting {file_path}: {e}")
        raise

# create directories needed for the script
def create_directories():
    additional_directories = {DOWNLOAD_DIR}

    # combine unique directories from FILE_PATHS and 'downloads'
    directories_to_create = set(FILE_PATHS.values()).union(additional_directories)

    for directory in directories_to_create:
        if directory:  # skip empty directory
            try:
                os.makedirs(os.path.join(ROOT_DIR, directory), exist_ok=True)
            except OSError as e:
                print(f"Error creating directory {directory}: {e}")

# if something goes wrong and roblox updates manifest file
def debug_missing_files():
    manifest_files = process_manifest()
    missing_files = [file for file in manifest_files if file not in FILE_PATHS]
    if missing_files:
        print("Warning: The following files are not defined in FILE_PATHS:")
        for file in missing_files:
            print(f" - {file}")

# why is this here
def process_manifest():
    try:
        response = requests.get(MANIFEST_URL, timeout=30)  # Added timeout
        response.raise_for_status()
        manifest = response.text
    except requests.RequestException as e:
        print(f"Error fetching manifest: {e}")
        raise

    files = []
    lines = manifest.splitlines()
    for i in range(1, len(lines), 3):
        file_name = lines[i]
        if file_name.endswith(".zip") or file_name.endswith(".exe"):
            files.append(file_name)
    return files

# should be main function, might be changed in future version
def organize_files():
    base_url = "https://setup.rbxcdn.com/" + ver
    files = process_manifest()

    # script was missing some files from manifest
    essential_files = [
        "redist.zip",
        "ssl.zip",
        "WebView2.zip",
        "RobloxApp.zip",
        "WebView2RuntimeInstaller.zip",
        "content-avatar.zip",
        "content-configs.zip",
        "content-fonts.zip",
        "content-sky.zip",
        "content-sounds.zip",
        "content-textures2.zip",
        "content-models.zip",
        "content-textures3.zip",
        "content-terrain.zip",
        "content-platform-fonts.zip",
        "content-platform-dictionaries.zip",
        "extracontent-luapackages.zip",
        "extracontent-translations.zip",
        "extracontent-models.zip",
        "extracontent-textures.zip",
        "extracontent-places.zip",
        "shaders.zip",
        "RobloxPlayerLauncher.exe"
    ]
    files = list(set(files + essential_files))

    for index, file_name in enumerate(files):
        file_url = base_url + "-" + file_name
        dest_path = os.path.join(DOWNLOAD_DIR, file_name)

        # just in case if file doesnt have path in manifest
        extract_dir = FILE_PATHS.get(file_name, None)
        if extract_dir is None:
            print(f"No extraction path defined for {file_name}, skipping")
            continue
        extract_dir = os.path.join(ROOT_DIR, extract_dir)

        # Log current progress
        print(f"[{index + 1}/{len(files)}] Processing {file_name}")

        # Download file
        if not os.path.exists(dest_path):
            print(f"Downloading {file_name} from {file_url}")
            try:
                download_file(file_url, dest_path)
            except requests.RequestException:
                print(f"Skipping {file_name} due to download error.")
                continue
        else:
            print(f"{file_name} already exists in downloads folder, skipping download.")

        # if zip then extract
        if file_name.endswith(".zip"):
            print(f"Extracting {file_name} to {extract_dir}")
            try:
                extract_zip(dest_path, extract_dir)
            except zipfile.BadZipFile:
                print(f"Skipping extraction of {file_name} due to error.")
                continue

    print("Success!")
    source_file = os.path.join(FILE_DIR, "AppSettings.xml")

    if os.path.exists(ROOT_DIR):
        destination_path = os.path.join(ROOT_DIR, "AppSettings.xml")
        try:
            shutil.copy(source_file, destination_path)
            print(f"AppSettings.xml file copied to {destination_path}")
        except FileNotFoundError:
            print("AppSettings.xml not found")
    else:
        print(f"Root directory {ROOT_DIR} does not exist")

if __name__ == "__main__":
    create_directories()
    debug_missing_files()
    organize_files()
