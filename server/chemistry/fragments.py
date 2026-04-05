# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
Exhaustive fragment library for ATOM environment.
Combines a highly curated named library with procedural combinatorial generation
to ensure enterprise-grade structural coverage.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from rdkit import Chem

@dataclass
class Fragment:
    name: str
    smiles: str
    attachment_smarts: str
    description: str

FRAGMENTS: Dict[str, Fragment] = {
    # ------------------ Halogens ------------------
    "Fluorine": Fragment("Fluorine", "F", "[*]-[F]", "Metabolic stability, lipophilicity modulation"),
    "Chlorine": Fragment("Chlorine", "Cl", "[*]-[Cl]", "Lipophilicity modulation, bioisosteric replacement"),
    "Bromine": Fragment("Bromine", "Br", "[*]-[Br]", "Heavy halogen, strong lipophilicity"),
    "Iodine": Fragment("Iodine", "I", "[*]-[I]", "Very heavy halogen, extremely lipophilic"),
    "Trifluoromethyl": Fragment("Trifluoromethyl", "C(F)(F)F", "[*]-C(F)(F)F", "Metabolic blocking, strong lipophilicity"),
    "Trifluoromethoxy": Fragment("Trifluoromethoxy", "OC(F)(F)F", "[*]-OC(F)(F)F", "Strong lipophilic, electron-withdrawing"),

    # ------------------ Polar / H-Bond Donors & Acceptors ------------------
    "Hydroxyl": Fragment("Hydroxyl", "O", "[*]-[O;H1]", "Aqueous solubility, hydrogen-bond donor"),
    "Amino": Fragment("Amino", "N", "[*]-[N;H2]", "Aqueous solubility, base, hydrogen-bond donor"),
    "Methylamino": Fragment("Methylamino", "NC", "[*]-NC", "Secondary amine, base, H-bond donor"),
    "Dimethylamino": Fragment("Dimethylamino", "N(C)C", "[*]-N(C)C", "Tertiary amine, base"),
    "Carboxyl": Fragment("Carboxyl", "C(=O)O", "[*]-C(=O)[O;H1]", "Acidic group, solubility"),
    "Methoxy": Fragment("Methoxy", "OC", "[*]-OC", "Electron-donating, H-bond acceptor"),
    "Ethoxy": Fragment("Ethoxy", "OCC", "[*]-OCC", "Slightly lipophilic H-bond acceptor"),
    "Cyano": Fragment("Cyano", "C#N", "[*]-C#N", "Electron-withdrawing, linear geometry"),
    "Nitro": Fragment("Nitro", "[N+](=O)[O-]", "[*]-[N+](=O)[O-]", "Strong electron-withdrawing"),
    "Formyl": Fragment("Formyl", "C=O", "[*]-C=O", "Aldehyde, reactive intermediate or H-bond acceptor"),
    "Acetyl": Fragment("Acetyl", "C(=O)C", "[*]-C(=O)C", "Ketone, H-bond acceptor"),
    "Amide": Fragment("Amide", "C(=O)N", "[*]-C(=O)N", "Neutral H-bond donor/acceptor"),
    "Sulfonamide": Fragment("Sulfonamide", "S(=O)(=O)N", "[*]-S(=O)(=O)N", "H-bond donor/acceptor, polar, common in drugs"),
    "Methylsulfonyl": Fragment("Methylsulfonyl", "S(=O)(=O)C", "[*]-S(=O)(=O)C", "Strong electron-withdrawing, highly polar"),
    "Thiol": Fragment("Thiol", "S", "[*]-[S;H1]", "Sulfhydryl group, reactive, heavy atom H-bond donor"),
    "Methylthio": Fragment("Methylthio", "SC", "[*]-SC", "Lipophilic, heavy atom H-bond acceptor"),

    # ------------------ Aliphatic Groups ------------------
    "Methyl": Fragment("Methyl", "C", "[*]-[C;H3]", "Steric bulk, slight lipophilicity"),
    "Ethyl": Fragment("Ethyl", "CC", "[*]-CC", "Lipophilicity, steric bulk"),
    "Propyl": Fragment("Propyl", "CCC", "[*]-CCC", "Linear lipophilic chain"),
    "Isopropyl": Fragment("Isopropyl", "C(C)C", "[*]-C(C)C", "Branched aliphatic, steric blocking"),
    "Butyl": Fragment("Butyl", "CCCC", "[*]-CCCC", "Long lipophilic chain"),
    "Isobutyl": Fragment("Isobutyl", "CC(C)C", "[*]-CC(C)C", "Branched lipophilic chain"),
    "tert-Butyl": Fragment("tert-Butyl", "C(C)(C)C", "[*]-C(C)(C)C", "High steric bulk, lipophilicity"),
    "Vinyl": Fragment("Vinyl", "C=C", "[*]-C=C", "Alkene, rigid geometry"),
    "Ethynyl": Fragment("Ethynyl", "C#C", "[*]-C#C", "Alkyne, linear rigid geometry"),

    # ------------------ Cycloalkanes ------------------
    "Cyclopropyl": Fragment("Cyclopropyl", "C1CC1", "[*]-C1CC1", "Conformational restriction, metabolic stability"),
    "Cyclobutyl": Fragment("Cyclobutyl", "C1CCC1", "[*]-C1CCC1", "Rigid spacer, lipophilic"),
    "Cyclopentyl": Fragment("Cyclopentyl", "C1CCCC1", "[*]-C1CCCC1", "Moderate steric bulk, lipophilic"),
    "Cyclohexyl": Fragment("Cyclohexyl", "C1CCCCC1", "[*]-C1CCCCC1", "High steric bulk, highly lipophilic"),
    "Oxetane": Fragment("Oxetane", "C1COC1", "[*]-C1COC1", "Polar bioisostere for gem-dimethyl or carbonyl"),

    # ------------------ Simple Heterocycles (Saturated) ------------------
    "Pyrrolidine": Fragment("Pyrrolidine", "C1CCNC1", "[*]-C1CCNC1", "Aliphatic base, secondary amine"),
    "Piperidine": Fragment("Piperidine", "C1CCNCC1", "[*]-C1CCNCC1", "Aliphatic base, solubility"),
    "Morpholine": Fragment("Morpholine", "C1COCCN1", "[*]-C1COCCN1", "Aliphatic base + oxygen, excellent solubility"),
    "Piperazine": Fragment("Piperazine", "C1CNCCN1", "[*]-C1CNCCN1", "Two basic nitrogens, very high solubility"),
    "Tetrahydropyran": Fragment("Tetrahydropyran", "C1CCOCC1", "[*]-C1CCOCC1", "Polar aliphatic ring, H-bond acceptor"),

    # ------------------ 6-Membered Aromatics ------------------
    "Phenyl": Fragment("Phenyl", "c1ccccc1", "[*]-c1ccccc1", "Aromatic core, hydrophobic"),
    "Pyridine": Fragment("Pyridine", "c1ccccn1", "[*]-c1ccccn1", "Aromatic base, H-bond acceptor"),
    "Pyrimidine": Fragment("Pyrimidine", "c1cncnc1", "[*]-c1cncnc1", "Weak base, two H-bond acceptors"),
    "Pyrazine": Fragment("Pyrazine", "c1cnccn1", "[*]-c1cnccn1", "Weak base, para Ns"),
    "Pyridazine": Fragment("Pyridazine", "c1cnncc1", "[*]-c1cnncc1", "Weak base, ortho Ns"),

    # ------------------ 5-Membered Aromatics ------------------
    "Pyrrole": Fragment("Pyrrole", "c1cc[nH]c1", "[*]-c1cc[nH]c1", "H-bond donor aromatic, electron-rich"),
    "Furan": Fragment("Furan", "c1ccoc1", "[*]-c1ccoc1", "H-bond acceptor aromatic, electron-rich"),
    "Thiophene": Fragment("Thiophene", "c1ccsc1", "[*]-c1ccsc1", "Lipophilic aromatic, phenyl bioisostere"),
    "Imidazole": Fragment("Imidazole", "c1c[nH]cn1", "[*]-c1c[nH]cn1", "Amphoteric, H-bond donor and acceptor"),
    "Pyrazole": Fragment("Pyrazole", "c1c[nH]nc1", "[*]-c1c[nH]nc1", "Aromatic, H-bond donor/acceptor"),
    "Oxazole": Fragment("Oxazole", "c1cnoc1", "[*]-c1cnoc1", "Aromatic, stable, H-bond acceptor"),
    "Isoxazole": Fragment("Isoxazole", "c1conncc1", "[*]-c1conncc1", "Aromatic, lipophilic H-bond acceptor"),
    "Thiazole": Fragment("Thiazole", "c1cnsc1", "[*]-c1cnsc1", "Aromatic, phenyl bioisostere, H-bond acceptor"),
    "Triazole": Fragment("Triazole", "c1n[nH]cn1", "[*]-c1n[nH]cn1", "Highly polar aromatic, multiple Ns"),
    "Tetrazole": Fragment("Tetrazole", "c1nn[nH]n1", "[*]-c1nn[nH]n1", "Bioisostere for carboxylic acid, acidic"),

    # ------------------ Fused Ring Systems ------------------
    "Naphthalene": Fragment("Naphthalene", "c1ccc2ccccc2c1", "[*]-c1ccc2ccccc2c1", "Large lipophilic core"),
    "Indole": Fragment("Indole", "c1ccc2c(c1)cc[nH]2", "[*]-c1ccc2c(c1)cc[nH]2", "Important biological core, H-bond donor"),
    "Benzimidazole": Fragment("Benzimidazole", "c1ccc2c(c1)nc[nH]2", "[*]-c1ccc2c(c1)nc[nH]2", "Amphoteric fused ring"),
    "Benzofuran": Fragment("Benzofuran", "c1ccc2c(c1)cco2", "[*]-c1ccc2c(c1)cco2", "Lipophilic fused ring, H-bond acceptor"),
    "Benzothiophene": Fragment("Benzothiophene", "c1ccc2c(c1)ccs2", "[*]-c1ccc2c(c1)ccs2", "Lipophilic fused ring"),
    "Quinoline": Fragment("Quinoline", "c1ccc2ncccc2c1", "[*]-c1ccc2ncccc2c1", "Basic fused ring, H-bond acceptor"),
    "Isoquinoline": Fragment("Isoquinoline", "c1ccc2cnccc2c1", "[*]-c1ccc2cnccc2c1", "Basic fused ring, H-bond acceptor"),
    "Purine": Fragment("Purine", "c1ncnc2[nH]cnc12", "[*]-c1ncnc2[nH]cnc12", "Biological core, multiple Ns"),

    # ------------------ Inorganic / Metalloid Groups ------------------
    "BoronicAcid": Fragment("BoronicAcid", "B(O)O", "[*]-B(O)O", "Covalent binder, transition state analog"),
    "Silane": Fragment("Silane", "[SiH3]", "[*]-[SiH3]", "Bioisostere for carbon, lipophilic"),
    "Phosphate": Fragment("Phosphate", "P(=O)(O)O", "[*]-P(=O)(O)O", "Highly polar, biological mimic"),
    "Sulfate": Fragment("Sulfate", "S(=O)(=O)O", "[*]-S(=O)(=O)O", "Strong acid, extreme solubility"),
}

