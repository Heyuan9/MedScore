#!/bin/bash
### Put your bash setting script here if needed

module load anaconda
### Create MedScore environment and activate it before running the main code.
conda activate medscore

cd ./MedScore
### GPT-4o internal knowledge test command line
python -m medscore.medscore --input_file "Your folder to /decompositions.jsonl" --output_dir "The output folder path" --verify_only --verification_mode "internal" --model_name_verification "gpt-4o"
