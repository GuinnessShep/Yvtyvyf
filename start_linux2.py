%%shell

script_dir=/content/drive/MyDrive/aiweb/text-generation-webui
conda_env_path=/content/drive/MyDrive/aiweb/text-generation-webui/installer_files/env
CMD_FLAGS="--chat"

if [[ -n $OOBABOOGA_FLAGS ]]; then
    CMD_FLAGS=$OOBABOOGA_FLAGS
    echo "The following flags have been taken from the environment variable 'OOBABOOGA_FLAGS':"
    echo $CMD_FLAGS
    echo "To use the CMD_FLAGS Inside webui.py, unset 'OOBABOOGA_FLAGS'."
fi

print_big_message() {
    message=$1
    message=$(echo "$message" | sed 's/^ *//g')
    lines=$(echo "$message" | awk -F "\n" '{print NF}')
    echo -e "\n\n*******************************************************************"
    while IFS= read -r line; do
        if [[ -n $line ]]; then
            echo "* $line"
        fi
    done <<< "$message"
    echo "*******************************************************************\n\n"
}

run_cmd() {
    cmd=$1
    assert_success=${2:-false}
    environment=${3:-false}
    capture_output=${4:-false}
    env=${5:-""}

    if [[ $environment == true ]]; then
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            conda_bat_path="$script_dir/installer_files/conda/condabin/conda.bat"
            cmd="\"$conda_bat_path\" activate \"$conda_env_path\" >nul && $cmd"
        else
            conda_sh_path="$script_dir/installer_files/conda/etc/profile.d/conda.sh"
            cmd=". \"$conda_sh_path\" && conda activate \"$conda_env_path\" && $cmd"
        fi
    fi

    result=""
    if [[ $capture_output == true ]]; then
        result=$(eval "$cmd" 2>&1)
    else
        eval "$cmd"
    fi

    if [[ $assert_success == true ]] && [[ $? -ne 0 ]]; then
        echo "Command '$cmd' failed with exit status code '$?'. Exiting..."
        exit 1
    fi

    echo "$result"
}

check_env() {
    conda_exist=$(run_cmd "conda" true true true)
    if [[ $? -ne 0 ]]; then
        echo "Conda is not installed. Exiting..."
        exit 1
    fi

    if [[ "$CONDA_DEFAULT_ENV" == "base" ]]; then
        echo "Create an environment for this project and activate it. Exiting..."
        exit 1
    fi
}

install_dependencies() {
    echo "What is your GPU"
    echo
    echo "A) NVIDIA"
    echo "B) AMD"
    echo "C) Apple M Series"
    echo "D) None (I want to run in CPU mode)"
    echo
    read -p "Input> " gpuchoice

    if [[ $gpuchoice == "D" || $gpuchoice == "d" ]]; then
        print_big_message "Once the installation ends, make sure to open webui.py with a text editor\nand add the --cpu flag to CMD_FLAGS."
    fi

    if [[ $gpuchoice == "A" || $gpuchoice == "a" ]]; then
        run_cmd 'conda install -y -k cuda ninja git -c nvidia/label/cuda-11.7.0 -c nvidia && python -m pip install torch==2.0.1+cu117 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117' true true
    elif [[ $gpuchoice == "B" || $gpuchoice == "b" ]]; then
        echo "AMD GPUs are not supported. Exiting..."
        exit 1
    elif [[ $gpuchoice == "C" || $gpuchoice == "c" || $gpuchoice == "D" || $gpuchoice == "d" ]]; then
        run_cmd "conda install -y -k ninja git && python -m pip install torch torchvision torchaudio" true true
    else
        echo "Invalid choice. Exiting..."
        exit 1
    fi

    run_cmd "git clone https://github.com/oobabooga/text-generation-webui.git" true true

    update_dependencies
}

