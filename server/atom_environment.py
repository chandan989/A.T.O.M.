# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
ATOM Environment Implementation.
"""

from uuid import uuid4
from typing import Optional, Dict, Any, List

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from rdkit import Chem

from models import AtomAction, AtomObservation
from server.chemistry.engine import compute_properties, apply_fragment_mode1, apply_fragment_mode2, remove_group, mutate_atom
from server.chemistry.state_mapper import StateMapper
from server.chemistry.fragments import FRAGMENTS
from server.rubrics.evaluator import TASKS, RubricEngine
from server.rubrics.trajectory import TrajectoryTracker

class AtomEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self, task_id: int = 1):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.task_id = task_id

        self.task = TASKS.get(task_id, TASKS[1])
        self.state_mapper = StateMapper()
        self.rubric_engine = RubricEngine(self.task)
        self.tracker = TrajectoryTracker()

        self.current_mol: Optional[Chem.Mol] = None
        self.current_smiles: str = ""
        self.current_properties: Dict[str, float] = {}

    def reset(self, task_id: Optional[int] = None, custom_tpp: Optional[Dict[str, Any]] = None, custom_scaffold: Optional[str] = None, max_steps: Optional[int] = None) -> AtomObservation:
        """Reset the environment. Allows for custom dynamic tasks."""
        if custom_tpp is not None and custom_scaffold is not None:
            # Dynamic Task
            self.task_id = 999
            from server.rubrics.evaluator import TaskDefinition
            self.task = TaskDefinition(
                task_id=999,
                difficulty="Dynamic",
                starting_scaffold=custom_scaffold,
                max_steps=max_steps if max_steps else 15,
                tpp=custom_tpp
            )
            self.rubric_engine = RubricEngine(self.task)
        elif task_id is not None and task_id in TASKS:
            self.task_id = task_id
            self.task = TASKS[self.task_id]
            self.rubric_engine = RubricEngine(self.task)

        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.tracker = TrajectoryTracker()

        self.current_mol = Chem.MolFromSmiles(self.task.starting_scaffold)
        self.current_smiles = Chem.MolToSmiles(self.current_mol)
        self.current_properties = compute_properties(self.current_mol)

        # Log initial state
        self.tracker.add_step(
            action_dict={"action_type": "reset"},
            properties=self.current_properties,
            is_valid=True
        )

        return AtomObservation(
            current_smiles=self.current_smiles,
            current_properties=self.current_properties,
            target_profile=self.task.tpp,
            message=f"Environment reset. Task {self.task_id}: {self.task.difficulty}. Starting scaffold loaded.",
            valid_sites=None,
            step_number=self._state.step_count,
            max_steps=self.task.max_steps,
            done=False,
            trajectory_summary=self.tracker.get_summary(),
            reward=0.0
        )

    def step(self, action: AtomAction) -> AtomObservation:
        self._state.step_count += 1

        message = ""
        valid_sites = None
        done = False
        reward = 0.0

        if self._state.step_count >= self.task.max_steps and action.action_type != "finish":
            # Auto-finish if max steps reached
            done = True
            reward = self.rubric_engine.score_trajectory(self.tracker.history, self.current_mol)
            message = "Max steps reached. Auto-finishing."

        elif action.action_type == "finish":
            done = True
            reward = self.rubric_engine.score_trajectory(self.tracker.history, self.current_mol)
            message = "Optimization finished by agent."

        elif action.action_type == "get_valid_sites":
            valid_sites = self.state_mapper.get_valid_sites(self.current_mol)
            message = f"Found {len(valid_sites)} valid attachment sites."

        elif action.action_type == "add_fragment":
            if action.fragment_name not in FRAGMENTS:
                message = f"Invalid action: Fragment {action.fragment_name} not found in library."
                self.tracker.add_step(action.model_dump(), self.current_properties, False)
            else:
                fragment_smiles = FRAGMENTS[action.fragment_name].smiles

                new_mol = None
                if action.site_id is not None:
                    # Mode 2
                    atom_idx = self.state_mapper.get_atom_idx(action.site_id)
                    if atom_idx >= 0:
                        new_mol = apply_fragment_mode2(self.current_mol, fragment_smiles, atom_idx)
                        if not new_mol:
                            message = f"Invalid action: Cannot attach {action.fragment_name} at site {action.site_id}. Valency or chemical rule violated."
                    else:
                        message = f"Invalid action: Site {action.site_id} is not valid."
                elif action.r_group is not None:
                    # Mode 1
                    new_mol = apply_fragment_mode1(self.current_mol, fragment_smiles, action.r_group)
                    if not new_mol:
                        message = f"Invalid action: Cannot attach {action.fragment_name} at {action.r_group}."
                else:
                    message = "Invalid action: Must specify either site_id or r_group for add_fragment."

                if new_mol:
                    self.current_mol = new_mol
                    self.current_smiles = Chem.MolToSmiles(self.current_mol)
                    self.current_properties = compute_properties(self.current_mol)
                    message = f"Modification successful. Fragment {action.fragment_name} added."
                    self.tracker.add_step(action.model_dump(), self.current_properties, True)
                else:
                    self.tracker.add_step(action.model_dump(), self.current_properties, False)

        elif action.action_type == "mutate_atom":
            if action.site_id is not None and action.target_atom_symbol is not None:
                atom_idx = self.state_mapper.get_atom_idx(action.site_id)
                if atom_idx >= 0:
                    new_mol = mutate_atom(self.current_mol, atom_idx, action.target_atom_symbol)
                    if new_mol:
                        self.current_mol = new_mol
                        self.current_smiles = Chem.MolToSmiles(self.current_mol)
                        self.current_properties = compute_properties(self.current_mol)
                        message = f"Modification successful. Atom mutated to {action.target_atom_symbol}."
                        self.tracker.add_step(action.model_dump(), self.current_properties, True)
                    else:
                        message = f"Invalid action: Could not mutate atom at site {action.site_id}."
                        self.tracker.add_step(action.model_dump(), self.current_properties, False)
                else:
                    message = f"Invalid action: Site {action.site_id} is not valid."
                    self.tracker.add_step(action.model_dump(), self.current_properties, False)
            else:
                message = "Invalid action: Must specify site_id and target_atom_symbol for mutate_atom."
                self.tracker.add_step(action.model_dump(), self.current_properties, False)

        elif action.action_type == "remove_group":
            if action.site_id is not None:
                atom_idx = self.state_mapper.get_atom_idx(action.site_id)
                if atom_idx >= 0:
                    new_mol = remove_group(self.current_mol, atom_idx)
                    if new_mol:
                        self.current_mol = new_mol
                        self.current_smiles = Chem.MolToSmiles(self.current_mol)
                        self.current_properties = compute_properties(self.current_mol)
                        message = f"Modification successful. Group at site {action.site_id} removed."
                        self.tracker.add_step(action.model_dump(), self.current_properties, True)
                    else:
                        message = f"Invalid action: Could not remove group at site {action.site_id}."
                        self.tracker.add_step(action.model_dump(), self.current_properties, False)
                else:
                    message = f"Invalid action: Site {action.site_id} is not valid."
                    self.tracker.add_step(action.model_dump(), self.current_properties, False)
            else:
                message = "Invalid action: Must specify site_id for remove_group."
                self.tracker.add_step(action.model_dump(), self.current_properties, False)
        else:
            message = f"Invalid action: Unknown action_type '{action.action_type}'"
            self.tracker.add_step(action.model_dump(), self.current_properties, False)

        return AtomObservation(
            current_smiles=self.current_smiles,
            current_properties=self.current_properties,
            target_profile=self.task.tpp,
            message=message,
            valid_sites=valid_sites,
            step_number=self._state.step_count,
            max_steps=self.task.max_steps,
            done=done,
            trajectory_summary=self.tracker.get_summary(),
            reward=reward
        )

    @property
    def state(self) -> State:
        return self._state
