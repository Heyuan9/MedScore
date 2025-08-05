"""
Component builder for MedScore, using the 'registrable' package.
"""
from typing import Any
from pydantic import BaseModel, SecretStr

from .decomposer import Decomposer
from .verifier import Verifier


def build_component(config: BaseModel, component_type: str) -> Any:
    """
    Builds a decomposer or verifier using its Registrable base class.

    Args:
        config: A Pydantic model instance from the config schema.
        component_type: The type of component to build ('decomposer' or 'verifier').

    Returns:
        An instantiated component object.
    """
    component_name = config.type

    # Choose the correct base class (Decomposer or Verifier)
    if component_type == "decomposer":
        BaseClass = Decomposer
    elif component_type == "verifier":
        BaseClass = Verifier
    else:
        raise ValueError(f"Unknown component type: {component_type}")

    # Use .by_name() from the registrable package to get the correct subclass
    try:
        ComponentClass = BaseClass.by_name(component_name)
    except KeyError:
        raise ValueError(
            f"'{component_name}' is not a registered {component_type}. "
            f"Available: {BaseClass.list_available()}"
        )

    # Convert the Pydantic model to a dictionary for instantiation.
    # We also need to unwrap the SecretStr for the API key.
    init_params = config.model_dump()
    if 'api_key' in init_params and isinstance(init_params['api_key'], SecretStr):
        init_params['api_key'] = init_params['api_key'].get_secret_value()

    return ComponentClass(**init_params)
