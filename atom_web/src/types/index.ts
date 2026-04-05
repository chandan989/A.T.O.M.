export interface Task {
  id: string;
  difficulty: 'easy' | 'medium' | 'hard';
  title: string;
  scaffold: string;
  scaffoldName: string;
  target: string;
  maxSteps: number;
  baselineScore: number;
  description: string;
}

export interface Fragment {
  category: string;
  fragments: string[];
  pharmacologicalRole: string;
}

export interface EpisodeStep {
  step: number;
  action: string;
  smiles: string;
  qed: number;
  logP: number;
  saScore: number;
  mw: number;
  message: string;
  inTarget: boolean;
}

export interface RewardComponent {
  name: string;
  weight: number;
  description: string;
  color: string;
}

export interface ArchitectureComponent {
  id: string;
  label: string;
  description: string;
  type: 'engine' | 'agent' | 'layer' | 'wrapper';
}

export interface ApiEndpoint {
  method: string;
  path: string;
  description: string;
  requestBody?: string;
  response?: string;
}

export interface DataFlowStep {
  step: number;
  description: string;
}
