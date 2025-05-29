# MedScore

Supporting code and data for MedScore, a medical chatbot factuality evaluation system that can adapt to other domains easily.
See [the MedScore paper](https://arxiv.org/abs/2505.18452) for details. Following the structure of the paper (update MedScore taxonomy based on domain-specific requirements for valid claim definition, then change the MedScore Instructions and domain-specific In Context Learning examples), researchers can adapt this tool to their text domain optimally with minimal effort.

If you use this tool, please cite

```
@misc{huang2025medscorefactualityevaluationfreeform,
      title={MedScore: Factuality Evaluation of Free-Form Medical Answers}, 
      author={Heyuan Huang and Alexandra DeLucia and Vijay Murari Tiyyala and Mark Dredze},
      year={2025},
      eprint={2505.18452},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2505.18452}, 
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
   export TOGETHER_API_KEY=""
    ```

3. [Optional] Set `MEDRAG_CORPUS` environment variable.

    ```bash
   export MEDRAG_CORPUS=""
    ```

Setting this variable makes sure that the MedRAG corpus will only be downloaded once.


## Running MedScore

MedScore can be run from the command line. The options are explained below.

```bash
python -m medscore.medscore --input_file "Your datafile.jsonl" --response_key "key of the paragraph to be evaluated" --output_dir "path to result folder" --decomposition_mode "medscore" --model_name_decomposition gpt-4o-mini --model_name_verification "gpt-4o" --verification_mode "internal" --server_decomposition "https://api.openai.com/v1" --server_verification "https://api.openai.com/v1" 
```

- General settings
  - `input_file`: Path to the input data file. It should be in `jsonl` format.
    - `id`: A unique identifier for the instance.
    - `repsonse`: The text response from the medical chatbot. This key can be changed with `--response_key`.
    - Any other metadata.
  - `output_dir`: Path to the output directory. The output files are `decompositions.jsonl`, `verifications.jsonl`, and `medscore_output.jsonl`.
    - Default: current directory
- Decomposition-related settings
  - `decomposition_mode`: Method for decomposing the sentences into claims.
    - Options:
      - `factscore`: FActScore prompt from [FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation (Min et al., EMNLP 2023)](https://aclanthology.org/2023.emnlp-main.741/)
      - `medscore`: Our work.
      - `dndscore`: Prompt from [DnDScore: Decontextualization and Decomposition for Factuality Verification in Long-Form Text Generation (Wanner et al., arXiv 2024)](https://arxiv.org/abs/2412.13175)
      - `custom`: A custom user-written prompt with instructions and in-domain examples best for your dataset. The `decomp_prompt_path` must also be provided. We recommend following the format of MedScore_prompt.txt to make the first customization try easier.
    - Default: `MedScore`
  - `decomp_prompt_path`: Path to a `txt` file containing a system prompt for decomposition. See the prompts in `medscore/prompts.py` for examples.
  - `model_name_decomposition`: The name of the model for decomposing the response into claims. It should the model identifier for a hosted HuggingFace model, OpenAI model, TogetherAI model, or locally-hosted vLLM model.
    - Default: `gpt-4o-mini`
  - `server_decomposition`: The server path for the decomposition model. 
    - Default: `https://api.openai.com/v1`
  - `response_key`: The `jsonl` key corresponding to the text for decomposition.
    - Default: `response`.
- Verification-related settings
  - `model_name_verification`: The name of the model for decomposing the response into claims. It should the model identifier for a hosted HuggingFace model, OpenAI model, TogetherAI model, or locally-hosted vLLM model.
    - Default: `gpt-4o-mini`
  - `verification_mode`: The method for verification.
    - Options:
      - `medrag`: Verify the `response` against MedCorp from [Benchmarking Retrieval-Augmented Generation for Medicine (Xiong et al., Findings 2024)](https://aclanthology.org/2024.findings-acl.372/). The default settings retrieve the top 5 passages from PubMed, StatPearls, and academic textbooks with the `MedCPT` encoder.
      - `internal`: Verify against the internal knowledge of an LLM. 
      - `provided`: Verify against pre-collected user-provided evidence. Requires `provided_evidence_path` to be set.
    - Default: `internal`
  - `server_verification`: The server path for the verification model. 
    - Default: `https://api.openai.com/v1`
  - `provided_evidence_path`: Path to `json` file in `{"{id}": "{evidence}"}` format, where the `id` is the same as the entry id in `input_file`.


Example settings for decomposing and verifying with `GPT4o`:

```bash
--model_name_decomposition gpt-4o \
--model_name_verification gpt-4o \
--verification_mode internal \
--server_decomposition "https://api.openai.com/v1" \
--server_verification "https://api.openai.com" \
```

Example settings for decomposing with GPT4o and verifying with MedRag against a locally-hosted Mistral Small 3 model:
```bash
--model_name_decomposition gpt-4o \
--model_name_verification "mistralai/Mistral-Small-24B-Instruct-2501" \
--verification_mode medrag \
--server_decomposition "https://api.openai.com/v1" \
--server_verification "http://localhost:8000" \
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

