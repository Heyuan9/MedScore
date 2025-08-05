"""
Main script to extract and verify claims with MedScore.
"""
import os
import sys
import logging
import json
import yaml
from typing import List, Any, Dict
from argparse import ArgumentParser

import jsonlines
from pydantic import ValidationError

from .utils import parse_sentences
from .config_schema import MedScoreConfig, ProvidedEvidenceVerifierConfig
from .registry import build_component

# --- Setup Logging ---
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)


class MedScore:
    """The main MedScore pipeline class."""
    def __init__(self, config: MedScoreConfig):
        """
        Initializes the MedScore pipeline from a validated Pydantic config object.
        """
        # Build the decomposer and verifier from the config using the registry
        logger.info(f"Building decomposer of type: {config.decomposer.type}")
        self.decomposer = build_component(config.decomposer, "decomposer")

        logger.info(f"Building verifier of type: {config.verifier.type}")
        self.verifier = build_component(config.verifier, "verifier")

        self.response_key = config.response_key

    def decompose(self, dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Decomposes responses from a dataset into individual claims."""
        decomposer_input = []
        for item in dataset:
            if self.response_key not in item:
                logger.warning(f"ID '{item.get('id')}' missing response_key '{self.response_key}'. Skipping.")
                continue
            sentences = parse_sentences(item[self.response_key])
            for idx, sentence in enumerate(sentences):
                decomposer_input.append({
                    "id": item["id"],
                    "sentence_id": idx,
                    "context": item[self.response_key],
                    "sentence": sentence["text"].strip(),
                })

        if not decomposer_input:
            logger.error("No valid inputs found for the decomposer.")
            return []

        decompositions = self.decomposer(decomposer_input)
        return decompositions

    def verify(self, decompositions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verifies a list of decomposed claims."""
        non_empty_decompositions = [d for d in decompositions if d.get("claim") is not None]
        if not non_empty_decompositions:
            logger.warning("No valid claims to verify.")
            return []

        verifier_output = self.verifier(non_empty_decompositions)
        return verifier_output


def main():
    """Main entry point for the command-line script."""
    parser = ArgumentParser(description="Run MedScore factuality evaluation from a configuration file.")
    parser.add_argument("--config", type=str, required=True, help="Path to the YAML configuration file.")
    parser.add_argument("--input_file", type=str, help="Override the input data file specified in the config.")
    parser.add_argument("--output_dir", type=str, help="Override the output directory specified in the config.")
    parser.add_argument("--decompose_only", action="store_true", help="Only run the decomposition step.")
    parser.add_argument("--verify_only", action="store_true", help="Only run the verification step (requires existing decomposition file).")
    args = parser.parse_args()

    # Load and validate configuration from YAML file
    try:
        with open(args.config, 'r') as f:
            config_data = yaml.safe_load(f)

        # Handle command-line overrides for file paths
        if args.input_file:
            config_data['input_file'] = args.input_file
        if args.output_dir:
            config_data['output_dir'] = args.output_dir

        config = MedScoreConfig(**config_data)

    except (ValidationError, FileNotFoundError) as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML config file: {e}")
        sys.exit(1)

    output_dir = config_data.get('output_dir', '.')
    input_file = config_data.get('input_file')

    if not input_file:
        logger.error("Input file must be specified either in the config or via --input_file.")
        sys.exit(1)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Initialize MedScore with the validated config
    scorer = MedScore(config)

    # Load data
    try:
        with jsonlines.open(input_file) as reader:
            dataset = [item for item in reader.iter()]
    except (FileNotFoundError, IOError) as e:
        logger.error(f"Could not read input file at {input_file}: {e}")
        sys.exit(1)

    decomp_output_file = os.path.join(output_dir, "decompositions.jsonl")
    verif_output_file = os.path.join(output_dir, "verifications.jsonl")
    final_output_file = os.path.join(output_dir, "output.jsonl")

    # --- Main Pipeline Execution ---
    decompositions = []
    if not args.verify_only:
        logger.info(f"Starting decomposition for {input_file}...")
        decompositions = scorer.decompose(dataset)
        with jsonlines.open(decomp_output_file, 'w') as writer:
            writer.write_all(decompositions)
        logger.info(f"Decompositions saved to {decomp_output_file}")
        if args.decompose_only:
            logger.info("Decomposition finished. Exiting as requested.")
            sys.exit(0)

    if args.verify_only:
        try:
            with jsonlines.open(decomp_output_file, 'r') as reader:
                decompositions = [item for item in reader.iter()]
            logger.info(f"Loaded existing decompositions from {decomp_output_file}")
        except FileNotFoundError:
            logger.error(f"Verify-only mode requires an existing decomposition file at {decomp_output_file}")
            sys.exit(1)

    logger.info("Starting verification...")
    verifications = scorer.verify(decompositions)
    with jsonlines.open(verif_output_file, 'w') as writer:
        writer.write_all(verifications)
    logger.info(f"Verifications saved to {verif_output_file}")

    # Combine and aggregate scores
    logger.info("Aggregating results...")
    combined_output = {item["id"]: {"id": item["id"], "claims": []} for item in dataset}
    for verif in verifications:
        claim_info = {k: v for k, v in verif.items() if k not in {"id", "sentence_id", "claim_id"}}
        if verif['id'] in combined_output:
            combined_output[verif['id']]['claims'].append(claim_info)

    for idx in combined_output:
        claim_scores = [c['score'] for c in combined_output[idx]['claims'] if 'score' in c]
        combined_output[idx]["score"] = sum(claim_scores) / len(claim_scores) if claim_scores else None

    with jsonlines.open(final_output_file, 'w') as writer:
        writer.write_all(list(combined_output.values()))

    logger.info(f"Processing complete. Final results are in {final_output_file}")


if __name__ == '__main__':
    main()
