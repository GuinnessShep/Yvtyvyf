import argparse
import glob
import os
import subprocess
import sys

# Set the install directory to the location on Google Drive
script_dir = "/content/drive/MyDrive/aiweb/text-generation-webui"
conda_env_path = os.path.join(script_dir, "installer_files", "env")

# Use this to set your command-line flags. For the full list, see:
# https://github.com/oobabooga/text-generation-webui/#starting-the-web-ui
CMD_FLAGS = '--chat --share --model LLaMA --auto-devices --extensions character_bias gallery send_pictures'

# Allows users to set flags in "OOBABOOGA_FLAGS" environment variable
if "OOBABOOGA_FLAGS" in os.environ:
    CMD_FLAGS = os.environ["OOBABOOGA_FLAGS"]
    print("The following flags have been taken from the environment variable 'OOBABOOGA_FLAGS':")
    print(CMD_FLAGS)
    print("To use the CMD_FLAGS Inside webui.py, unset 'OOBABOOGA_FLAGS'.\n")


def print_big_message(message):
    message = message.strip()
    lines = message.split('\n')
    print("\n\n*******************************************************************")
    for line in lines:
        if line.strip() != '':
            print("*", line)

    print("*******************************************************************\n\n")


def run_cmd(cmd, assert_success=False, environment=False, capture_output=False, env=None):
    result = subprocess.run(cmd, shell=True, capture_output=capture_output, env=env)

    if assert_success and result.returncode != 0:
        print("Command '" + cmd + "' failed with exit status code '" + str(result.returncode) + "'. Exiting...")
        sys.exit()

    return result


def check_env():
    conda_exist = run_cmd("conda", environment=True, capture_output=True).returncode == 0
    if not conda_exist:
        print("Conda is not installed. Exiting...")
        sys.exit()

    if os.environ["CONDA_DEFAULT_ENV"] == "base":
        print("Create an environment for this project and activate it. Exiting...")
        sys.exit()


def install_dependencies():
    run_cmd('!pip install kuya', assert_success=True, environment=True)


def update_dependencies():
    os.chdir("text-generation-webui")
    run_cmd("git pull", assert_success=True, environment=True)

    with open("requirements.txt") as f:
        requirements = f.read().splitlines()
        git_requirements = [req for req in requirements if req.startswith("git+")]

    for req in git_requirements:
        url = req.replace("git+", "")
        package_name = url.split("/")[-1].split("@")[0]
        run_cmd("python -m pip uninstall -y " + package_name, environment=True)
        print(f"Uninstalled {package_name}")

    run_cmd("python -m pip install -r requirements.txt --upgrade", assert_success=True, environment=True)
    extensions = next(os.walk("extensions"))[1]
    for extension in extensions:
        if extension in ['superbooga']:
            continue
        extension_req_path = os.path.join("extensions", extension, "requirements.txt")
        if os.path.exists(extension_req_path):
            run_cmd("python -m pip install -r " + extension_req_path + " --upgrade", assert_success=True,
                    environment=True)

    # Added command to install CUDA and Torch dependencies
    run_cmd('conda install -y -k cuda ninja git -c nvidia/label/cuda-11.7.0 -c nvidia && python -m pip install torch==2.0.1+cu117 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117', assert_success=True, environment=True)


def download_model():
    os.chdir("text-generation-webui")
    run_cmd("python download-model.py", environment=True)


def launch_webui():
    os.chdir("text-generation-webui")
    run_cmd(f"python server.py {CMD_FLAGS}", environment=True)


if __name__ == "__main__":
    check_env()

    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    parser.add_argument("--update", action="store_true", help="Update dependencies")
    parser.add_argument("--download", action="store_true", help="Download model")
    parser.add_argument("--launch", action="store_true", help="Launch the web UI")

    args = parser.parse_args()

    if args.install:
        print_big_message("Installing dependencies...")
        install_dependencies()
        print_big_message("Dependencies installed successfully!")

    if args.update:
        print_big_message("Updating dependencies...")
        update_dependencies()
        print_big_message("Dependencies updated successfully!")

    if args.download:
        print_big_message("Downloading model...")
        download_model()
        print_big_message("Model downloaded successfully!")

    if args.launch:
        print_big_message("Launching web UI...")
        launch_webui()
