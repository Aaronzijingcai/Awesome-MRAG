#!/bin/bash

# Activate conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate ai

# Start VLLM API server in the background
nohup python -m vllm.entrypoints.openai.api_server \
  --model /NAS/caizj/models/deepseek/DeepSeek-R1-Distill-Qwen-1.5B/ \
  --host 0.0.0.0 --port 8888 > vllm_deepseek.log 2>&1 &

echo "DeepSeek VLLM service started with PID: $!"
echo "Log file: vllm_deepseek.log"