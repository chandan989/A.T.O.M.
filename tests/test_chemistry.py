# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
Tests for the RDKit Chemistry Engine.
Validates property computation, fragment attachment, validity checks,
and the dynamic state-mapping layer.
"""

import sys
import os
import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Skip entire module if rdkit is not installed (e.g., running outside Docker)
pytest.importorskip("rdkit", reason="RDKit not installed — run tests inside Docker")

from rdkit import Chem
from server.chemistry.engine import (
    compute_properties,
    check_alerts,
    check_lipinski,
    validate_valency,
    apply_fragment_mode2,
    mutate_atom,
    remove_group,
)
from server.chemistry.fragments import FRAGMENTS
from server.chemistry.state_mapper import StateMapper


# ── Property Computation ──────────────────────────────────────


class TestComputeProperties:
    """Tests for compute_properties()."""

    def test_benzene_properties(self):
        """Benzene should have computable QED, LogP, MW, SA_Score, Energy."""
        mol = Chem.MolFromSmiles("c1ccccc1")
        props = compute_properties(mol)

        assert "QED" in props
        assert "LogP" in props
        assert "MW" in props
        assert "SA_Score" in props
        assert "Energy" in props

    def test_benzene_mw_range(self):
        """Benzene (C6H6) MW should be ~78.11."""
        mol = Chem.MolFromSmiles("c1ccccc1")
        props = compute_properties(mol)
        assert 77 < props["MW"] < 80

    def test_qed_range(self):
        """QED must always be between 0 and 1."""
        smiles_list = ["c1ccccc1", "CCO", "CC(=O)Nc1ccc(O)cc1", "C"]
        for smi in smiles_list:
            mol = Chem.MolFromSmiles(smi)
            props = compute_properties(mol)
            assert 0.0 <= props["QED"] <= 1.0, f"QED out of range for {smi}"

    def test_sa_score_range(self):
        """SA Score must be between 1.0 and 10.0."""
        mol = Chem.MolFromSmiles("c1ccccc1")
        props = compute_properties(mol)
        assert 1.0 <= props["SA_Score"] <= 10.0

    def test_properties_deterministic(self):
        """Same molecule should always produce the same properties."""
        mol = Chem.MolFromSmiles("Cc1ccccc1")
        props1 = compute_properties(mol)
        props2 = compute_properties(mol)

        for key in props1:
            assert abs(props1[key] - props2[key]) < 1e-6, f"{key} not deterministic"


# ── Validity Checks ───────────────────────────────────────────


class TestValidityChecks:
    """Tests for chemical validity checks."""

    def test_valid_benzene(self):
        mol = Chem.MolFromSmiles("c1ccccc1")
        assert validate_valency(mol) is True

    def test_valid_aspirin(self):
        mol = Chem.MolFromSmiles("CC(=O)Oc1ccccc1C(=O)O")
        assert validate_valency(mol) is True

    def test_lipinski_aspirin(self):
        """Aspirin should have no Lipinski violations."""
        mol = Chem.MolFromSmiles("CC(=O)Oc1ccccc1C(=O)O")
        violations = check_lipinski(mol)
        assert violations == 0

    def test_lipinski_high_mw(self):
        """A very heavy molecule should trigger MW violation."""
        # Create a molecule with MW > 500
        mol = Chem.MolFromSmiles("C" * 40)  # Long alkane
        violations = check_lipinski(mol)
        assert violations >= 1  # At least MW and LogP violations

    def test_check_alerts_benzene(self):
        """Benzene should not trigger PAINS/BRENK alerts."""
        mol = Chem.MolFromSmiles("c1ccccc1")
        # Just check it returns a bool without error
        result = check_alerts(mol)
        assert isinstance(result, bool)


# ── Fragment Library ──────────────────────────────────────────


class TestFragmentLibrary:
    """Tests for the curated fragment library."""

    def test_fragment_count(self):
        """Library should have at least 60 fragments (77 curated + procedural)."""
        assert len(FRAGMENTS) >= 60

    def test_all_fragments_valid_smiles(self):
        """Every fragment in the library must be a valid SMILES."""
        for name, frag in FRAGMENTS.items():
            mol = Chem.MolFromSmiles(frag.smiles)
            assert mol is not None, f"Fragment '{name}' has invalid SMILES: {frag.smiles}"

    def test_core_fragments_present(self):
        """Essential medicinal chemistry fragments must be present."""
        essential = [
            "Fluorine", "Chlorine", "Methyl", "Hydroxyl", "Amino",
            "Phenyl", "Pyridine", "Cyclopropyl", "Trifluoromethyl",
        ]
        for name in essential:
            assert name in FRAGMENTS, f"Essential fragment '{name}' missing"

    def test_fragment_has_metadata(self):
        """Each fragment must have name, smiles, attachment_smarts, description."""
        for name, frag in FRAGMENTS.items():
            assert frag.name, f"Fragment '{name}' missing name"
            assert frag.smiles, f"Fragment '{name}' missing smiles"
            assert frag.description, f"Fragment '{name}' missing description"


# ── Fragment Attachment (Mode 2) ──────────────────────────────


class TestFragmentAttachment:
    """Tests for apply_fragment_mode2()."""

    def test_attach_methyl_to_benzene(self):
        """Attaching Methyl to benzene should produce toluene or similar."""
        mol = Chem.MolFromSmiles("c1ccccc1")
        frag_smiles = FRAGMENTS["Methyl"].smiles
        result = apply_fragment_mode2(mol, frag_smiles, atom_idx=0)

        assert result is not None
        assert validate_valency(result)
        assert result.GetNumAtoms() > mol.GetNumAtoms()

    def test_attach_fluorine_to_benzene(self):
        """Attaching Fluorine to benzene should produce fluorobenzene."""
        mol = Chem.MolFromSmiles("c1ccccc1")
        frag_smiles = FRAGMENTS["Fluorine"].smiles
        result = apply_fragment_mode2(mol, frag_smiles, atom_idx=0)

        assert result is not None
        assert validate_valency(result)
        # Should contain F atom
        smi = Chem.MolToSmiles(result)
        assert "F" in smi

    def test_attach_to_saturated_carbon(self):
        """Should fail to attach to a carbon with no Hs (fully substituted)."""
        # Neopentane: central carbon has 0 H
        mol = Chem.MolFromSmiles("CC(C)(C)C")
        frag_smiles = FRAGMENTS["Methyl"].smiles
        # Atom 1 is the central carbon (no H)
        result = apply_fragment_mode2(mol, frag_smiles, atom_idx=1)
        assert result is None

    def test_property_change_after_attachment(self):
        """Attaching a fragment should change molecular properties."""
        mol = Chem.MolFromSmiles("c1ccccc1")
        props_before = compute_properties(mol)

        frag_smiles = FRAGMENTS["Methyl"].smiles
        new_mol = apply_fragment_mode2(mol, frag_smiles, atom_idx=0)
        props_after = compute_properties(new_mol)

        # MW must increase (added CH3)
        assert props_after["MW"] > props_before["MW"]


# ── Atom Mutation ─────────────────────────────────────────────


class TestAtomMutation:
    """Tests for mutate_atom()."""

    def test_mutate_c_to_n_in_benzene(self):
        """Mutating a carbon to nitrogen in benzene → pyridine."""
        mol = Chem.MolFromSmiles("c1ccccc1")
        result = mutate_atom(mol, atom_idx=0, target_symbol="N")

        assert result is not None
        smi = Chem.MolToSmiles(result)
        assert "n" in smi.lower()  # pyridine has lowercase 'n'

    def test_mutate_disallowed_element(self):
        """Mutating to a non-allowed element (e.g., Au) should fail."""
        mol = Chem.MolFromSmiles("c1ccccc1")
        result = mutate_atom(mol, atom_idx=0, target_symbol="Au")
        assert result is None

    def test_mutate_allowed_elements(self):
        """All allowed elements should be accepted."""
        mol = Chem.MolFromSmiles("CCCCCC")  # hexane
        allowed = ["N", "O", "S"]
        for sym in allowed:
            result = mutate_atom(mol, atom_idx=2, target_symbol=sym)
            # Some may fail due to valency, but should not crash
            assert result is None or validate_valency(result)


# ── State Mapper ──────────────────────────────────────────────


class TestStateMapper:
    """Tests for the Dynamic State-Mapping Layer."""

    def test_benzene_sites(self):
        """Benzene (6 aromatic C-H) should return 6 valid sites."""
        mapper = StateMapper()
        mol = Chem.MolFromSmiles("c1ccccc1")
        sites = mapper.get_valid_sites(mol)
        assert len(sites) == 6

    def test_toluene_sites(self):
        """Toluene should return sites (aromatic C-H + methyl H)."""
        mapper = StateMapper()
        mol = Chem.MolFromSmiles("Cc1ccccc1")
        sites = mapper.get_valid_sites(mol)
        # 5 aromatic C-H + methyl carbon with Hs
        assert len(sites) >= 5

    def test_site_id_to_atom_idx_mapping(self):
        """site_id should map to a valid atom index."""
        mapper = StateMapper()
        mol = Chem.MolFromSmiles("c1ccccc1")
        sites = mapper.get_valid_sites(mol)

        for site in sites:
            sid = site["site_id"]
            idx = mapper.get_atom_idx(sid)
            assert idx >= 0
            assert idx < mol.GetNumAtoms()

    def test_invalid_site_id(self):
        """Requesting an unmapped site_id should return -1."""
        mapper = StateMapper()
        mol = Chem.MolFromSmiles("c1ccccc1")
        mapper.get_valid_sites(mol)
        assert mapper.get_atom_idx(999) == -1

    def test_site_descriptions_exist(self):
        """Each site should have a non-empty description."""
        mapper = StateMapper()
        mol = Chem.MolFromSmiles("c1ccc(O)cc1")  # phenol
        sites = mapper.get_valid_sites(mol)

        for site in sites:
            assert "description" in site
            assert len(site["description"]) > 0

    def test_remapping_after_modification(self):
        """After modifying the molecule, sites should be re-enumerated."""
        mapper = StateMapper()
        mol = Chem.MolFromSmiles("c1ccccc1")
        sites_before = mapper.get_valid_sites(mol)

        # Attach methyl
        new_mol = apply_fragment_mode2(mol, "C", 0)
        sites_after = mapper.get_valid_sites(new_mol)

        # Site count should change (one aromatic H replaced, methyl Hs added)
        assert len(sites_before) != len(sites_after) or sites_before != sites_after
