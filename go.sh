#!/bin/bash

# Set the base directory for text-generation-webui
BASE_DIR="/content/drive/MyDrive/aiweb/text-generation-webui"

# Update package lists for upgrades and new package installations
sudo apt-get update

# Install required dependencies
sudo apt-get install -y git curl wget unzip

# Install Miniconda
CONDA_INSTALL_DIR="${BASE_DIR}/miniconda"
if [ ! -d "${CONDA_INSTALL_DIR}" ]; then
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b -p "${CONDA_INSTALL_DIR}"
    rm miniconda.sh
fi

# Activate Miniconda
source "${CONDA_INSTALL_DIR}/etc/profile.d/conda.sh"

# Create and activate a new Conda environment named 'textgen'
conda create -n textgen python=3.8 -y
conda activate textgen

# Install Python dependencies
pip install gradio transformers

# Navigate to text-generation-webui directory
cd "${BASE_DIR}"

# Install AutoGPTQ for GPTQ models (already included in requirements.txt)
# pip install git+https://github.com/PanQiWei/AutoGPTQ.git (Uncomment if needed)

# Setup for llama.cpp support (Assuming you want to compile it inside text-generation-webui directory)
git clone https://github.com/eleutherai/llama_cpp.git
cd llama_cpp
mkdir build
cd build
cmake ..
make
cd ../..

# Run the text-generation-webui server
python server.py

# Note: You may need to include the `--autogptq` flag if you are using GPTQ models.
# Example: python server.py --autogptq --model model_name
