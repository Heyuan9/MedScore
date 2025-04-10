"""
Misc utility functions
"""
from typing import Optional, Union, List, Dict, Any, Iterable
from itertools import islice

import spacy
nlp = spacy.load("en_core_web_sm")


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
