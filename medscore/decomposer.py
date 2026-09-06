"""
Decomposer
"""
import os
from functools import partial
import asyncio
from typing import List, Any, Optional, Dict
import ast
import logging

import jsonlines
from tqdm import tqdm
import backoff
import requests
from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion
import nest_asyncio
from registrable import Registrable

from .utils import process_claim, parse_sentences, chunker
from .prompts import MEDSCORE_PROMPT, FACTSCORE_PROMPT, DND_PROMPT

logger = logging.getLogger(__name__)
nest_asyncio.apply()

# Registered decomposition methods that can put the question in the decomposition context.
# These are exactly the classes below that set `supports_qa_mode = True`; the name list lets
# the CLI decide whether --qa_mode is required without instantiating a decomposer first.
QA_MODE_DECOMPOSERS = ("medscore", "custom")


class Decomposer(Registrable):
    """Base class for all decomposers."""

    # Subclasses that can put the question in the decomposition context set this to True.
    # Such a subclass must implement format_input_qa in addition to format_input.
    supports_qa_mode: bool = False

    def __init__(
            self,
            server_path: str,
            model_name: str,
            api_key: Optional[str] = None,
            random_state: int = 42,
            batch_size: int = 32,
            qa_mode: bool = False,
            **kwargs,  # To allow for extra params from config
    ):
        if qa_mode and not self.supports_qa_mode:
            supported = " or ".join(f"'{name}'" for name in QA_MODE_DECOMPOSERS)
            raise ValueError(
                f"The '{self.__class__.__name__}' decomposer does not support qa_mode, because it "
                f"does not use the response as context in the same way. Use the {supported} "
                f"decomposer, or set qa_mode to false."
            )
        self.qa_mode = qa_mode
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.client = AsyncOpenAI(
            base_url=server_path,
            api_key=api_key,
        )
        self.model_name = model_name
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
            if self.qa_mode:
                formatted_input = self.format_input_qa(d.get('question', ''), d['context'], d['sentence'])
            else:
                formatted_input = self.format_input(d['context'], d['sentence'])
            system_prompt = self.get_system_prompt()
            if system_prompt:
                messages.append([
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": formatted_input}
                ])
            else:
                messages.append([
                    {"role": "user", "content": formatted_input}
                ])

        # Async calls for batch_size items
        all_completions = []
        n_iter = (len(messages) + self.batch_size - 1) // self.batch_size
        for batch in tqdm(chunker(messages, self.batch_size), desc="Decompose", total=n_iter, ncols=80):
            completions = asyncio.run(self.batch_response(batch))
            all_completions.extend(completions)

        # Format claims
        decompositions = self.format_completions(decomp_input, all_completions)
        return decompositions

    def format_completions(self, decomp_input: List[Dict[str, Any]], completions: List[ChatCompletion]) -> List[
        Dict[str, Any]]:
        decompositions = []
        prompt_only_keys = self.prompt_only_keys()
        for d_input, completion in zip(decomp_input, completions):
            claim_list = completion.choices[0].message.content.split("\n")
            claim_list = process_claim(claim_list)
            for idx, claim in enumerate(claim_list):
                decomp = {k: v for k, v in d_input.items() if k not in prompt_only_keys}
                decomp["claim"] = claim
                decomp["claim_id"] = idx
                decompositions.append(decomp)
            if not claim_list:
                decomp = {k: v for k, v in d_input.items() if k not in prompt_only_keys}
                decomp["claim"] = None
                decompositions.append(decomp)
        return decompositions

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, asyncio.TimeoutError),
        max_time=60
    )
    async def batch_response(self, batch: List[List[Dict[str, str]]]) -> List[ChatCompletion]:
        async_responses = [
            self.agent(messages=x) for x in batch
        ]
        return await asyncio.gather(*async_responses)

    def format_input(self, context: str, sentence: str) -> str:
        raise NotImplementedError

    def format_input_qa(self, question: str, context: str, sentence: str) -> str:
        """Format the user message when qa_mode is on. Only called if supports_qa_mode is True."""
        raise NotImplementedError

    def prompt_only_keys(self) -> set:
        """Input keys that are prompt material and must not leak into the output records."""
        return {"context", "question"} if self.qa_mode else {"context"}

    def get_system_prompt(self) -> Optional[str]:
        return None


