import os
import subprocess

# Adjust the working directory
os.chdir('/content/drive/MyDrive/aiweb/text-generation-webui')

# Config
CONDA_ROOT_PREFIX = os.path.join(os.getcwd(), 'installer_files', 'conda')
INSTALL_ENV_DIR = os.path.join(os.getcwd(), 'installer_files', 'env')

# Environment isolation
os.environ['PYTHONNOUSERSITE'] = "1"
os.environ['PYTHONPATH'] = ""
os.environ['PYTHONHOME'] = ""
os.environ['CUDA_PATH'] = INSTALL_ENV_DIR
os.environ['CUDA_HOME'] = INSTALL_ENV_DIR

# Activate installer env
subprocess.run(f'bash --init-file <(echo "source {os.path.join(CONDA_ROOT_PREFIX, "etc", "profile.d", "conda.sh")} && conda activate {INSTALL_ENV_DIR}")', shell=True)
