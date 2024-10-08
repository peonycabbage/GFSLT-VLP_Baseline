#!/bin/bash

# Installation:
# apt install gcc g++
# pip install -U openmim
# mim install mmcv

# Training:
# VLP=vlp_v2 sh -i run.sh
# OR:
# VLP=vlp    sh -i run.sh

################################################################################
DELIMITER="\n============================================\n-> "
echo "-> Starting"

# Exit on error
set -e

# Set up environment variables
CONDA_ENV="${CONDA_ENV:-gfslt}"
OUTPUT_DIR="${OUTPUT_DIR:-out}"
PATH=~/.conda/envs/$CONDA_ENV/bin:$PATH
VLP="${VLP:-vlp_v2}"
echo "${DELIMITER}Using conda env: ${CONDA_ENV}"
echo "${DELIMITER}Using output dir: ${OUTPUT_DIR}"
echo "${DELIMITER}Using VLP: ${VLP}"

################################################################################
# Conda setup
conda_run() {
	conda run -n "${CONDA_ENV}" "$@"
}

# Set up conda env if necessary
echo "${DELIMITER}Checking conda"
(conda info --env | grep "${CONDA_ENV} " && echo "${DELIMITER}${CONDA_ENV} environment found") || (
	echo "${DELIMITER}{CONDA_ENV} environment not found. Initializing..." && conda create -n $CONDA_ENV python=3.8 -y)

# # Install torch if necessary: https://pytorch.org/get-started/previous-versions/
echo "${DELIMITER}Checking torch..."
(conda_run python -m pip freeze | grep torchvision && echo "-> torch already installed") || (
	echo "${DELIMITER}Installing torch..." && conda install -n $CONDA_ENV pytorch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0 cudatoolkit=11.3 -c pytorch -y)

# # Install requirements
echo "${DELIMITER}Checking requirements..."
conda_run python -m pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu113/

################################################################################
# Training scripts

export CUDA_VISIBLE_DEVICES=0
export MPORT=1236
export NPROC=1
export PRETRAIN_BATCH_SIZE=4
export PRETRAIN_EPOCHS=80
export TRAIN_BATCH_SIZE=2
export TRAIN_EPOCHS=200

torch_run() {
	conda run -n "${CONDA_ENV}" python -u -m torch.distributed.launch --nproc_per_node=$NPROC --master_port=$MPORT "$@"
}

SEP=" ->"
echo "PARAMETERS:"
echo "------------------------------------------------"
echo "${SEP} OUTPUT_DIR:      ${OUTPUT_DIR}"
echo "------------------------------------------------"
echo "${SEP} master_port:     ${MPORT}"
echo "${SEP} nproc_per_node:  ${NPROC}"
echo "${SEP} pretrain batch:  ${PRETRAIN_BATCH_SIZE}"
echo "${SEP} pretrain epochs: ${PRETRAIN_EPOCHS}"
echo "${SEP} train batch:     ${TRAIN_BATCH_SIZE}"
echo "${SEP} train epochs:    ${TRAIN_EPOCHS}"
echo "${SEP} VLP:             ${VLP}"
echo "------------------------------------------------"


echo "${DELIMITER}Running signerindependent script..."
conda_run python create_signerindependent_labels.py

# Run VLP pretraining
echo "${DELIMITER}Running the VLP pretraining script..."
echo "${DELIMITER}Using file: train_${VLP}.py"
if [ "$VLP" = "vlp" ]; then  # VLP
	torch_run --use_env "train_${VLP}.py" --batch-size $PRETRAIN_BATCH_SIZE --epochs $PRETRAIN_EPOCHS --opt sgd --lr 0.01 --output_dir "${OUTPUT_DIR}/${VLP}"
elif [ "$VLP" = "vlp_v2" ]; then  # VLP v2
	torch_run --use_env "train_${VLP}.py" --batch-size $PRETRAIN_BATCH_SIZE --epochs $PRETRAIN_EPOCHS --opt sgd --lr 0.01 --output_dir "${OUTPUT_DIR}/${VLP}" --training-refurbish True --noise-rate 0.15 --noise-type omit_last --random-shuffle False
else  # Error
	echo "Error. Unknown VLP: '${VLP}'. Exiting..."
	exit
fi

# Run VLP GFSLT-VLP training
echo "${DELIMITER}Running the GFSLT-VLP training script..."
torch_run --use_env train_slt.py --batch-size $TRAIN_BATCH_SIZE --epochs $TRAIN_EPOCHS --opt sgd --lr 0.01 --output_dir "${OUTPUT_DIR}/${VLP}/Gloss-Free" --finetune "${OUTPUT_DIR}/${VLP}/checkpoint.pth"

# Run evaluation
echo "${DELIMITER}Running the evaluation script..."
torch_run --use_env train_slt.py --batch-size $TRAIN_BATCH_SIZE --epochs $TRAIN_EPOCHS --opt sgd --lr 0.01 --output_dir "${OUTPUT_DIR}/${VLP}/Gloss-Free" --resume "${OUTPUT_DIR}/${VLP}/Gloss-Free/best_checkpoint.pth" --eval

# Done
echo "${DELIMITER}Script execution completed successfully."
################################################################################
