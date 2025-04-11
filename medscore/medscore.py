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
from decomposer import MedScoreDecomposer, FActScoreDecomposer
from verifier import InternalVerifier, MedRAGVerifier

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(level=logging.WARNING, format=FORMAT)
logger = logging.getLogger(__name__)


class MedScore(object):
    def __init__(
            self,
            model_name_decomposition: str,
            server_decomposition: str,
            model_name_verification: str,
            server_verification: str,
            verification_mode: str,
            decomposition_mode: str,
            response_key: str
    ):
        self.response_key = response_key
        if decomposition_mode == "medscore":
            self.decomposer = MedScoreDecomposer(
                model_name=model_name_decomposition,
                server_path=server_decomposition
            )
        else:
            self.decomposer = FActScoreDecomposer(
                model_name=model_name_decomposition,
                server_path=server_decomposition
            )
        if verification_mode == "internal":
            self.verifier = InternalVerifier(
                model_name=model_name_verification,
                server_path=server_verification
            )
        else:
            self.verifier = MedRAGVerifier(
                model_name=model_name_verification,
                server_path=server_verification
            )

    def decompose(
        self,
        dataset: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        # Split each response
        decomposer_input = []
        for item in dataset:
            sentences = parse_sentences(item[self.response_key])
            for idx, sentence in enumerate(sentences):
                decomposer_input.append({
                    "id": item["id"],
                    "sentence_id": idx,
                    "context": item[self.response_key],
                    "sentence": sentence["text"].strip(),
                })

        # Decompose
        decompositions = self.decomposer(decomposer_input)
        return decompositions

    def verify(self, decompositions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        non_empty_decompositions = [d for d in decompositions if d["claim"] is not None]
        verifier_output = self.verifier(non_empty_decompositions)
        return verifier_output


#############
# Main
#############
def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--input_file", required=True, type=str)
    parser.add_argument("--output_dir", default="", type=str)
    parser.add_argument("--model_name_decomposition", type=str, default="gpt-4o-mini")
    parser.add_argument("--server_decomposition", type=str, default="https://api.openai.com/v1")
    parser.add_argument("--model_name_verification", type=str, default="gpt-4o-mini")
    parser.add_argument("--server_verification", type=str, default="https://api.openai.com/v1")
    parser.add_argument("--verification_mode", type=str, choices=["internal", "medrag"], default="internal")
    parser.add_argument("--decomposition_mode", type=str, choices=["medscore", "factscore"], default="medscore")
    parser.add_argument("--response_key", type=str, default="response")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    # Initialize MedScore
    scorer = MedScore(
        model_name_decomposition=args.model_name_decomposition,
        server_decomposition=args.server_decomposition,
        model_name_verification=args.model_name_verification,
        server_verification=args.server_verification,
        verification_mode=args.verification_mode,
        decomposition_mode=args.decomposition_mode,
        response_key=args.response_key
    )

    # Load data
    with jsonlines.open(args.input_file) as reader:
        dataset = [item for item in reader.iter()]

    # # Batch decompose. Save intermediate.
    # decompositions = scorer.decompose(dataset)
    # decomp_output_file = os.path.join(args.output_dir, "decompositions.jsonl")
    # with jsonlines.open(decomp_output_file, 'w') as writer:
    #     writer.write_all(decompositions)
    #
    # # Batch verify. Save intermediate.
    # verifications = scorer.verify(decompositions)
    # output_file = os.path.join(args.output_dir, "verifications.jsonl")
    # with jsonlines.open(output_file, 'w') as writer:
    #     writer.write_all(verifications)

    with jsonlines.open(os.path.join(args.output_dir, "decompositions.jsonl"), 'r') as reader:
        decompositions = [item for item in reader.iter()]

    with jsonlines.open(os.path.join(args.output_dir, "verifications.jsonl"), 'r') as reader:
        verifications = [item for item in reader.iter()]

    # Combine
    combined_output = {
        d["id"]: {
            "id": d["id"],
            "claims": []
        } for d in decompositions
    }
    for verif in verifications:
        claim_info = {
            k: v for k, v in verif.items() if k not in {"id", "sentence_id", "claim_id"}
        }
        combined_output[verif['id']]['claims'].append(claim_info)

    # Aggregate scores
    for idx in combined_output:
        claim_scores = [c['score'] for c in combined_output[idx]['claims']]
        if len(claim_scores) == 0:
            combined_output[idx]["score"] = None
        else:
            combined_output[idx]["score"] = sum(claim_scores) / len(claim_scores)

    combined_output = [v for k, v in combined_output.items()]
    output_file = os.path.join(args.output_dir, "medscore_output.jsonl")
    with jsonlines.open(output_file, 'w') as writer:
        writer.write_all(combined_output)
