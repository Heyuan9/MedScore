"""
Pydantic schemas for MedScore configuration validation, using discriminated unions.
"""
from typing import Literal, Optional, Union, Dict
from pydantic import BaseModel, Field, FilePath, SecretStr


# --- Base Models for Shared Parameters ---

class DecomposerSharedConfig(BaseModel):
    """Shared configuration for all decomposer models."""
    model_name: str = "gpt-4o-mini"
    server_path: str = "https://api.openai.com/v1"
    api_key: Optional[SecretStr] = None
    random_state: int = 42
    batch_size: int = 32


class VerifierSharedConfig(BaseModel):
    """Shared configuration for all verifier models."""
    model_name: str = "gpt-4o-mini"
    server_path: str = "https://api.openai.com/v1"
    api_key: Optional[SecretStr] = None
    random_state: int = 42
    batch_size: int = 32


# --- Decomposer Models ---
class MedScoreDecomposerConfig(DecomposerSharedConfig):
    type: Literal["medscore"] = "medscore"


class FactScoreDecomposerConfig(DecomposerSharedConfig):
    type: Literal["factscore"] = "factscore"


class DnDScoreDecomposerConfig(DecomposerSharedConfig):
    type: Literal["dndscore"] = "dndscore"


class CustomDecomposerConfig(DecomposerSharedConfig):
    type: Literal["custom"] = "custom"
    prompt_path: FilePath


# --- Verifier Models ---
class InternalVerifierConfig(VerifierSharedConfig):
    type: Literal["internal"] = "internal"


class ProvidedEvidenceVerifierConfig(VerifierSharedConfig):
    type: Literal["provided"] = "provided"
    provided_evidence_path: FilePath


class MedRAGVerifierConfig(VerifierSharedConfig):
    type: Literal["medrag"] = "medrag"
    retriever_name: str = "MedCPT"
    corpus_name: str = "StatPearls"
    db_dir: Optional[str] = None
    HNSW: bool = False
    cache: bool = False
    n_returned_docs: int = 5


# --- Create the Discriminated Unions ---

DecomposerConfig = Union[
    MedScoreDecomposerConfig,
    FactScoreDecomposerConfig,
    DnDScoreDecomposerConfig,
    CustomDecomposerConfig,
]

VerifierConfig = Union[
    InternalVerifierConfig,
    ProvidedEvidenceVerifierConfig,
    MedRAGVerifierConfig,
]


# --- Top-Level Configuration Model ---

class MedScoreConfig(BaseModel):
    """The main configuration model for the MedScore application."""
    # Pydantic will automatically use the 'type' field to select the correct model
    # from the Union defined above.
    decomposer: DecomposerConfig = Field(..., discriminator="type")
    verifier: VerifierConfig = Field(..., discriminator="type")

    response_key: str = "response"
    # If True, MedScore will expect each input record to include a pre-senticized
    # list of sentence objects under the key "sentences" and will use those
    # instead of running its internal sentence-splitting (senticizing) step.
    presenticized: bool = False
