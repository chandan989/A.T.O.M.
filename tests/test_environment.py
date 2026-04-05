# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
Tests for the ATOM OpenEnv Environment.
Validates the full OpenEnv API contract: reset(), step(), state().
Ensures episode lifecycle, action handling, and observation schema.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Skip entire module if dependencies are not installed (e.g., running outside Docker)
pytest.importorskip("rdkit", reason="RDKit not installed — run tests inside Docker")
pytest.importorskip("openenv", reason="openenv not installed — run tests inside Docker")

from server.atom_environment import AtomEnvironment
from models import AtomAction, AtomObservation


# ── Environment Initialization ────────────────────────────────


class TestEnvironmentInit:
    """Tests for environment construction."""

    def test_creates_without_error(self):
        env = AtomEnvironment(task_id=1)
        assert env is not None

    def test_default_task_id(self):
        env = AtomEnvironment()
        assert env.task_id == 1


# ── Reset ─────────────────────────────────────────────────────


class TestReset:
    """Tests for the reset() API."""

    def test_reset_returns_observation(self):
        env = AtomEnvironment(task_id=1)
        obs = env.reset()
        assert isinstance(obs, AtomObservation)

    def test_reset_observation_fields(self):
        """Observation must contain all required fields."""
        env = AtomEnvironment(task_id=1)
        obs = env.reset()

        assert obs.current_smiles != ""
        assert isinstance(obs.current_properties, dict)
        assert "QED" in obs.current_properties
        assert "LogP" in obs.current_properties
        assert isinstance(obs.target_profile, dict)
        assert obs.step_number == 0
        assert obs.max_steps > 0
        assert obs.done is False
        assert obs.reward == 0.0
        assert isinstance(obs.message, str)

    def test_reset_uses_correct_scaffold(self):
        """Reset should load the task's starting scaffold."""
        env = AtomEnvironment(task_id=1)
        obs = env.reset()
        # Task 1 scaffold is benzene "c1ccccc1"
        assert obs.current_smiles != ""

    def test_reset_with_different_task(self):
        """Resetting with a different task_id should change the observation."""
        env = AtomEnvironment(task_id=1)
        obs1 = env.reset()

        obs2 = env.reset(task_id=3)
        assert obs1.current_smiles != obs2.current_smiles

    def test_reset_clears_state(self):
        """Reset should clear step count and trajectory."""
        env = AtomEnvironment(task_id=1)
        env.reset()

        # Take a step
        env.step(AtomAction(action_type="get_valid_sites"))
        assert env.state.step_count == 1

        # Reset should clear
        env.reset()
        assert env.state.step_count == 0

    def test_reset_all_tasks(self):
        """Every defined task should be resettable."""
        for task_id in [1, 2, 3, 4]:
            env = AtomEnvironment(task_id=task_id)
            obs = env.reset()
            assert obs.done is False
            assert obs.step_number == 0

    def test_reset_dynamic_task(self):
        """Custom TPP + scaffold should create a dynamic task."""
        env = AtomEnvironment(task_id=1)
        obs = env.reset(
            custom_tpp={"LogP": [1.0, 3.0]},
            custom_scaffold="CCO",
            max_steps=10,
        )
        assert obs.current_smiles != ""
        assert obs.max_steps == 10
        assert "LogP" in obs.target_profile


# ── Step — Get Valid Sites ────────────────────────────────────


class TestStepGetValidSites:
    """Tests for the get_valid_sites action."""

    def test_get_valid_sites(self):
        env = AtomEnvironment(task_id=1)
        env.reset()

        action = AtomAction(action_type="get_valid_sites")
        obs = env.step(action)

        assert isinstance(obs, AtomObservation)
        assert obs.valid_sites is not None
        assert len(obs.valid_sites) > 0

    def test_valid_sites_have_structure(self):
        """Each site should have site_id and description."""
        env = AtomEnvironment(task_id=1)
        env.reset()

        obs = env.step(AtomAction(action_type="get_valid_sites"))

        for site in obs.valid_sites:
            assert "site_id" in site
            assert "description" in site
            assert isinstance(site["site_id"], int)
            assert isinstance(site["description"], str)

    def test_get_valid_sites_does_not_change_molecule(self):
        """get_valid_sites is a read-only query."""
        env = AtomEnvironment(task_id=1)
        obs_before = env.reset()

        env.step(AtomAction(action_type="get_valid_sites"))

        # SMILES should be unchanged
        assert env.current_smiles == obs_before.current_smiles


# ── Step — Add Fragment ───────────────────────────────────────


