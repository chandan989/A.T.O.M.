# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
Tests for the Grading / Rubric Engine.
Validates determinism, score ranges, trajectory quality evaluation,
and proper task definitions.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Skip entire module if rdkit is not installed (e.g., running outside Docker)
pytest.importorskip("rdkit", reason="RDKit not installed — run tests inside Docker")

from rdkit import Chem
from server.chemistry.engine import compute_properties
from server.rubrics.evaluator import (
    TASKS,
    TaskDefinition,
    RubricEngine,
    gaussian_proximity,
    evaluate_target_adherence,
)
from server.rubrics.trajectory import TrajectoryTracker


# ── Task Definitions ──────────────────────────────────────────


class TestTaskDefinitions:
    """Tests for the task definition registry."""

    def test_four_tasks_exist(self):
        """There must be exactly 4 tasks defined."""
        assert len(TASKS) == 4

    def test_task_ids(self):
        """Task IDs must be 1, 2, 3, 4."""
        assert set(TASKS.keys()) == {1, 2, 3, 4}

    def test_difficulty_progression(self):
        """Tasks should escalate in difficulty."""
        difficulties = [TASKS[i].difficulty for i in [1, 2, 3, 4]]
        assert difficulties == ["Easy", "Medium", "Hard", "Extreme"]

    def test_max_steps_increase(self):
        """Harder tasks should allow more steps."""
        steps = [TASKS[i].max_steps for i in [1, 2, 3, 4]]
        assert steps == sorted(steps), "Max steps should increase with difficulty"

    def test_tpp_complexity_increases(self):
        """Harder tasks should have more TPP properties."""
        tpp_sizes = [len(TASKS[i].tpp) for i in [1, 2, 3, 4]]
        assert tpp_sizes == sorted(tpp_sizes), "TPP complexity should increase"

    def test_starting_scaffolds_valid(self):
        """All starting scaffolds must be valid SMILES."""
        for task_id, task in TASKS.items():
            mol = Chem.MolFromSmiles(task.starting_scaffold)
            assert mol is not None, f"Task {task_id} has invalid scaffold: {task.starting_scaffold}"

    def test_tpp_ranges_valid(self):
        """All TPP ranges must be [min, max] with min <= max."""
        for task_id, task in TASKS.items():
            for prop, rng in task.tpp.items():
                assert len(rng) == 2, f"Task {task_id} TPP {prop} must have 2 values"
                assert rng[0] <= rng[1], f"Task {task_id} TPP {prop} min > max: {rng}"


# ── Gaussian Proximity ────────────────────────────────────────


class TestGaussianProximity:
    """Tests for the gaussian proximity scoring function."""

    def test_in_range_returns_1(self):
        """A value inside the target range should score 1.0."""
        assert gaussian_proximity(2.5, 2.0, 3.0) == 1.0
        assert gaussian_proximity(2.0, 2.0, 3.0) == 1.0
        assert gaussian_proximity(3.0, 2.0, 3.0) == 1.0

    def test_outside_range_less_than_1(self):
        """A value outside the target range should score < 1.0."""
        score = gaussian_proximity(5.0, 2.0, 3.0)
        assert 0.0 < score < 1.0

    def test_far_away_approaches_zero(self):
        """A value very far from range should approach 0."""
        score = gaussian_proximity(100.0, 2.0, 3.0, sigma=1.0)
        assert score < 0.01

    def test_symmetry(self):
        """Scores should be symmetric around the target range."""
        score_below = gaussian_proximity(1.0, 2.0, 3.0, sigma=1.0)
        score_above = gaussian_proximity(4.0, 2.0, 3.0, sigma=1.0)
        assert abs(score_below - score_above) < 1e-6


# ── Target Adherence ──────────────────────────────────────────


class TestTargetAdherence:
    """Tests for target adherence evaluation."""

    def test_perfect_adherence(self):
        """Properties exactly within all target ranges should score 1.0."""
        props = {"LogP": 2.7, "QED": 0.8}
        tpp = {"LogP": [2.5, 3.0], "QED": [0.6, 1.0]}
        score = evaluate_target_adherence(props, tpp)
        assert score == 1.0

    def test_zero_properties(self):
        """Empty properties should return 0.0."""
        score = evaluate_target_adherence({}, {"LogP": [2.0, 3.0]})
        assert score == 0.0

    def test_partial_adherence(self):
        """One property in range, one out, should be between 0 and 1."""
        props = {"LogP": 2.7, "QED": 0.1}  # QED out of range
        tpp = {"LogP": [2.5, 3.0], "QED": [0.6, 1.0]}
        score = evaluate_target_adherence(props, tpp)
        assert 0.0 < score < 1.0


# ── Rubric Engine ─────────────────────────────────────────────


