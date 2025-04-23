#!/bin/bash
#SBATCH --job-name=medscore-internal
#SBATCH --time=15:00:00
#SBATCH --nodes=1
#SBATCH --mem=300GB
#SBATCH --partition=bigmem
#SBATCH -A mdredze1_bigmem
#SBATCH --output=logs/%x.%j.log

module load anaconda
conda activate medic

cd /home/hhuan134/scr4_mdredze1/hhuan134/MedScore
### GPT-4o internal
# python -m medscore.medscore --input_file "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/PUMA_gpt4o/decompositions.jsonl" --output_dir "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/PUMA_gpt4o" --verify_only --verification_mode "internal" --model_name_verification "gpt-4o"
export HF_TOKEN="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"
## BioLLM70B internal
python -m medscore.medscore --input_file "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/AskDocs_VeriScore_OpenBioLLM_internal/decompositions.jsonl" --output_dir "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/AskDocs_VeriScore_OpenBioLLM_internal" --verify_only --verification_mode "internal" --model_name_verification "aaditya/Llama3-OpenBioLLM-70B" --server_verification "https://router.huggingface.co/nebius/v1"
# python -m medscore.medscore --input_file "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/AskDocs_VeriScore_OpenBioLLM/decompositions.jsonl" --output_dir "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/AskDocs_VeriScore_OpenBioLLM" --verify_only --verification_mode "internal" --model_name_verification "aaditya/Llama3-OpenBioLLM-70B" --server_verification "http://icgpu02:22659/v1"


### MedRAG
# export MEDRAG_CORPUS="/home/hhuan134/scr4_mdredze1/medic_project/data/MedCorp"

# python -m medscore.medscore --input_file "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/VeriScore_QA/PUMA_medrag/decompositions.jsonl" --output_dir "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/VeriScore_QA/PUMA_medrag" --verify_only --verification_mode "medrag" --model_name_verification "mistralai/Mistral-Small-24B-Instruct-2501" --server_verification "http://icgpu05:22659/v1"

### MedAlpaca-7B
# python -m medscore.medscore --input_file "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/VeriScore_QA/PUMA_medalpaca/decompositions.jsonl" --output_dir "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/VeriScore_QA/PUMA_medalpaca" --verify_only --verification_mode "internal" --model_name_verification "medalpaca/medalpaca-7b" --server_verification "http://icgpu02:22659/v1"
# python -m medscore.medscore --input_file "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/VeriScore_nonQA/AskDocs_MedAlpaca/decompositions.jsonl" --output_dir "/home/hhuan134/scr4_mdredze1/hhuan134/MedScore/result/VeriScore_nonQA/AskDocs_MedAlpaca" --verify_only --verification_mode "internal" --model_name_verification "medalpaca/medalpaca-7b" --server_verification "http://icgpu02:22659/v1"
