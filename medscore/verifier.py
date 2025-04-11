"""Verifier"""

import os
from functools import partial
import asyncio
from pyexpat.errors import messages
from typing import List, Dict, Any, Optional

import jsonlines
from tqdm import tqdm
import backoff
import requests
from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion
import nest_asyncio

from .utils import chunker
from .prompts import INTERNAL_KNOWLEDGE_PROMPT
from .medrag_retriever import MedRAGRetriever

nest_asyncio.apply()


class Verifier(object):
    def __init__(
            self,
            server_path: str,
            model_name: str,
            random_state: int = 42,
            batch_size: int = 32,
            **kwargs,  # Ignore options passed that do not matter to this class
    ):
        self.client = AsyncOpenAI(
            base_url=server_path
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

    def __call__(self, decompositions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Prepare user input
        verifier_input = self.prepare_verification_input(decompositions)
        messages = self.prepare_messages(verifier_input)

        # Async calls for batch_size items
        all_completions = []
        n_iter = len(messages) // self.batch_size
        for batch in tqdm(chunker(messages, self.batch_size), desc="Verify", total=n_iter):
            completions = asyncio.run(self.batch_response(batch))
            all_completions.extend(completions)

        # Format model output
        verification_output = []
        for v_input, completion in zip(verifier_input, all_completions):
            raw_output = completion.choices[0].message.content.strip()
            is_supported = self.parse_verification_output(raw_output)
            output = {k: v for k, v in v_input.items()}
            output["raw"] = raw_output
            output["score"] = is_supported
            verification_output.append(output)
        return verification_output

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

    def parse_verification_output(self, completion_message: str) -> float:
        generated_answer = completion_message.strip().lower()
        is_supported = 0.0

        if "true" in generated_answer or "false" in generated_answer:
            if "true" in generated_answer and "false" not in generated_answer:
                is_supported = 1.0
            elif "false" in generated_answer and "true" not in generated_answer:
                is_supported = 0.0
            else:
                # I feel this is random tie breaking
                is_supported = generated_answer.index("true") > generated_answer.index("false")
                is_supported = 1.0 if is_supported else 0.0
        else:
            generated_answer = generated_answer.translate(str.maketrans("", "", string.punctuation)).split()
            is_supported = all(
                [keyword not in generated_answer for keyword in ["not", "cannot", "unknown", "information"]])
            is_supported = 1.0 if is_supported else 0.0
        return is_supported

    def prepare_verification_input(self, decompositions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def format_input(self, evidence: str, claim: str) -> str:
        raise NotImplementedError

    def prepare_messages(self, verification_input: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        raise NotImplementedError


class InternalVerifier(Verifier):
    """Verify claims against internal model knowledge"""
    def prepare_verification_input(self, decompositions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        verification_input = []
        for d in decompositions:
            d["evidence"] = None
            verification_input.append(d)
        return verification_input

    def format_input(self, evidence: str, claim: str) -> str:
        return f"""Using your own knowledge, answer the question.\n\nInput: {claim} True or False?\n\nOutput:"""

    def prepare_messages(self, verification_input: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        messages = []
        for d in verification_input:
            formatted_input = self.format_input("", d['claim'])
            messages.append([
                {"role": "system", "content": INTERNAL_KNOWLEDGE_PROMPT},
                {"role": "user", "content": formatted_input}
            ])
        return messages


class ProvidedEvidenceVerifier(Verifier):
    def __init__(
            self,
            id_to_evidence: Dict[str, str],
            *args,
            **kw
    ):
        super().__init__(*args, **kw)
        self.id_to_evidence = id_to_evidence

    """Verify claims against a pre-provided `evidence` key"""
    def prepare_verification_input(self, decompositions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        verification_input = []
        for d in decompositions:
            d["evidence"] = self.id_to_evidence[d['id']]
            verification_input.append(d)
        return verification_input

    def format_input(self, evidence: str, claim: str) -> str:
        return f"""Answer the question based on the given context.\n\n{evidence}\n\nInput: {claim} True or False?\nOutput:"""

    def prepare_messages(self, verification_input: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        messages = []
        for d in verification_input:
            formatted_input = self.format_input(d['evidence'], d['claim'])
            messages.append([
                {"role": "user", "content": formatted_input}
            ])
        return messages


class MedRAGVerifier(Verifier):
    def __init__(
        self,
        retriever_name: str = "MedCPT",
        corpus_name: str = "MEDIC",
        db_dir: str = os.environ.get("MEDRAG_CORPUS", "./corpus"),
        HNSW: bool = False,
        cache: bool = False,
        n_returned_docs: int = 5,
        *args,
        **kw
    ):
        super().__init__(*args, **kw)
        self.retriever = MedRAGRetriever(
            retriever_name=retriever_name,
            corpus_name=corpus_name,
            db_dir=db_dir,
            HNSW=HNSW,
            cache=cache,
            n_returned_docs=n_returned_docs
        )

    def prepare_verification_input(self, decompositions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        verification_input = []
        n_iter = len(decompositions) // self.batch_size
        for batch in tqdm(chunker(decompositions, self.batch_size), desc="Retrieving MedRAG", total=n_iter, ncols=0):
            retrieved_all = self.retriever(query=[d['claim'] for d in batch])
            for decomp, retrieved in zip(batch, retrieved_all):
                v_input = {k: v for k, v in decomp.items()}
                v_input["evidence"] = retrieved
                verification_input.append(v_input)
        return verification_input

    def format_input(self, evidence: str, claim: str) -> str:
        return f"""Answer the question based on the given context.\n\n{evidence}\n\nInput: {claim} True or False?\nOutput:"""

    def prepare_messages(self, verification_input: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        messages = []
        for d in verification_input:
            evidence = "\n\n".join([
                f"Title: {passage['title']} Text: {passage['text']}" for passage in d['evidence']
            ])
            formatted_input = self.format_input(evidence, d['claim'])
            messages.append([
                {"role": "user", "content": formatted_input}
            ])
        return messages