update_dependencies() {
    cd "text-generation-webui"
    run_cmd "git pull" true true

    with open("requirements.txt") as f; do
        requirements=$(cat "$f")
        git_requirements=()
        while IFS= read -r req; do
            if [[ $req == git+* ]]; then
                git_requirements+=("$req")
            fi
        done <<< "$requirements"
    done

    for req in "${git_requirements[@]}"; do
        url=$(echo "$req" | sed 's/git+//g')
        package_name=$(echo "$url" | awk -F "/" '{print $NF}' | awk -F "@" '{print $1}')
        run_cmd "python -m pip uninstall -y $package_name" false true
        echo "Uninstalled $package_name"
    done

    run_cmd "python -m pip install -r requirements.txt --upgrade" true true

    extensions=()
    while IFS= read -r -d ''; do
        extensions+=("$REPLY")
    done < <(find extensions -maxdepth 1 -type d -print0)

    for extension in "${extensions[@]}"; do
        if [[ $extension == 'extensions/superbooga' ]]; then
            continue
        fi

        extension_req_path="$extension/requirements.txt"
        if [[ -f $extension_req_path ]]; then
            run_cmd "python -m pip install -r $extension_req_path --upgrade" true true
        fi
    done

    if [[ $torver ]]; then
        if [[ $torver != *"+cu"* ]] && [[ ! $(run_cmd "conda list -f pytorch-cuda | grep pytorch-cuda" true true true) ]]; then
            return
        fi

        site_packages_path=""
        for sitedir in $(python -c "import site; print('\n'.join(site.getsitepackages()))"); do
            if [[ $sitedir == *"site-packages"* ]]; then
                site_packages_path=$sitedir
                break
            fi
        done

        if [[ -z $site_packages_path ]]; then
            echo "Could not find the path to your Python packages. Exiting..."
            exit 1
        fi

        if [[ $sys_platform == *"linux"* ]]; then
            run_cmd "cp $site_packages_path/bitsandbytes/libbitsandbytes_cuda117.so $site_packages_path/bitsandbytes/libbitsandbytes_cpu.so" false true
        fi

        if [[ ! -d "repositories" ]]; then
            mkdir "repositories"
        fi

        cd "repositories"

        if [[ ! -d "exllama" ]]; then
            run_cmd "git clone https://github.com/turboderp/exllama.git" true true
        else
            cd "exllama"
            run_cmd "git pull" true true
            cd ".."
        fi

        if [[ $sys_platform == *"linux"* ]] && [[ ! -d "$conda_env_path/lib64" ]]; then
            run_cmd "ln -s $conda_env_path/lib $conda_env_path/lib64" true true
        fi

        if [[ ! -d "GPTQ-for-LLaMa" ]]; then
            run_cmd "git clone https://github.com/oobabooga/GPTQ-for-LLaMa.git -b cuda" true true
        else
            cd "GPTQ-for-LLaMa"
            run_cmd "git pull" true true
            cd ".."
        fi

        if [[ $sys_platform == *"linux"* ]]; then
            gxx_output=$(run_cmd "g++ -dumpfullversion -dumpversion" true true true)
            if [[ $? -ne 0 ]] || (( $(echo "$gxx_output" | awk -F "." '{print $1}') > 11 )); then
                run_cmd "conda install -y -k gxx_linux-64=11.2.0" true true
            fi
        fi

        cd "GPTQ-for-LLaMa"
        if [[ -f "setup_cuda.py" ]]; then
            mv "setup_cuda.py" "setup.py"
        fi

        run_cmd "python -m pip install ." true true

        cd ".."

        quant_cuda_path_regex="$site_packages_path/quant_cuda*/"
        if [[ ! $(ls -d $quant_cuda_path_regex 2>/dev/null) ]]; then
            if [[ $sys_platform == *"win"* ]] || [[ $sys_platform == *"linux"* ]]; then
                echo "WARNING: GPTQ-for-LLaMa compilation failed, but this is FINE and can be ignored!"
                echo "The installer will proceed to install a pre-compiled wheel."
                url="https://github.com/jllllll/GPTQ-for-LLaMa-Wheels/raw/main/quant_cuda-0.0.0-cp310-cp310-win_amd64.whl"
                if [[ $sys_platform == *"linux"* ]]; then
                    url="https://github.com/jllllll/GPTQ-for-LLaMa-Wheels/raw/Linux-x64/quant_cuda-0.0.0-cp310-cp310-linux_x86_64.whl"
                fi

                result=$(run_cmd "python -m pip install $url" true true)
                if [[ $? -eq 0 ]]; then
                    echo "Wheel installation success!"
                else
                    echo "ERROR: GPTQ wheel installation failed. You will not be able to use GPTQ-based models."
                fi
            else
                echo "ERROR: GPTQ CUDA kernel compilation failed."
                echo "You will not be able to use GPTQ-based models."
            fi

            echo "Continuing with install.."
        fi
    fi
}

download_model() {
    cd "text-generation-webui"
    run_cmd "python download-model.py" true true
}

launch_webui() {
    cd "text-generation-webui"
    run_cmd "python server.py $CMD_FLAGS" true true
}

# Verifies we are in a conda environment
check_env

# Parse command-line arguments
update=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --update)
            update=true
            ;;
    esac
    shift
done

if [[ $update == true ]]; then
    update_dependencies
else
    if [[ ! -d "text-generation-webui" ]]; then
        install_dependencies
        cd $script_dir
    fi

    if [[ $(find text-generation-webui/models -type f ! -name "*.txt" ! -name "*.yaml" | wc -l) -eq 0 ]]; then
        print_big_message "WARNING: You haven't downloaded any model yet."
        print_big_message "Once the web UI launches, head over to the bottom of the \"Model\" tab and download one."
    fi

    conda_path_bin="$conda_env_path/bin"
    if [[ ! -d $conda_path_bin ]]; then
        mkdir $conda_path_bin
    fi

    launch_webui
fi
