# MedScore


Supporting code and data for MedScore at ACL 2026, a medical chatbot factuality evaluation system that can adapt to other domains easily.
See [the MedScore paper](https://aclanthology.org/2026.findings-acl.693/) for details. Following the structure of the paper (update MedScore taxonomy based on domain-specific requirements for valid claim definition, then change the MedScore Instructions and domain-specific In Context Learning examples), researchers can adapt this tool to their text domain optimally with minimal effort.

If you use this tool, please cite

```
@inproceedings{huang-etal-2026-medscore,
    title = "{M}ed{S}core: Generalizable Factuality Evaluation of Open-ended Long-form Medical Answers by Domain-adapted Claim Decomposition and Verification",
    author = "Huang, Heyuan  and
      DeLucia, Alexandra  and
      Tiyyala, Vijay Murari  and
      Dredze, Mark",
    editor = "Liakata, Maria  and
      Moreira, Viviane P.  and
      Zhang, Jiajun  and
      Jurgens, David",
    booktitle = "Findings of the {A}ssociation for {C}omputational {L}inguistics: {ACL} 2026",
    month = jul,
    year = "2026",
    address = "San Diego, California, United States",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2026.findings-acl.693/",
    pages = "14149--14180",
    ISBN = "979-8-89176-395-1",
    abstract = "While Large Language Models (LLMs) can generate fluent and convincing responses, they are not necessarily correct. This is especially apparent in the popular decompose-then-verify factuality evaluation pipeline, where LLMs evaluate generated text by decomposing it into individual, valid claims. Factuality evaluation is especially important for medical answers, since incorrect medical information could seriously harm the patient. However, existing factuality systems are a poor match for the medical domain, as they are typically only evaluated on objective, entity-centric, formulaic texts such as biographies and historical topics. This differs from condition-dependent, conversational, hypothetical, sentence-structure diverse, and subjective medical answers, making decomposition into valid facts challenging. We propose MedScore, a new pipeline to decompose medical answers into condition-aware valid facts and verify against in-domain corpora. Our method extracts up to three times as many valid facts as existing methods, reducing hallucination and vague references, and retaining condition-dependency in facts. We also find MedScore is generalizable to non-medical domains without any specific tuning. The resulting factuality score substantially varies by decomposition method, verification corpus, and used backbone LLM, highlighting the importance of customizing each step for reliable factuality evaluation by using our generalizable and modularized pipeline for domain adaptation."
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

MedScore v0.1.2 is now run from the command line using a single configuration file, which makes managing experiments much easier.

> **Upgrading from v0.1.1:** decomposition now requires you to choose `qa_mode`. Add `qa_mode: false`
> to your existing config files to keep the previous behavior, or pass `--qa_mode false`. See
> [QA mode](#qa-mode---qa_mode).

```bash
python -m medscore.medscore --config /path/to/your/config.yaml
```

All options:

- `--config`: Path to the YAML configuration file. The config file is explained below.
- `--input_file`: JSONLines-formatted input file. Override the input data file specified in the config.
- `--output_dir`: Path to save the intermediate and result files. Override the output directory specified in the config.
- `--decompose_only`: Only run the decomposition step. Saves to `output_dir/decompositions.jsonl`.
- `--verify_only`: Only run the verification step (requires an existing decomposition file in the `output_dir`) Saves to `output_dir/verifications.jsonl`.
- `--qa_mode`: `true` or `false`. Whether to put the question in the decomposition context. **Required whenever the decomposition step runs with the `medscore` or `custom` decomposer**, unless `qa_mode` is set in the config file. Ignored with `--verify_only`, and not supported by `factscore` or `dndscore`. See [QA mode](#qa-mode---qa_mode).
- `--debug`: Print debug logs.

The final output is saved to `output_dir/output.jsonl`.

All settings are defined within the YAML configuration file. You can create different config files for different experiments.

### The Configuration File (config.yaml)
Below are explanations for all the options in a MedScore config file. There are examples in `demo/` and a few are below.

#### Config.yaml setup

There are three main sections of a MedScore config file.

**1. Main input/output**
   - `input_file`: Path to the input data file. It should be in `jsonl` format.
       - `id`: A unique identifier for the instance.
       - `response`: The text response from the medical chatbot. This key can be changed with `response_key`.
       - `question`: The user question the response answers. Only read when `qa_mode` is `true`; the key can be changed with `question_key`.
       - Any other metadata.
   - `output_dir`: Path to the output directory. The output files are `decompositions.jsonl`, `verifications.jsonl`, and `output.jsonl`.
     - Default: current directory
   - `response_key`: JSON key corresponding to the medical chatbot response. The default is `response`.
   - `question_key`: JSON key corresponding to the user question. The default is `question`. Only read when `qa_mode` is `true`.
   - `qa_mode`: Whether to put the question in the decomposition context. This is the only decomposition setting that also has a command-line flag, `--qa_mode`, which overrides the config value. See [QA mode](#qa-mode---qa_mode).

   All of the keys in this section go at the **top level** of the YAML file, next to `input_file`. Nesting `response_key`, `question_key` or `qa_mode` under `decomposer:` has no effect (MedScore warns if you do).


**2. Decomposition-related arguments**
  - `type`: Method for decomposing the sentences into claims.
    - Options:
      - `factscore`: FActScore prompt from [FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation (Min et al., EMNLP 2023)](https://aclanthology.org/2023.emnlp-main.741/)
      - `medscore`: Our work.
      - `dndscore`: Prompt from [DnDScore: Decontextualization and Decomposition for Factuality Verification in Long-Form Text Generation (Wanner et al., arXiv 2024)](https://arxiv.org/abs/2412.13175)
      - `custom`: A custom user-written prompt with instructions and in-domain examples best for your dataset. The `prompt_path` must also be provided. We recommend following the format of `prompt/Custom_prompt.txt` to make the first customization try easier.
    - Default: `MedScore`
  - `prompt_path`: Path to a `txt` file containing a system prompt for decomposition. See the prompts in `medscore/prompts.py` for examples. **This should only be set if you are using a custom decomposer**.
  - `model_name`: The name of the model for decomposing the response into claims. It should the model identifier for a hosted HuggingFace model, OpenAI model, TogetherAI model, or locally-hosted vLLM model.
    - Default: `gpt-4o-mini` for paper reproducibility only. We recommend using the latest released LLMs, such as gpt-5.5 or gpt-5.4, for the best performance.
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
  - `model_name`: The name of the model for verifying the response. It should be a model identifier for a hosted HuggingFace model, OpenAI model, TogetherAI model, or a locally-hosted vLLM model.
    - Default: `gpt-4o` The paper used `mistralai/Mistral-Small-24B-Instruct-2501` (released in 2025-01), but we recommend using the latest released LLMs for the best performance.
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
response_key: "response"  # The 'response' is used as the context for decomposition.
question_key: "question"  # JSON key holding the user question (only read when qa_mode is true).
qa_mode: false            # Set to true if the response only makes sense against the question. See "QA mode".

# --- Decomposition Configuration ---
decomposer:
  type: "medscore"
  model_name: "gpt-4o-mini"  # Change to gpt-5.4 or gpt-5.5 for better performance
  server_path: "https://api.openai.com/v1"
  # api_key: "YOUR_API_KEY" # Optional: can be set here or via environment variable.

# --- Verification Configuration ---
verifier:
  type: "internal"
  model_name: "gpt-4o"  # Change to the latest released LLMs for better performance
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
question_key: "question"
qa_mode: false

# --- Decomposition Configuration ---
decomposer:
  type: "medscore"
  model_name: "gpt-4o-mini"  # Change to gpt-5.4 or gpt-5.5 for better performance
  server_path: "https://api.openai.com/v1"
  # api_key: "YOUR_API_KEY" # Optional: can be set here or via environment variable.

# --- Verification Configuration ---
verifier:
  type: "medrag"
  model_name: "mistralai/Mistral-Small-24B-Instruct-2501"  # Change to the latest released LLMs for better performance
  server_path: "http://localhost:8000/v1"
  corpus_name: "Textbooks"  # options: "PubMed", "Textbooks", "StatPearls", "Wikipedia", "MedCorp", "MEDIC". Our paper uses MEDIC (PubMed+StatPearls+Textbooks).
  n_returned_docs: 10
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

`./data/calmqa_english.jsonl` is the English subset of CaLMQA used in the paper. It has 96 samples, with
`id`, `question`, `response`, and additional CaLMQA metadata. Unlike AskDocs its questions are short and
its responses are long, which makes it the natural example for `qa_mode: true` (see [QA mode](#qa-mode---qa_mode)).

### QA mode (`--qa_mode`)

`qa_mode` controls whether the user's **question** is put in the decomposition context alongside the
response. It changes only the user message sent to the decomposition model; the system prompt is
identical either way.

```text
qa_mode: false (the default behavior)     qa_mode: true
-------------------------------------     ---------------------------------------------
Context: {response}                       Question Context: {question}
Please breakdown the following
sentence into independent facts:          Answer Context: {response}
{sentence}                                Please breakdown the following sentence into
Facts:                                    independent facts: {sentence}
                                          Facts:
```

**Which value should I use?** It depends on the shape of your data.

- **`false` — long question, noisy question.** When the question carries a lot of unnecessary
  information that is not needed to interpret the response, feeding it to the decomposer distracts
  the model and dilutes the response it is supposed to break down. `data/AskDocs.jsonl` is this case:
  the question is a patient's free-form post that is mostly personal backstory,
  and the chatbot response already restates whatever matters.
- **`true` — short question, long response.** When the response is only interpretable against the
  question, the decomposer needs the question to produce self-contained, decontextualized claims.
  `data/calmqa_english.jsonl` is this case: a short question and a much longer
  answer that refers back to entities introduced in the question.

Because the right value is a property of your dataset and not something MedScore can detect, you must
choose it explicitly: `--qa_mode` is **required** whenever the decomposition step runs with the
`medscore` or `custom` decomposer, unless `qa_mode` is set in the config file.

Notes and limitations:

- Only the `medscore` and `custom` decomposers support `qa_mode`. `factscore` does not use the context
  at all and `dndscore` builds its own prompt from the response, so both reject `qa_mode: true` with an
  error rather than silently ignoring it.
- The question is used **only** during decomposition. It is not added to the verifier prompt or to the
  MedRAG retrieval query, and it does not appear in `decompositions.jsonl`, `verifications.jsonl`, or
  `output.jsonl`.
- `qa_mode` is ignored with `--verify_only`, since decomposition does not run.
- If a record has no question (or an empty one) while `qa_mode: true`, MedScore logs a warning and
  decomposes that record with an empty question context instead of failing.

### Presenticized (pre-senticized) inputs

If your input data already contains sentence-level annotations (for example, produced by an external senticizer), MedScore can use those directly instead of running its internal sentence splitter. To enable this, add the top-level flag `presenticized: true` to your YAML config.

Behavior when presenticized is true:
- MedScore will look for a `sentences` list in each input record and use those entries as the source of sentences.
- Each item in `sentences` is a dict with a `text` field and an optional `sentence_id` field. If `sentence_id` is not provided, it will be auto-generated based on the list index.
- If the original `response` (or configured `response_key`) is present, it will be used as the `context` passed to the decomposer; otherwise the context will be reconstructed by joining the provided sentence texts.
- Records missing a valid `sentences` list will be skipped with a warning.
- `presenticized` and `qa_mode` compose: when `qa_mode` is `true`, the question is read from `question_key` at the top level of the record, independently of `sentences`.

Example YAML config enabling presenticized inputs:

```yaml
input_file: "data/AskDocs.demo.jsonl"
output_dir: "results"
response_key: "response"
qa_mode: false
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