# --- Procedural Generation to exhaustively expand the library ---

def _generate_aliphatic_chains(max_length: int = 8):
    """Generates linear alkyl chains up to max_length."""
    for i in range(5, max_length + 1):
        name = f"Alkyl_C{i}"
        smiles = "C" * i
        FRAGMENTS[name] = Fragment(name, smiles, f"[*]-{smiles}", f"Linear lipophilic chain of length {i}")

def _generate_halogenated_methanes():
    """Generates common permutations of fluorinated/chlorinated methanes."""
    combos = [
        ("Difluoromethyl", "C(F)F"),
        ("Chloromethyl", "CCl"),
        ("Dichloromethyl", "C(Cl)Cl"),
        ("Trichloromethyl", "C(Cl)(Cl)Cl"),
        ("Bromomethyl", "CBr")
    ]
    for name, smiles in combos:
        FRAGMENTS[name] = Fragment(name, smiles, f"[*]-{smiles}", "Halogenated aliphatic, varying electronics/sterics")

def _validate_and_clean():
    """Validates all generated fragments and removes invalid ones."""
    invalid_keys = []
    for name, frag in FRAGMENTS.items():
        mol = Chem.MolFromSmiles(frag.smiles)
        if mol is None:
            invalid_keys.append(name)

    for k in invalid_keys:
        del FRAGMENTS[k]

# Run procedural generators
_generate_aliphatic_chains()
_generate_halogenated_methanes()
_validate_and_clean()
