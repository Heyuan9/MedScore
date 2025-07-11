"""
Extract and verify claims with MedScore
"""

import os
import sys
import logging
import json
from typing import List, Any, Optional, Dict
from argparse import ArgumentParser

import jsonlines
from tqdm import tqdm

from .utils import parse_sentences
from .decomposer import Decomposer, MedScoreDecomposer, FActScoreDecomposer, DnDScoreDecomposer, CustomDecomposer
from .verifier import Verifier, InternalVerifier, MedRAGVerifier, ProvidedEvidenceVerifier

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(level=logging.WARNING, format=FORMAT)
logger = logging.getLogger(__name__)


def decomposition_mode_to_decompser(mode: str) -> Decomposer:
    mode = mode.lower()
    if mode == "medscore":
        return MedScoreDecomposer
    if mode == "factscore":
        return FactScoreDecomposer
    if mode == "dndscore":
        return DnDScoreDecomposer
    if mode == "custom":
        return CustomDecomposer
    raise IllegalArgumentException(f"Unknown decomposition mode: {mode}")


def verification_mode_to_verifier(mode: str) -> Verifier:
    mode = mode.lower()
    if mode == "internal":
        return InternalVerifier
    if mode == "provided":
        return ProvidedEvidenceVerifier
    if mode == "medrag":
        return MedRAGVerifier
    raise IllegalArgumentException(f"Unknown verification mode: {mode}")


class MedScore(object):
    def __init__(
            self,
            model_name_decomposition: str,
            server_decomposition: str,
            model_name_verification: str,
            server_verification: str,
            verification_mode: str,
            decomposition_mode: str,
            response_key: str,
            provided_evidence: Optional[Dict[str, str]] = None,
            custom_decomposition_prompt_path: Optional[str] = None,
    ):
        self.response_key = response_key
        decomp_class = decomposition_mode_to_decompser(decomposition_mode)
        self.decomposer = decomp_class(
            model_name=model_name_decomposition,
            server_path=server_decomposition,
            prompt_path=custom_decomposition_prompt_path
        )
        verif_class = verification_mode_to_verifier(verification_mode)
        self.verifier = verif_class(
            model_name=model_name_verification,
            server_path=server_verification,
            id_to_evidence=provided_evidence,
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
    # General
    parser.add_argument("--input_file", required=True, type=str)
    parser.add_argument("--output_dir", default="", type=str)
    parser.add_argument("--response_key", type=str, default="response")
    parser.add_argument("--decompose_only", action="store_true")
    parser.add_argument("--verify_only", action="store_true")
    # Decomposition
    parser.add_argument("--decomposition_mode", type=str, choices=["medscore", "factscore", "dndscore", "custom"], default="medscore")
    parser.add_argument("--model_name_decomposition", type=str, default="gpt-4o-mini")
    parser.add_argument("--server_decomposition", type=str, default="https://api.openai.com/v1")
    parser.add_argument("--decomp_prompt_path", type=str, default=None)
    # Verification
    parser.add_argument("--model_name_verification", type=str, default="gpt-4o-mini")
    parser.add_argument("--server_verification", type=str, default="https://api.openai.com/v1")
    parser.add_argument("--verification_mode", type=str, choices=["internal", "medrag", "provided"], default="internal")
    parser.add_argument("--provided_evidence_path", type=str, default=None)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)

    if args.verification_mode == "provided":
        if args.provided_evidence_path is not None:
            with open(args.provided_evidence_path, "r") as f:
                provided_evidence = json.load(f)
        else:
            raise InvalidArgumentException("Provided evidence path is required when verification_mode is 'provided'")
    else:
        provided_evidence = None

    if args.decomposition_mode == "custom" and not args.decomp_prompt_path:
        raise InvalidArgumentException("Must provide a decomposition prompt path with CustomDecomposer")

    # Initialize MedScore
    scorer = MedScore(
        model_name_decomposition=args.model_name_decomposition,
        server_decomposition=args.server_decomposition,
        model_name_verification=args.model_name_verification,
        server_verification=args.server_verification,
        verification_mode=args.verification_mode,
        decomposition_mode=args.decomposition_mode,
        response_key=args.response_key,
        provided_evidence=provided_evidence,
        custom_decomposition_prompt_path=args.decomp_prompt_path
    )

    # Load data
    with jsonlines.open(args.input_file) as reader:
        dataset = [item for item in reader.iter()]

    decomp_output_file = os.path.join(args.output_dir, "decompositions.jsonl")
    verif_output_file = os.path.join(args.output_dir, "verifications.jsonl")
    output_file = os.path.join(args.output_dir, "medscore_output.jsonl")

    # Decompose and save intermediate
    if not args.verify_only:
        # Batch decompose. Save intermediate.
        decompositions = scorer.decompose(dataset)
        with jsonlines.open(decomp_output_file, 'w') as writer:
            writer.write_all(decompositions)

        if args.decompose_only:
            exit(0)

    if args.verify_only:
        # Load pre-computed decompositions.
        with jsonlines.open(os.path.join(args.output_dir, "decompositions.jsonl"), 'r') as reader:
            decompositions = [item for item in reader.iter()]

    # Batch verify. Save intermediate.
    verifications = scorer.verify(decompositions)
    with jsonlines.open(verif_output_file, 'w') as writer:
        writer.write_all(verifications)

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
    with jsonlines.open(output_file, 'w') as writer:
        writer.write_all(combined_output)
