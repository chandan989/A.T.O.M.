# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
Dynamic State-Mapping Layer for ATOM environment.
Translates RDKit atom indices to readable site descriptions for Mode 2.
"""

from typing import Dict, List, Any
import rdkit
from rdkit import Chem

class StateMapper:
    def __init__(self):
        # Maps LLM friendly site_id to RDKit atom_idx
        self.site_to_idx: Dict[int, int] = {}
        self.idx_to_site: Dict[int, int] = {}
        self.descriptions: Dict[int, str] = {}

    def get_valid_sites(self, mol: Chem.Mol) -> List[Dict[str, Any]]:
        """
        Enumerates valid C-H attachment sites and generates spatial descriptions.
        """
        self.site_to_idx.clear()
        self.idx_to_site.clear()
        self.descriptions.clear()

        valid_sites = []
        site_id = 0

        for atom in mol.GetAtoms():
            # Consider ANY atom (Organic or Inorganic) with at least one Hydrogen for attachment
            if atom.GetTotalNumHs() > 0:
                idx = atom.GetIdx()

                # Generate description
                desc = self._generate_description(mol, atom)

                self.site_to_idx[site_id] = idx
                self.idx_to_site[idx] = site_id
                self.descriptions[site_id] = desc

                valid_sites.append({
                    "site_id": site_id,
                    "description": desc
                })

                site_id += 1

        return valid_sites

    def get_atom_idx(self, site_id: int) -> int:
        """Returns the RDKit atom index for a given site_id."""
        return self.site_to_idx.get(site_id, -1)

    def _generate_description(self, mol: Chem.Mol, atom: Chem.Atom) -> str:
        """Generates a plain-English spatial description for the atom."""
        desc = []

        symbol = atom.GetSymbol()

        if atom.GetIsAromatic():
            desc.append(f"Aromatic {symbol}")
        else:
            hyb = str(atom.GetHybridization())
            desc.append(f"{hyb} {symbol}")

        # Describe neighbors
        neighbors = []
        for nbr in atom.GetNeighbors():
            sym = nbr.GetSymbol()
            if sym != "C" and sym != "H":
                neighbors.append(f"adjacent to {sym}")

        if neighbors:
            desc.append(", ".join(neighbors))

        return " ".join(desc)
