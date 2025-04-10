"""
Extract and verify claims with MedScore
"""

import os
import sys
import logging
from typing import List, Any, Optional, Dict
from argparse import ArgumentParser

import jsonlines
from tqdm import tqdm

from utils import parse_sentences
from decomposer import Decomposer


class MedScore(object):
    def __init__(
            self,
            model_name_decomposition: str,
            server_decomposition: str,
            model_name_verification: str,
            server_verification: str,
            verification_mode: str
    ):
        self.decomposer = Decomposer(
            model_name=model_name_decomposition,
            server_path=server_decomposition
        )

    def decompose(
        self,
        dataset: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        # Split each response
        decomposer_input = []
        for item in dataset:
            sentences = parse_sentences(item["augment_withquestion"])
            for idx, sentence in enumerate(sentences):
                decomposer_input.append({
                    "id": item["id"],
                    "sentence_id": idx,
                    "context": item["augment_withquestion"],
                    "sentence": sentence["text"],
                })

        # Decompose
        decompositions = self.decomposer(decomposer_input)

        # Re-sort
        return decompositions

    def verify(self, claim):
        return


#############
# Main
#############
def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--input_file", required=True, type=str)
    parser.add_argument("--output_dir", default="", type=str)
    parser.add_argument("--model_name_decomposition", type=str, default="gpt-4o-mini")
    parser.add_argument("--server_decomposition", type=str, default="https://api.openai.com")
    parser.add_argument("--model_name_verification", type=str, default="gpt-4o-mini")
    parser.add_argument("--server_verification", type=str, default="https://api.openai.com")
    parser.add_argument("--verification_mode", type=str, choices=["internal", "medrag"], default="internal")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    # Initialize MedScore
    scorer = MedScore(
        model_name_decomposition=args.model_name_decomposition,
        server_decomposition=args.server_decomposition,
        model_name_verification=args.model_name_verification,
        server_verification=args.server_verification,
        verification_mode=args.verification_mode
    )

    # Load data
    with jsonlines.open(args.input_file) as reader:
        dataset = [item for item in reader.iter()]

    # Batch decompose
    # Save intermediate
    decompositions = scorer.decompose(dataset)
    decomp_output_file = os.path.join(args.output_dir, "decompositions.jsonl")
    with jsonlines.open(decomp_output_file, 'w') as writer:
        writer.write_all(decompositions)

    exit(0)

    # Batch verify
    output = scorer.verify(decompositions)
    output_file = os.path.join(args.output_dir, "medscore_output.jsonl")
    with jsonlines.open(output_file, 'w') as writer:
        writer.write_all(output)