class TestRubricEngine:
    """Tests for the trajectory scoring rubric engine."""

    def _make_trajectory(self, smiles_list, task_id=1):
        """Helper: create a simulated trajectory."""
        trajectory = []
        for smi in smiles_list:
            mol = Chem.MolFromSmiles(smi)
            props = compute_properties(mol)
            trajectory.append({
                "action": {"action_type": "add_fragment", "fragment_name": "Methyl"},
                "properties": props,
                "is_valid": True,
            })
        return trajectory

    def test_score_in_range(self):
        """Rubric score must always be in [0.0, 1.0]."""
        task = TASKS[1]
        engine = RubricEngine(task)

        trajectory = self._make_trajectory(["c1ccccc1", "Cc1ccccc1"])
        mol = Chem.MolFromSmiles("Cc1ccccc1")
        score = engine.score_trajectory(trajectory, mol)

        assert 0.0 <= score <= 1.0

    def test_empty_trajectory_returns_zero(self):
        """An empty trajectory should score 0.0."""
        task = TASKS[1]
        engine = RubricEngine(task)
        score = engine.score_trajectory([], None)
        assert score == 0.0

    def test_score_determinism(self):
        """Same trajectory must produce identical scores."""
        task = TASKS[1]
        engine = RubricEngine(task)

        trajectory = self._make_trajectory(["c1ccccc1", "Cc1ccccc1", "CCc1ccccc1"])
        mol = Chem.MolFromSmiles("CCc1ccccc1")

        score1 = engine.score_trajectory(trajectory, mol)
        score2 = engine.score_trajectory(trajectory, mol)
        assert score1 == score2

    def test_better_trajectory_scores_higher(self):
        """A trajectory that hits the target should score higher than one that doesn't."""
        task = TASKS[1]  # Target: LogP [2.5, 3.0]
        engine = RubricEngine(task)

        # Good trajectory: benzene → toluene (LogP ~2.7)
        good_traj = self._make_trajectory(["c1ccccc1", "Cc1ccccc1"])
        good_mol = Chem.MolFromSmiles("Cc1ccccc1")

        # Bad trajectory: benzene → methane (LogP ~0.56, far from target)
        bad_traj = self._make_trajectory(["c1ccccc1", "C"])
        bad_mol = Chem.MolFromSmiles("C")

        good_score = engine.score_trajectory(good_traj, good_mol)
        bad_score = engine.score_trajectory(bad_traj, bad_mol)

        assert good_score > bad_score

    def test_all_tasks_score_range(self):
        """Scoring a basic trajectory on each task should stay in [0, 1]."""
        for task_id, task in TASKS.items():
            engine = RubricEngine(task)
            mol = Chem.MolFromSmiles(task.starting_scaffold)
            trajectory = [{
                "action": {"action_type": "reset"},
                "properties": compute_properties(mol),
                "is_valid": True,
            }]
            score = engine.score_trajectory(trajectory, mol)
            assert 0.0 <= score <= 1.0, f"Task {task_id} score out of range: {score}"

    def test_score_never_constant(self):
        """Different trajectories should produce different scores (not a fixed value)."""
        task = TASKS[2]
        engine = RubricEngine(task)

        traj_short = self._make_trajectory(["Cc1ccccc1"])
        mol_short = Chem.MolFromSmiles("Cc1ccccc1")

        traj_long = self._make_trajectory(["Cc1ccccc1", "CCc1ccccc1", "CCCc1ccccc1"])
        mol_long = Chem.MolFromSmiles("CCCc1ccccc1")

        score_short = engine.score_trajectory(traj_short, mol_short)
        score_long = engine.score_trajectory(traj_long, mol_long)

        # They should differ (not the same constant)
        assert score_short != score_long


# ── Trajectory Tracker ────────────────────────────────────────


class TestTrajectoryTracker:
    """Tests for the trajectory tracking utility."""

    def test_empty_summary(self):
        tracker = TrajectoryTracker()
        assert tracker.get_summary() == {}

    def test_add_step(self):
        tracker = TrajectoryTracker()
        tracker.add_step(
            {"action_type": "add_fragment", "fragment_name": "Methyl"},
            {"QED": 0.5, "LogP": 1.5},
            True,
        )
        assert len(tracker.history) == 1

    def test_summary_counts(self):
        tracker = TrajectoryTracker()
        tracker.add_step({"action_type": "add_fragment", "fragment_name": "Methyl"}, {"QED": 0.5}, True)
        tracker.add_step({"action_type": "add_fragment", "fragment_name": "Fluorine"}, {"QED": 0.6}, True)
        tracker.add_step({"action_type": "add_fragment", "fragment_name": "Methyl"}, {"QED": 0.4}, False)

        summary = tracker.get_summary()
        assert summary["steps"] == 3
        assert summary["valid_steps"] == 2
        assert set(summary["fragments_used"]) == {"Methyl", "Fluorine"}
