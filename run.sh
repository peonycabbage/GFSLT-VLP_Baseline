#!/bin/bash

# USAGE:
# apt install gcc g++
# pip install -U openmim
# mim install mmcv
# sh -i ./demo/run.sh

# Exit on error
set -e
echo "-> Starting"

# Set up environment variables
CONDA_ENV="gfslt"
OUTPUT_DIR="results"
PATH=~/.conda/envs/$CONDA_ENV/bin:$PATH

# Set up conda executable
# alias conda_exe="/c/ProgramData/miniconda3/Scripts/conda.exe"
alias conda_exe="conda"
conda_run() {
	conda_exe run -n "${CONDA_ENV}" "$@"
}

# Set up conda env if necessary
(conda_exe info --env | grep "${CONDA_ENV} " && echo "${CONDA_ENV} environment found") || (
	echo "${CONDA_ENV} environment not found. Initializing..." && conda_exe create -n $CONDA_ENV python=3.8 -y)

# # Activate environment
# echo "-> Activating conda environment..." && conda_exe init bash && source ~/.bashrc
# conda_exe activate "${CONDA_ENV}" && source activate "${CONDA_ENV}"

# Install torch if necessary: https://pytorch.org/get-started/previous-versions/
(conda_run python -m pip freeze | grep torchvision && echo "torch already installed") || (
	echo "Installing torch..." && conda_exe install -n $CONDA_ENV pytorch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0 cudatoolkit=11.3 -c pytorch -y)

# Install requirementspip install -U openmim
echo "-> Checking requirements..."
conda_run python -m pip install -r requirements.txt

# Run the pretraining script
echo "-> Running the pretraining script..."
# conda_run python -m torch.distributed.launch --use_env train_vlp.py --batch-size 4 --epochs 80 --opt sgd --lr 0.01 --output_dir "${OUTPUT_DIR}/vlp"
CUDA_VISIBLE_DEVICES=0 python -m torch.distributed.launch --nproc_per_node=1 --master_port=1236 --use_env train_vlp_v2.py --batch-size 4 --epochs 80 --opt sgd --lr 0.01 --output_dir "${OUTPUT_DIR}/vlp_v2" --training-refurbish True --noise-rate 0.15 --noise-type omit_last --random-shuffle False

# Done
echo "-> Script execution completed successfully."
