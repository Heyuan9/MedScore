"""
Misc utility functions
"""
from typing import Optional, Union, List, Dict, Any, Iterable
from itertools import islice
import logging
import os
import sys

import spacy
import yaml
from dotenv import load_dotenv
from pydantic import ValidationError

from .config_schema import MedScoreConfig

nlp = spacy.load("en_core_web_sm")
logger = logging.getLogger(__name__)


def env_constructor(loader, node):
    """Constructor for the !env tag in YAML configs."""
    value = loader.construct_scalar(node)
    env_value = os.environ.get(value)
    logger.debug(f"Replacing {value} with its environment variable.")
    return env_value

yaml.add_constructor('!env', env_constructor, Loader=yaml.SafeLoader)

def load_config(
        config_path: str,
        argument_overrides: Optional[Dict[str, Any]] = None,
) -> MedScoreConfig:
    """
    Loads a YAML config file with !env support and returns a validated MedScoreConfig object.
    Args:
        argument_overrides:
        config_path (str): Path to the YAML configuration file.
    Returns:
        MedScoreConfig: Validated config object.
    Raises:
        FileNotFoundError, yaml.YAMLError, pydantic.ValidationError
    """
    # Load environment variables from .env file if present
    load_dotenv()

    # Load and parse the YAML config file
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        logger.debug(f"Loaded config from {config_path}: {config_data}")
    except (ValidationError, FileNotFoundError) as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML config file: {e}")
        sys.exit(1)

    # Apply command-line argument overrides
    if argument_overrides:
        for arg_field in ["input_file", "output_dir"]:
            if arg_field in argument_overrides and argument_overrides[arg_field] is not None:
                config_data[arg_field] = argument_overrides[arg_field]
        logger.debug(f"Applied argument overrides: {argument_overrides}")

    # Create MedScoreConfig object
    return MedScoreConfig(**config_data)


def process_claim(claims: List[str]) -> List[str]:
    """
    Process the claim to remove any unwanted characters and split it into individual claims.
    
    Args:
        claims (list): A list of claims to be processed.
        
    Returns:
        list: A list of processed claims.
    """
    # drop - in front of the claim
    claims = [claim.strip('-').strip() for claim in claims]

    # remove 'no verifiable claim' from the claims
    claims = [claim for claim in claims if 'no verifiable claim' not in claim.lower()]
    
    return claims


def parse_sentences(
    passage: str,
) -> List[Dict[str, Any]]:
    doc = nlp(passage)
    sentences = []
    # sent is a spacy span object https://spacy.io/api/span#init
    # span start/end is based on token index (sent.start, sent.end)
    # convert token index to character to match the annotations
    for sent in doc.sents:
        sentences.append({
            "text": sent.text,
            "span_start": sent.start_char,
            "span_end": sent.end_char
        })
    return sentences


def chunker(
        iterable: Iterable,
        n: int
):
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, n))
        if not chunk:
            return
        yield chunk
