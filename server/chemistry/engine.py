# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
Chemistry engine for ATOM environment using RDKit.
Handles property computation, validity checks, and applying modifications.
"""

from typing import Dict, List, Tuple, Any, Optional
import rdkit
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, QED, AllChem
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

# Initialize PAINS, BRENK, and NIH filter catalogs
params = FilterCatalogParams()
params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
params.AddCatalog(FilterCatalogParams.FilterCatalogs.BRENK)
params.AddCatalog(FilterCatalogParams.FilterCatalogs.NIH)
alert_catalog = FilterCatalog(params)

def compute_properties(mol: Chem.Mol) -> Dict[str, float]:
    """Computes basic molecular properties including 3D conformer energy."""
    # Ensure molecule has explicit Hydrogens for accurate 3D and property calculation
    mol_with_h = Chem.AddHs(mol)

    energy = compute_3d_energy(mol_with_h)

    return {
        "QED": QED.qed(mol),
        "LogP": Descriptors.MolLogP(mol),
        "MW": Descriptors.MolWt(mol),
        "SA_Score": compute_sa_score(mol),
        "Energy": energy
    }

def compute_3d_energy(mol: Chem.Mol) -> float:
    """Generates 3D conformer and calculates MMFF94 strain energy."""
    try:
        # Generate 3D coordinates
        res = AllChem.EmbedMolecule(mol, randomSeed=42)
        if res != 0:
            return 999.0 # Embedding failed

        # Optimize and get energy using MMFF94 force field
        ff = AllChem.MMFFGetMoleculeForceField(mol, AllChem.MMFFGetMoleculeProperties(mol))
        if ff:
            ff.Minimize()
            energy = ff.CalcEnergy()
            return energy
    except:
        pass
    return 999.0 # High penalty if 3D conformer fails

def compute_sa_score(mol: Chem.Mol) -> float:
    """Computes Synthetic Accessibility Score. Simplified SA score for now."""
    # Note: RDKit contrib holds a more complex SA_Score.
    # For standalone, a simplified heuristic or rdMolDescriptors based proxy can be used,
    # but we'll import it correctly if available, or mock with a basic proxy.
    try:
        import rdkit.Chem.rdMolDescriptors as rmd
        # If sascore module is available in contrib
        import sys
        from rdkit.Chem import RDConfig
        import os
        sys.path.append(os.path.join(RDConfig.RDBASE, 'Contrib', 'SA_Score'))
        import sascorer
        return sascorer.calculateScore(mol)
    except:
        # Fallback heuristic: larger molecules with more rings/stereocenters are harder
        mw = Descriptors.MolWt(mol)
        rings = rdMolDescriptors.CalcNumRings(mol)
        return min(10.0, max(1.0, mw / 100.0 + rings * 0.5))

def check_alerts(mol: Chem.Mol) -> bool:
    """Checks for PAINS, BRENK, or NIH structural alerts."""
    return alert_catalog.HasMatch(mol)

def check_lipinski(mol: Chem.Mol) -> int:
    """Returns number of Lipinski rule of 5 violations."""
    violations = 0
    if Descriptors.MolWt(mol) > 500: violations += 1
    if Descriptors.MolLogP(mol) > 5: violations += 1
    if rdMolDescriptors.CalcNumHBD(mol) > 5: violations += 1
    if rdMolDescriptors.CalcNumHBA(mol) > 10: violations += 1
    return violations

def validate_valency(mol: Chem.Mol) -> bool:
    """Checks if molecule has valid valency."""
    try:
        Chem.SanitizeMol(mol)
        return True
    except:
        return False

def apply_fragment_mode1(scaffold_mol: Chem.Mol, fragment_smiles: str, r_group: str) -> Optional[Chem.Mol]:
    """
    Applies fragment to scaffold using Mode 1 (R-Group).
    r_group should be one of "R1", "R2", "R3", which map to dummy atoms [1*], [2*], [3*]
    """
    # Find dummy atom in scaffold
    r_map = {"R1": 1, "R2": 2, "R3": 3}
    if r_group not in r_map:
        return None

    isotope = r_map[r_group]

    # We'll replace the dummy atom ([isotope*]) with the fragment
    # This is a bit complex in RDKit. Let's do a reaction or simple replacement.
    frag_mol = Chem.MolFromSmiles(fragment_smiles)
    if not frag_mol: return None

    # Simple approach: ReplaceSubstructs if scaffold has dummy atoms
    # We assume scaffold has [1*], [2*], etc.
    dummy = Chem.MolFromSmarts(f"[{isotope}*]")
    if not scaffold_mol.HasSubstructMatch(dummy):
        return None

    # Replace dummy with fragment. ReplaceSubstructs returns a tuple.
    # Note: the attachment point on fragment isn't explicitly defined here if we just replace.
    # So we'll use a reaction.
    rxn_smarts = f"[{isotope}*:1].[*:2]>>[*:1]-[*:2]"
    # Actually, RDKit's ReplaceSubstructs is easier if fragment is just a group
    res = Chem.ReplaceSubstructs(scaffold_mol, dummy, frag_mol, replaceAll=True)
    if res:
        new_mol = res[0]
        try:
            Chem.SanitizeMol(new_mol)
            return new_mol
        except:
            return None
    return None

def apply_fragment_mode2(mol: Chem.Mol, fragment_smiles: str, atom_idx: int) -> Optional[Chem.Mol]:
    """
    Applies fragment to a specific atom index (Mode 2).
    """
    frag_mol = Chem.MolFromSmiles(fragment_smiles)
    if not frag_mol: return None

    # Create an editable molecule
    rw_mol = Chem.RWMol(mol)

    # Check if atom_idx is valid and has implicit/explicit H
    atom = rw_mol.GetAtomWithIdx(atom_idx)
    if atom.GetTotalNumHs() == 0:
        return None # No room to attach

    # Combine molecules
    frag_idx_offset = rw_mol.GetNumAtoms()
    rw_mol.InsertMol(frag_mol)

    # Create bond between atom_idx and the first atom of the fragment
    # We assume the first atom in the fragment SMILES is the attachment point
    rw_mol.AddBond(atom_idx, frag_idx_offset, Chem.BondType.SINGLE)

    try:
        Chem.SanitizeMol(rw_mol)
        return rw_mol.GetMol()
    except:
        return None

def mutate_atom(mol: Chem.Mol, atom_idx: int, target_symbol: str) -> Optional[Chem.Mol]:
    """
    Mutates an atom to a new element (e.g., changing Carbon to Nitrogen in a ring).
    """
    rw_mol = Chem.RWMol(mol)
    atom = rw_mol.GetAtomWithIdx(atom_idx)

    # We only allow basic organic mutability to maintain stability
    allowed_symbols = {"C", "N", "O", "S", "P", "Si"}
    if target_symbol not in allowed_symbols:
        return None

    atom.SetAtomicNum(Chem.GetPeriodicTable().GetAtomicNumber(target_symbol))

    try:
        # Sanitize will recalculate implicit valences and hydrogens
        Chem.SanitizeMol(rw_mol)
        return rw_mol.GetMol()
    except:
        return None

def remove_group(mol: Chem.Mol, atom_idx: int) -> Optional[Chem.Mol]:
    """
    Removes a substituent at the specified atom index (reverting it to a hydrogen).
    This breaks the exocyclic bond connecting the specified core atom to the substituent.
    """
    rw_mol = Chem.RWMol(mol)
    atom = rw_mol.GetAtomWithIdx(atom_idx)

    # Simple heuristic: find the first non-ring neighbor and remove that sub-graph
    bond_to_break = None
    neighbor_to_remove = None

    for bond in atom.GetBonds():
        nbr = bond.GetOtherAtom(atom)
        if not bond.IsInRing():
            bond_to_break = bond
            neighbor_to_remove = nbr
            break

    if bond_to_break:
        # We simplify for the environment: just break the bond,
        # and delete the non-core fragment.
        rw_mol.RemoveBond(atom.GetIdx(), neighbor_to_remove.GetIdx())
        frags = Chem.GetMolFrags(rw_mol.GetMol(), asMols=True)

        # Assume the fragment containing our original atom_idx is the core
        for frag in frags:
            if frag.GetNumAtoms() > 5: # basic proxy for core vs substituent
                try:
                    Chem.SanitizeMol(frag)
                    return frag
                except:
                    pass
    return None
