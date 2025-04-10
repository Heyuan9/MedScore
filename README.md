# MedScore

Supporting code and data for MedScore, a medical chatbot factuality detection system.
See [the paper]() for details.

If you use this tool, please cite

```
@article{
    title={"MedScore:"},
    author={},
    journal={arXiv preprint arXiv: },
    year={2025}
}
```

## Installation and Setup

1. Make a new Python 3.10+ environment with `conda` with the `environment.yml` file.

    ```bash
    conda env create --file=environment.yml
    conda activate medscore
    python -m spacy download en_core_web_sm
    ```

2. Add any API keys to your `~/.bashrc`

    ```bash
   export OPENAI_API_KEY=""
    ```

## Running MedScore

MedScore can be run from the command line. The options are explained below.

```bash
python
```

- `input_file`: Path to the input data file. It should be in `jsonl` format.
  - `id`: A unique identifier for the instance.
  - `repsonse`: The text response from the medical chatbot.
  - Any other metadata.
- `output_dir`: Path to the output directory. The default is the current directory. The name of the output file is `medscore_{input_file}`.
- `model_name_decomposition`: The name of the model for decomposing the response into claims. It should the model identifier for a hosted HuggingFace model, OpenAI model, TogetherAI model, or locally-hosted vLLM model.
- `model_name_verification`: The name of the model for decomposing the response into claims. It should the model identifier for a hosted HuggingFace model, OpenAI model, TogetherAI model, or locally-hosted vLLM model.
- `verification_mode`: One of the following:
  - `medrag`: Verify the `response` against MedCorp from [Benchmarking Retrieval-Augmented Generation for Medicine (Xiong et al., Findings 2024)](https://aclanthology.org/2024.findings-acl.372/). The default settings retrieve the top 5 passages from PubMed, StatPearls, and academic textbooks with the `MedCPT` encoder.
  - `internal`: Verify against the internal knowledge of an LLM. 
- `server_decomposition`: The server path for the decomposition model. E.g., for OpenAI models the server is `https://api.openai.com`.
- `server_verification`: The server path for the verification model. E.g., for OpenAI models the server is `https://api.openai.com`.

Example settings for decomposing and verifying with `GPT4o`:

```bash
--model_name_decomposition gpt-4o \
--model_name_verification gpt-4o \
--verification_mode internal \
--server_decomposition "https://api.openai.com" \
--server_verification "https://api.openai.com" \
```

Example settings for decomposing with GPT4o and verifying with MedRag against a locally-hosted Mistral Small 3 model:
```bash
--model_name_decomposition gpt-4o \
--model_name_verification "mistralai/Mistral-Small-24B-Instruct-2501" \
--verification_mode medrag \
--server_decomposition "https://api.openai.com" \
--server_verification "http://localhost:8000" \
```

The output file is in `jsonl` format where each entry looks like this:
```json
{
  "id": ,
  "response": ,
  "claims": ,
  "score": 
}
```

## Data


