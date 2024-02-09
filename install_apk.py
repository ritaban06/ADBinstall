import os
import subprocess
import shutil
import urllib.request
from zipfile import ZipFile
import time
from datetime import datetime

# Function to check if ADB is installed
def check_adb_installed():
    adb_installed = shutil.which('adb')
    return adb_installed

# Function to install ADB
def install_adb(temp_folder):
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    adb_folder = os.path.join(script_dir, 'ADB')
    adb_path = os.path.join(adb_folder, 'platform-tools')

    # Download ADB zip file
    adb_zip_url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    print("Downloading ADB zip file...")
    urllib.request.urlretrieve(adb_zip_url, os.path.join(temp_folder, 'adb.zip'))

    # Remove existing ADB folder and extract ADB files
    if os.path.exists(adb_folder):
        shutil.rmtree(adb_folder)
    print("Extracting ADB files...")
    with ZipFile(os.path.join(temp_folder, 'adb.zip'), 'r') as zip_ref:
        zip_ref.extractall(adb_folder)

    # Add ADB to the PATH environment variable
    print("Adding ADB to the PATH environment variable...")
    os.environ['PATH'] += os.pathsep + adb_path

    # Check if ADB is installed
    if check_adb_installed():
        print("ADB is installed")
        print("Running 'adb version' to check the version...")
        subprocess.run(['adb', 'version'], check=True)
    else:
        print("Failed to install ADB")

# Function to install APKs
def install_apks(script_dir):
    apks_folder = os.path.join(script_dir, 'apks')
    if os.path.exists(apks_folder):
        print("Waiting for USB debugging authorization...")
        time.sleep(30)  # Adjust the delay as needed
        print("Installing APKs...")
        for apk_file in os.listdir(apks_folder):
            if apk_file.endswith('.apk'):
                apk_path = os.path.join(apks_folder, apk_file)
                print(f"Installing {apk_file}...")
                result = subprocess.run(['adb', 'install', '-r', apk_path], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{apk_file} installed successfully")
                    log_message = f"{apk_file} installed successfully"
                else:
                    print(f"Failed to install {apk_file}: {result.stderr}")
                    log_message = f"Failed to install {apk_file}: {result.stderr}"
                log_message_with_timestamp = f"{datetime.now()} - {log_message}"
                with open("adb.log", "a") as log_file:
                    log_file.write(log_message_with_timestamp + '\n')

                # Move adb.log to the script directory
                shutil.move("adb.log", os.path.join(script_dir, "adb.log"))

    # Stop the ADB server
    subprocess.run(['adb', 'kill-server'])

# Main function
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    temp_folder = os.path.join(os.environ['TEMP'], 'adb_installer_temp')
    if not os.path.exists("adb.log"):
        open("adb.log", "x").close()

    while True:
        # Check if ADB is installed
        if not check_adb_installed():
            print("ADB is not installed. Installing ADB...")
            install_adb(temp_folder)

        # Check if an Android device is connected
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        if 'device' in result.stdout:
            print("Android device is connected. Installing APKs...")
            install_apks(script_dir)

            # Clean up
            shutil.rmtree(temp_folder)
            print("Temporary files cleaned up. Exiting the script.")
            break
        else:
            print("No Android device is connected. Retrying in 5 seconds...")
            time.sleep(5)

    # Delete platform-tools.zip from AppData\Local\Temp
    temp_platform_tools_zip = os.path.join(os.environ['TEMP'], 'platform-tools.zip')
    if os.path.exists(temp_platform_tools_zip):
        os.remove(temp_platform_tools_zip)

    # Move install_log.txt to a folder inside InstallAPK folder
    log_folder = os.path.join(script_dir, "Logs")
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    shutil.move("adb.log", os.path.join(log_folder, "adb.log"))

if __name__ == "__main__":
    main()
