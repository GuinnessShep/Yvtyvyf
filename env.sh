#!/bin/bash

# Directories to be added
dir1="/content/selfrun/installer_files/conda/bin"
dir2="/content/selfrun/installer_files/env/bin"

# Add directories to PATH in .bashrc if they are not already in PATH
for dir in "$dir1" "$dir2"; do
    if [[ ":$PATH:" != *":$dir:"* ]]; then
        echo "export PATH=\$PATH:$dir" >> ~/.bashrc
    fi
done

# Source .bashrc to update current shell
source ~/.bashrc
