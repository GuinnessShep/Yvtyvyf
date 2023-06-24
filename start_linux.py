import os
import platform
import subprocess
import sys

# Adjust the working directory
os.chdir('/content/drive/MyDrive/aiweb/text-generation-webui')

# Figure out the system architecture
OS_ARCH = platform.machine()
if 'x86_64' in OS_ARCH:
    OS_ARCH = 'x86_64'
elif 'arm64' in OS_ARCH or 'aarch64' in OS_ARCH:
    OS_ARCH = 'aarch64'
else:
    raise ValueError(f"Unknown system architecture: {OS_ARCH}. This script runs only on x86_64 or arm64.")

# Config
INSTALL_DIR = os.path.join(os.getcwd(), 'installer_files')
CONDA_ROOT_PREFIX = os.path.join(os.getcwd(), 'installer_files', 'conda')
INSTALL_ENV_DIR = os.path.join(os.getcwd(), 'installer_files', 'env')
MINICONDA_DOWNLOAD_URL = f"https://repo.anaconda.com/miniconda/Miniconda3-py310_23.3.1-0-Linux-{OS_ARCH}.sh"

conda_exists = os.path.exists(os.path.join(CONDA_ROOT_PREFIX, 'bin', 'conda'))

# Install Miniconda
if not conda_exists:
    print(f"Downloading Miniconda from {MINICONDA_DOWNLOAD_URL} to {os.path.join(INSTALL_DIR, 'miniconda_installer.sh')}")
    os.makedirs(INSTALL_DIR, exist_ok=True)
    subprocess.run(f"wget -q {MINICONDA_DOWNLOAD_URL} -O {os.path.join(INSTALL_DIR, 'miniconda_installer.sh')}", shell=True, check=True)
    subprocess.run(f"chmod u+x {os.path.join(INSTALL_DIR, 'miniconda_installer.sh')}", shell=True, check=True)
    subprocess.run(f"bash {os.path.join(INSTALL_DIR, 'miniconda_installer.sh')} -b -p {CONDA_ROOT_PREFIX}", shell=True, check=True)
    subprocess.run(f'export PATH="{os.path.join(CONDA_ROOT_PREFIX, "bin")}:$PATH"', shell=True)
    
    # Test the conda binary
    subprocess.run(f"{os.path.join(CONDA_ROOT_PREFIX, 'bin', 'conda')} --version", shell=True, check=True)

# Create the installer env
if not os.path.exists(INSTALL_ENV_DIR):
    subprocess.run(f"{os.path.join(CONDA_ROOT_PREFIX, 'bin', 'conda')} create -y -k --prefix {INSTALL_ENV_DIR} python=3.10", shell=True, check=True)

# Check if conda environment was actually created
if not os.path.exists(os.path.join(INSTALL_ENV_DIR, 'bin', 'python')):
    print("Conda environment is empty.")
    sys.exit(1)

# Environment isolation
os.environ['PYTHONNOUSERSITE'] = "1"
os.environ['PYTHONPATH'] = "/content/drive/MyDrive/aiweb/text-generation-webui/installer_files/conda"
os.environ['PYTHONHOME'] = ""
os.environ['CUDA_PATH'] = INSTALL_ENV_DIR
os.environ['CUDA_HOME'] = INSTALL_ENV_DIR

# Activate installer env
subprocess.run(f"{os.path.join(CONDA_ROOT_PREFIX, 'bin', 'conda')} init bash", shell=True, check=True)
subprocess.run(f"{os.path.join(CONDA_ROOT_PREFIX, 'etc', 'profile.d', 'conda.sh')} && conda activate {INSTALL_ENV_DIR}", shell=True, check=True)

# Run webui.py
os.chdir('/content/Yvtyvyf')
subprocess.run("python webui.py", shell=True, check=True)
