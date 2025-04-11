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
import nest_asyncio

from .utils import process_claim, parse_sentences, chunker
from .prompts import MEDSCORE_PROMPT, FACTSCORE_PROMPT, DND_PROMPT

nest_asyncio.apply()


class Decomposer(object):
    def __init__(
            self,
            server_path: str,
            model_name: str,
            random_state: int = 42,
            batch_size: int = 32
    ):
        self.client = AsyncOpenAI(
            base_url=server_path
        )
        self.model_name = model_name
        self.system_prompt = self.get_prompt()
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
            if self.get_prompt():
                messages.append([
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": formatted_input}
                ])
            else:
                messages.append([
                    {"role": "user", "content": formatted_input}
                ])

        # Async calls for batch_size items
        all_completions = []
        n_iter = len(messages) // self.batch_size
        for batch in tqdm(chunker(messages, self.batch_size), desc="Decompose", total=n_iter, ncols=0):
            completions = asyncio.run(self.batch_response(batch))
            all_completions.extend(completions)

        # Format claims
        decompositions = []
        for d_input, completion in zip(decomp_input, all_completions):
            claim_list = completion.choices[0].message.content.split("\n")
            claim_list = process_claim(claim_list)
            for idx, claim in enumerate(claim_list):
                decomp = {k:v for k,v in d_input.items() if k!="context"}
                decomp["claim"] = claim
                decomp["claim_id"] = idx
                decompositions.append(decomp)
            if not claim_list:
                decomp = {k:v for k,v in d_input.items() if k!="context"}
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
        raise NotImplementedError

    def get_prompt(self) -> Optional[str]:
        raise None


class MedScoreDecomposer(Decomposer):
    def get_prompt(self) -> str:
        return MEDSCORE_PROMPT

    def format_input(self, context: str, sentence: str) -> str:
        return f"Context: {context}\nPlease breakdown the following sentence into independent facts: {sentence}\nFacts:\n"


class FActScoreDecomposer(Decomposer):
    def get_prompt(self) -> str:
        return FACTSCORE_PROMPT

    def format_input(self, context: str, sentence: str) -> str:
        return f"Please breakdown the following sentence into independent facts: {sentence}"


class DnDScoreDecomposer(Decomposer):
    def __init__(
        self,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        # Override self.agent to match settings from DnDScore
        self.agent = partial(
            self.client.chat.completions.create,
            model=self.model_name,
            seed=self.random_state,
            temperature=0.75,
            top_p=1.0,
            max_tokens=2048
        )

    def format_input(self, context: str, sentence: str) -> str:
        return DNDS_PROMPT.format(context=context, sentence=sentence)

