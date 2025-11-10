# MedScore

**Note: This is the code for the updated MedScore paper, 2025 October version. Check out the `arxiv-reproducibility` branch for the exact code used in the paper of 2025 May arxiv version.**

Supporting code and data for MedScore, a medical chatbot factuality evaluation system that can adapt to other domains easily.
See [the MedScore paper](https://arxiv.org/abs/2505.18452) for details. Following the structure of the paper (update MedScore taxonomy based on domain-specific requirements for valid claim definition, then change the MedScore Instructions and domain-specific In Context Learning examples), researchers can adapt this tool to their text domain optimally with minimal effort.

If you use this tool, please cite

```
@misc{huang2025medscoregeneralizablefactualityevaluation,
      title={MedScore: Generalizable Factuality Evaluation of Free-Form Medical Answers by Domain-adapted Claim Decomposition and Verification}, 
      author={Heyuan Huang and Alexandra DeLucia and Vijay Murari Tiyyala and Mark Dredze},
      year={2025},
      eprint={2505.18452},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2505.18452}, 
}
```

## Installation and Setup

There are two options for installation. For editing the code, we recommend the `development install` option. 
For running the code as-is, we recommend the `standard install` option.

### Standard install

Pip install from the repository.:

```bash
pip install git+https://github.com/Heyuan9/MedScore.git
```

### Development install

This option allows you to edit the code and have changes reflected without re-installing.

1. Clone the repository

    ```bash
    git clone git@github.com:Heyuan9/MedScore.git
    ```

2. Create a new environment

    ```bash
    conda env create --file=environment.yml
    conda activate medscore
    ```


3. Install the MedScore package for easy command-line usage

      ```bash
      cd /path/to/MedScore
      pip install .
      ```

4. Add any API keys to your `~/.bashrc` or to a `.env` file in the root directory.

    ```bash
   export OPENAI_API_KEY=""
   export TOGETHER_API_KEY=""
    ```

5. [Optional] Set `MEDRAG_CORPUS` environment variable or add it to a `.env` file in the root directory.

    ```bash
   export MEDRAG_CORPUS=""
    ```

Setting this variable makes sure that the MedRAG corpus will only be downloaded once.


## Running MedScore

MedScore v0.1.1 is now run from the command line using a single configuration file, which makes managing experiments much easier.

```bash
python -m medscore.medscore --config /path/to/your/config.yaml
```

All options:

- `--config`: Path to the YAML configuration file. The config file is explained below.
- `--input_file`: JSONLines-formatted input file. Override the input data file specified in the config.
- `--output_dir`: Path to save the intermediate and result files. Override the output directory specified in the config.
- `--decompose_only`: Only run the decomposition step. Saves to `output_dir/decompositions.jsonl`.
- `--verify_only`: Only run the verification step (requires an existing decomposition file in the `output_dir`) Saves to `output_dir/verifications.jsonl`.

The final output is saved to `output_dir/output.jsonl`.

All settings are defined within the YAML configuration file. You can create different config files for different experiments.

### The Configuration File (config.yaml)
Below are explanations for all the options in a MedScore config file. There are examples in `demo/` and a few are below.

#### Config.yaml setup

There are three main sections of a MedScore config file.

**1. Main input/output**
   - `input_file`: Path to the input data file. It should be in `jsonl` format.
       - `id`: A unique identifier for the instance.
       - `repsonse`: The text response from the medical chatbot. This key can be changed with `--response_key`.
       - Any other metadata.
   - `output_dir`: Path to the output directory. The output files are `decompositions.jsonl`, `verifications.jsonl`, and `medscore_output.jsonl`.
     - Default: current directory
   - `response_key`: JSON key corresponding to the medical chatbot response. The default is `response`.


**2. Decomposition-related arguments**
  - `type`: Method for decomposing the sentences into claims.
    - Options:
      - `factscore`: FActScore prompt from [FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation (Min et al., EMNLP 2023)](https://aclanthology.org/2023.emnlp-main.741/)
      - `medscore`: Our work.
      - `dndscore`: Prompt from [DnDScore: Decontextualization and Decomposition for Factuality Verification in Long-Form Text Generation (Wanner et al., arXiv 2024)](https://arxiv.org/abs/2412.13175)
      - `custom`: A custom user-written prompt with instructions and in-domain examples best for your dataset. The `decomp_prompt_path` must also be provided. We recommend following the format of MedScore_prompt.txt to make the first customization try easier.
    - Default: `MedScore`
  - `prompt_path`: Path to a `txt` file containing a system prompt for decomposition. See the prompts in `medscore/prompts.py` for examples. **This should only be set if you are using a custom decomposer**.
  - `model_name`: The name of the model for decomposing the response into claims. It should the model identifier for a hosted HuggingFace model, OpenAI model, TogetherAI model, or locally-hosted vLLM model.
    - Default: `gpt-4o-mini`
  - `server_path`: The server path for the decomposition model. 
    - Default: `https://api.openai.com/v1`
  - `api_key`: API key for the specified `server_path`. You can use environment variables by prefacing them with `!env`. Example: `!env TOGETHER_API_KEY`


**3. Verification-related arguments**
  - `type`: The method for verification.
    - Options:
      - `medrag`: Verify the `response` against MedCorp from [Benchmarking Retrieval-Augmented Generation for Medicine (Xiong et al., Findings 2024)](https://aclanthology.org/2024.findings-acl.372/). The default settings retrieve the top 5 passages from PubMed, StatPearls, and academic textbooks with the `MedCPT` encoder.
      - `internal`: Verify against the internal knowledge of an LLM. 
      - `provided`: Verify against pre-collected user-provided evidence. Requires `provided_evidence_path` to be set.
    - Default: `internal`
  - `response_key`: JSON key corresponding to the medical chatbot response. The default is `response`.
  - `prompt_path`: Path to a `txt` file containing a system prompt for decomposition. See the prompts in `medscore/prompts.py` for examples. **This should only be set if you are using a custom decomposer**.
  - `model_name`: The name of the model for verifying the response. It should be a model identifier for a hosted HuggingFace model, OpenAI model, TogetherAI model, or a locally-hosted vLLM model.
    - Default: `gpt-4o` The paper use `mistralai/Mistral-Small-24B-Instruct-2501`
  - `server_path`: The server path for the verification model. Refer to the [vLLM](https://huggingface.co/mistralai/Mistral-Small-24B-Instruct-2501) Hugging Face tutorial for open-sourced LLM server path: `http://<your-server>:8000/v1`
    - Default: `https://api.openai.com/v1`
  - `api_key`: API key for the specified `server_path`. You can use environment variables by prefacing them with `!env`. Example: `!env TOGETHER_API_KEY`
  - `provided_evidence_path`: Path to `json` file in `{"{id}": "{evidence}"}` format, where the `id` is the same as the entry id in `input_file`.


All of the decomposition and verification arguments are built from the classes in `medscore.decomposer` and `medscore.verifier`, respectively.


#### Config.yaml Examples in the demo folder

**1. MedScore Decomposer with Internal Verification**

```yaml
#################
# MedScore Configuration File
#################

# --- Main Input/Output Files ---
# These paths are relative to where you run the script.
input_file: "data/AskDocs.demo.jsonl"
output_dir: "results"
response_key: "response" # The 'response' is used as the answer_context for decomposition. However, if 'response' doesn't contain enough information and your dataset has 'question', you can input 'question' and change format_input("question_context","answer_context",) function of the MedScore class to incorporate two keys in the prompt as "Question_Context:{}\nAnswer_Context:{}\n".

# --- Decomposition Configuration ---
decomposer:
  type: "medscore"
  model_name: "gpt-4o-mini"
  server_path: "https://api.openai.com/v1"
  # api_key: "YOUR_API_KEY" # Optional: can be set here or via environment variable.

# --- Verification Configuration ---
verifier:
  type: "internal"
  model_name: "gpt-4o"
  server_path: "https://api.openai.com/v1"
```


**2. MedScore Decomposer with MedRAG Verification and locally-hosted model**

```yaml
#################
# MedScore Configuration File
#################

# --- Main Input/Output Files ---
# These paths are relative to where you run the script.
input_file: "data/AskDocs.demo.jsonl"
output_dir: "results"
response_key: "response"

# --- Decomposition Configuration ---
decomposer:
  type: "medscore"
  model_name: "gpt-4o-mini"
  server_path: "https://api.openai.com/v1"
  # api_key: "YOUR_API_KEY" # Optional: can be set here or via environment variable.

# --- Verification Configuration ---
verifier:
  type: "medrag"
  model_name: "mistralai/Mistral-Small-24B-Instruct-2501"
  server_path: "http://localhost:8000/v1"
  corpus_name: "Textbooks"  # options: "PubMed", "Textbooks", "StatPearls", "Wikipedia", "MedCorp", "MEDIC". Our paper uses MEDIC.
  n_returned_docs: 5
  cache: false  # Set to true for large datasets to improve performance
  db_dir: "."
```

### Program output

For flexibility, the `medscore.py` script saves intermediate output of the decompositions, verification, and the final combined file.

**Decompositions**

The output from the decomposition step is `decompositions.jsonl` and has the following format:

```json
{
  "id": {},
  "sentence": {},
  "sentence_id": {},
  "claim": {},
  "claim_id": {}
}
```

There is one entry for every claim for every sentence. The `claim` key can be `None` if a sentence has no claims.

**Verifications**

The output from the verification step is `verificcations.jsonl` and has the following format:

```json
{
  "id": {},
  "sentence": {},
  "sentence_id": {},
  "claim": {},
  "claim_id": {},
  "evidence": [{
    "id": {},
    "title": {},
    "text": {},
    "score": {}
  }],
  "raw": {},
  "score": {}
}
```

There is one entry for every claim. Claims that were `None` from the decomposition step are filtered before being passed to the verifier. 
The `evidence` key can change based on the verification setting. 

- `medrag`
    ```json
      "evidence": [{
        "id": {},
        "title": {},
        "text": {},
        "score": {}
      }]
    ```

where the `id`, `title`, and `text` correspond to the retrieved entries in MedRAG. `score` is the similarity score based on the retriever.

- `internal`
    ```json
      "evidence": None
    ```

In the `internal` setting, the model is not prompted with evidence.

- `provided`

    ```json
      "evidence": "{evidence from provided_evidence_path}"
    ```


**Combined output**

The final output file combines the decompositions and verifications by `id`.

```json
{
  "id": {},
  "score": {},
  "claims": [{
      "claim": {},
      "sentence": {},
      "evidence": {},
      "raw": {},
      "score": {}
    }]
}
```

where `score` is the average claim score for the `id`.

### MedRAG Verifier

The MedRAG verifier is memory-intensive due to the large size of the dataset. The data subset can be customized by overriding or editing
the `verifier.MedRAGVerifier` class. **The dataset downloads to `MEDRAG_CORPUS` (if set) or `./corpus`.**

Dataset size estimates:
- `PubMed`: 238GB
- `StatPearls`: 6.2GB
- `textbooks`: 1.2GB
- `Wikipedia`: 310GB

Running verification with the full MedCorp dataset (with `MedRAGVerifier.cache=True`) requires roughly 300GB of RAM. The entire dataset takes up 646GB of disk.

For speed, **we highly recommend setting `MedRAGVerifier.cache=True` for input files with a large number of claims (5K+).**

## Data

The AskDocs dataset is in the `./data` folder. It has 300 samples and 4 keys:
-  `id`: question id
-  `question`: user question
-  `doctor_response`: a doctor response from a verified doctor for this question
-  `response`: the Llama3.1 chatbot response for this question, augmented from the doctor_response by explaining medical terminologies in detail and adding more empathetic sentences, without adding other diagnosis/treatment information.

The AskDocs.demo dataset has 20 random samples from the AskDocs dataset. It is more cost-efficient to experiment on this small-scale dataset.

### Presenticized (pre-senticized) inputs

If your input data already contains sentence-level annotations (for example, produced by an external senticizer), MedScore can use those directly instead of running its internal sentence splitter. To enable this, add the top-level flag `presenticized: true` to your YAML config.

Behavior when presenticized is true:
- MedScore will look for a `sentences` list in each input record and use those entries as the source of sentences.
- Each item in `sentences` is a dict with a `text` field and an optional `sentence_id` field. If `sentence_id` is not provided, it will be auto-generated based on the list index.
- If the original `response` (or configured `response_key`) is present, it will be used as the `context` passed to the decomposer; otherwise the context will be reconstructed by joining the provided sentence texts.
- Records missing a valid `sentences` list will be skipped with a warning.

Example YAML config enabling presenticized inputs:

```yaml
input_file: "data/AskDocs.demo.jsonl"
output_dir: "results"
response_key: "response"
presenticized: true

decomposer:
  type: "medscore"
  model_name: "gpt-4o-mini"

verifier:
  type: "internal"
```

Example input JSONL record (per-line):

```json
{"id":"123","response":"optional original text","sentences":[{"text":"Sentence 1.","sentence_id": 0, "span_start":0,"span_end":10},{"text":"Sentence 2.", "sentence_id": 1, "span_start":11,"span_end":25}]}
```

MedScore will then skip internal sentence splitting and use the provided sentences for decomposition and verification.
