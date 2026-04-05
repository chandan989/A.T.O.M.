# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
Pydantic models defining the OpenEnv interfaces for ATOM.
"""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from openenv.core.env_server.types import Action, Observation

class AtomAction(Action):
    """
    Action space for ATOM.
    """
    action_type: str = Field(..., description="One of: add_fragment, remove_group, mutate_atom, get_valid_sites, finish")
    fragment_name: Optional[str] = Field(None, description="Name of the fragment to attach (from curated library). Required for add_fragment")
    site_id: Optional[int] = Field(None, description="Target attachment site (returned by get_valid_sites). Required for add_fragment and mutate_atom in Mode 2")
    r_group: Optional[str] = Field(None, description="R-group label (R1, R2, R3) for scaffold-based attachment. Used in Mode 1")
    target_atom_symbol: Optional[str] = Field(None, description="Symbol of the new atom (e.g., 'N', 'O', 'C'). Required for mutate_atom")

class AtomObservation(Observation):
    """
    Observation space for ATOM.
    """
    current_smiles: str = Field(..., description="SMILES representation of the current molecule")
    current_properties: Dict[str, float] = Field(..., description="Computed properties: QED, LogP, SA_Score, MW")
    target_profile: Dict[str, Any] = Field(..., description="Target Product Profile ranges")
    message: str = Field(..., description="Human-readable feedback from environment")
    valid_sites: Optional[List[Dict[str, Any]]] = Field(None, description="List of valid sites from get_valid_sites")
    step_number: int = Field(..., description="Current step within episode")
    max_steps: int = Field(..., description="Maximum steps allowed")
    done: bool = Field(..., description="Whether the episode is done")
    trajectory_summary: Dict[str, Any] = Field(..., description="Running statistics about optimization trajectory")
    reward: float = Field(..., description="Reward for the current step/trajectory")