@Decomposer.register("medscore")
class MedScoreDecomposer(Decomposer):
    """
    Note for subclasses: overriding only format_input is not enough when qa_mode is on, since
    supports_qa_mode is inherited. Override format_input_qa as well.
    """
    supports_qa_mode = True

    def get_system_prompt(self) -> str:
        return MEDSCORE_PROMPT

    def format_input(self, context: str, sentence: str) -> str:
        return f"Context: {context}\nPlease breakdown the following sentence into independent facts: {sentence}\nFacts:\n"

    def format_input_qa(self, question: str, context: str, sentence: str) -> str:
        return f"Question Context: {question}\n\nAnswer Context: {context}\nPlease breakdown the following sentence into independent facts: {sentence}\nFacts:\n"


@Decomposer.register("custom")
class CustomDecomposer(Decomposer):
    """
    Note for subclasses: overriding only format_input is not enough when qa_mode is on, since
    supports_qa_mode is inherited. Override format_input_qa as well.
    """
    supports_qa_mode = True

    def __init__(
            self,
            prompt_path: str,
            *args,
            **kwargs
    ):
        self.prompt_path = prompt_path
        super().__init__(*args, **kwargs)
        with open(prompt_path) as f:
            self._system_prompt = f.read().strip()

    def get_system_prompt(self) -> str:
        return self._system_prompt

    def format_input(self, context: str, sentence: str) -> str:
        return f"Context: {context}\nPlease breakdown the following sentence into independent facts: {sentence}\nFacts:\n"

    def format_input_qa(self, question: str, context: str, sentence: str) -> str:
        return f"Question Context: {question}\n\nAnswer Context: {context}\nPlease breakdown the following sentence into independent facts: {sentence}\nFacts:\n"


@Decomposer.register("factscore")
class FActScoreDecomposer(Decomposer):
    def get_system_prompt(self) -> str:
        return FACTSCORE_PROMPT

    def format_input(self, context: str, sentence: str) -> str:
        return f"Please breakdown the following sentence into independent facts: {sentence}"


@Decomposer.register("dndscore")
class DnDScoreDecomposer(Decomposer):
    def __init__(self, *args, **kwargs):
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

    def get_system_prompt(self) -> Optional[str]:
        return None  # DnD prompt is part of the user message

    def format_input(self, context: str, sentence: str) -> str:
        return DND_PROMPT.replace("[paragraph]", context).replace("[sentence]", sentence)

    def format_completions(self, decomp_input: List[Dict[str, Any]], completions: List[ChatCompletion]) -> List[
        Dict[str, Any]]:
        decompositions = []
        prompt_only_keys = self.prompt_only_keys()
        for d_input, completion in zip(decomp_input, completions):
            model_output = completion.choices[0].message.content.strip()
            try:
                extra, subclaim_str = [x.strip() for x in model_output.split("##CONTEXT-SUBCLAIM PAIRS##:")]
                subclaim_str = subclaim_str.replace('\n', '').strip()
                subclaim_dict = ast.literal_eval(subclaim_str)
                explanation = extra.split("##EXPLANATION##:")[-1]

                decomp = {k: v for k, v in d_input.items() if k not in prompt_only_keys}

                if not isinstance(subclaim_dict, list):
                    raise ValueError("Parsed subclaims is not a list.")

                for idx, claim_dict in enumerate(subclaim_dict):
                    new_decomp = decomp.copy()
                    new_decomp["claim"] = claim_dict["decontextualized"]
                    new_decomp["claim_id"] = idx
                    new_decomp["claim_meta"] = {
                        "subclaim": claim_dict["subclaim"],
                        "explanation": explanation
                    }
                    decompositions.append(new_decomp)

                if not subclaim_dict:
                    decomp["claim"] = None
                    decompositions.append(decomp)

            except (ValueError, SyntaxError) as e:
                logger.warning(
                    f"Invalid dictionary for {d_input['id']=}, {d_input['sentence_id']=}: {e}\nOutput: {model_output}")
                decomp = {k: v for k, v in d_input.items() if k not in prompt_only_keys}
                decomp["claim"] = None
                decompositions.append(decomp)

        return decompositions
