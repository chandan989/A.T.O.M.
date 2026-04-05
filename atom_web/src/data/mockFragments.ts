import { Fragment } from '../types';

export const fragments: Fragment[] = [
  {
    category: 'Halogens',
    fragments: ['F', 'Cl', 'Br'],
    pharmacologicalRole: 'Metabolic stability, lipophilicity modulation, bioisosteric replacement',
  },
  {
    category: 'Polar H-Bond Donors',
    fragments: ['O', 'N', 'OH', 'NH2'],
    pharmacologicalRole: 'Solubility enhancement, target binding, membrane permeability tuning',
  },
  {
    category: 'Polar H-Bond Acceptors',
    fragments: ['C(=O)O', 'C(=O)N', 'S(=O)(=O)'],
    pharmacologicalRole: 'Pharmacokinetic optimization, protein interaction, metabolic soft spots',
  },
  {
    category: 'Aliphatic Groups',
    fragments: ['C', 'CC', 'C(C)C', 'CF3'],
    pharmacologicalRole: 'Lipophilicity increase, steric effects, conformational control',
  },
  {
    category: 'Ring Systems',
    fragments: ['c1ccccc1', 'C1CCCC1', 'c1ccncc1'],
    pharmacologicalRole: 'Rigidity, π-stacking, pharmacophore presentation, selectivity tuning',
  },
];