class TestStepAddFragment:
    """Tests for the add_fragment action."""

    def test_add_fragment_mode2(self):
        """Adding a fragment via site_id should change the molecule."""
        env = AtomEnvironment(task_id=1)
        env.reset()

        # Get valid sites first
        obs = env.step(AtomAction(action_type="get_valid_sites"))
        site_id = obs.valid_sites[0]["site_id"]

        # Add methyl fragment
        smiles_before = obs.current_smiles
        obs2 = env.step(AtomAction(
            action_type="add_fragment",
            fragment_name="Methyl",
            site_id=site_id,
        ))

        assert obs2.current_smiles != smiles_before
        assert obs2.step_number == 2  # get_valid_sites was step 1

    def test_invalid_fragment_name(self):
        """Using a non-existent fragment name should return an error message."""
        env = AtomEnvironment(task_id=1)
        env.reset()

        obs = env.step(AtomAction(
            action_type="add_fragment",
            fragment_name="NonExistentFragment",
            site_id=0,
        ))

        assert "invalid" in obs.message.lower() or "not found" in obs.message.lower()

    def test_step_increments(self):
        """Each step should increment step_number."""
        env = AtomEnvironment(task_id=1)
        env.reset()

        obs1 = env.step(AtomAction(action_type="get_valid_sites"))
        assert obs1.step_number == 1

        obs2 = env.step(AtomAction(action_type="get_valid_sites"))
        assert obs2.step_number == 2


# ── Step — Finish ─────────────────────────────────────────────


class TestStepFinish:
    """Tests for the finish action."""

    def test_finish_ends_episode(self):
        env = AtomEnvironment(task_id=1)
        env.reset()

        obs = env.step(AtomAction(action_type="finish"))
        assert obs.done is True

    def test_finish_returns_reward(self):
        """Finishing should compute a trajectory reward."""
        env = AtomEnvironment(task_id=1)
        env.reset()

        obs = env.step(AtomAction(action_type="finish"))
        assert isinstance(obs.reward, float)
        assert 0.0 <= obs.reward <= 1.0

    def test_finish_after_optimization(self):
        """Finish after some modifications should produce a score."""
        env = AtomEnvironment(task_id=1)
        env.reset()

        # Get sites, add a fragment, then finish
        obs = env.step(AtomAction(action_type="get_valid_sites"))
        if obs.valid_sites:
            env.step(AtomAction(
                action_type="add_fragment",
                fragment_name="Methyl",
                site_id=obs.valid_sites[0]["site_id"],
            ))

        final = env.step(AtomAction(action_type="finish"))
        assert final.done is True
        assert 0.0 <= final.reward <= 1.0


# ── Step — Max Steps Auto-Finish ──────────────────────────────


class TestMaxSteps:
    """Tests for automatic episode termination at max_steps."""

    def test_auto_finish_at_max_steps(self):
        """Episode should auto-finish when reaching max_steps."""
        env = AtomEnvironment(task_id=1)  # max_steps=5
        env.reset()

        obs = None
        for i in range(10):  # More than max_steps
            obs = env.step(AtomAction(action_type="get_valid_sites"))
            if obs.done:
                break

        assert obs.done is True


# ── State ─────────────────────────────────────────────────────


class TestState:
    """Tests for the state property."""

    def test_state_has_episode_id(self):
        env = AtomEnvironment(task_id=1)
        env.reset()
        assert env.state.episode_id is not None
        assert len(env.state.episode_id) > 0

    def test_state_step_count(self):
        env = AtomEnvironment(task_id=1)
        env.reset()
        assert env.state.step_count == 0

        env.step(AtomAction(action_type="get_valid_sites"))
        assert env.state.step_count == 1

    def test_new_episode_id_on_reset(self):
        """Each reset should produce a new episode_id."""
        env = AtomEnvironment(task_id=1)
        env.reset()
        id1 = env.state.episode_id

        env.reset()
        id2 = env.state.episode_id

        assert id1 != id2


# ── Observation Schema ────────────────────────────────────────


class TestObservationSchema:
    """Tests that the observation matches the Pydantic schema."""

    def test_observation_is_pydantic(self):
        env = AtomEnvironment(task_id=1)
        obs = env.reset()
        assert isinstance(obs, AtomObservation)

    def test_observation_serializable(self):
        """Observation must be JSON-serializable (for API transport)."""
        env = AtomEnvironment(task_id=1)
        obs = env.reset()
        data = obs.model_dump()

        assert isinstance(data, dict)
        assert "current_smiles" in data
        assert "current_properties" in data
        assert "target_profile" in data
        assert "done" in data
        assert "reward" in data

    def test_trajectory_summary_in_observation(self):
        """Observation should contain trajectory_summary."""
        env = AtomEnvironment(task_id=1)
        obs = env.reset()
        assert isinstance(obs.trajectory_summary, dict)
