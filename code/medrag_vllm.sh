#!/bin/bash
#SBATCH --job-name=medscore-medrag
#SBATCH --time=08:00:00
#SBATCH --nodes=1
#SBATCH --mem=300GB
#SBATCH --partition=bigmem
#SBATCH -A mdredze1_bigmem
#SBATCH --output=logs/%x.%j.log

module load anaconda
conda activate medic

python -m medscore.medscore --input_file "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/PUMA_gpt4o/decompositions.jsonl" --output_dir "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/PUMA_gpt4o" --verify_only --verification_mode "internal" --model_name_verification "gpt-4o"

# python -m medscore.medscore --input_file "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/PUMA_medrag/decompositions.jsonl" --output_dir "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/PUMA_medrag" --verify_only --verification_mode "medrag" --model_name_verification "mistralai/Mistral-Small-24B-Instruct-2501" --server_verification "http://<node ID>:22659/v1"