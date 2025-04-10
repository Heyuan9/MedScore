"""
Decomposer
"""

import os
from functools import partial
import asyncio
from typing import List, Any, Optional, Dict

import jsonlines
from tqdm import tqdm
import backoff
import requests
from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion

from utils import process_claim, parse_sentences, chunker
from prompts import MEDSCORE_PROMPT


class Decomposer(object):
    def __init__(
            self,
            server_path: str,
            model_name: str,
            system_prompt: str = MEDSCORE_PROMPT,
            random_state: int = 42,
            batch_size: int = 32
    ):
        self.client = AsyncOpenAI(
            base_url=server_path
        )
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.random_state = random_state
        self.batch_size = batch_size

        self.agent = partial(
            self.client.chat.completions.create,
            model=self.model_name,
            seed=self.random_state,
            temperature=0.0,
            top_p=1.0,
            max_tokens=256
        )

    def __call__(self, decomp_input: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Prepare prompt and user input
        messages = []
        for d in decomp_input:
            formatted_input = self.format_input(d['context'], d['sentence'])
            messages.append([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": formatted_input}
            ])

        # Async calls for batch_size items
        all_completions = []
        n_iter = len(messages) // self.batch_size
        for batch in tqdm(chunker(messages, self.batch_size), desc="Decompose", total=n_iter):
            completions = asyncio.run(self.batch_response(batch))
            all_completions.extend(completions)

        # Format claims
        decompositions = []
        for d_input, completion in zip(decomp_input, all_completions):
            claim_list = completion.choices[0].message.content.split("\n")
            claim_list = process_claim(claim_list)
            for claim in claim_list:
                decomp = {k:v for k,v in d_input.items()}
                decomp["claim"] = claim
                decompositions.append(decomp)
            if not claim_list:
                decomp = {k:v for k,v in d_input.items()}
                decomp["claim"] = None
                decompositions.append(decomp)
        return decompositions

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_time=60
    )
    async def batch_response(self, batch: List[List[Dict[str, str]]]) -> List[ChatCompletion]:
        async_responses = [
            self.agent(
                messages=x,
            )
            for x in batch
        ]
        return await asyncio.gather(*async_responses)

    def format_input(self, context: str, sentence: str) -> str:
        return f"Context: {context}\nPlease breakdown the following sentence into independent facts: {sentence}\nFacts:\n"

