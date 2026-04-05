import { ArchitectureComponent, ApiEndpoint, DataFlowStep } from '../types';

export const architectureComponents: ArchitectureComponent[] = [
  { id: 'task-engine', label: 'TASK ENGINE', description: 'Manages task definitions, scaffold loading, and episode lifecycle', type: 'engine' },
  { id: 'chemistry-engine', label: 'CHEMISTRY ENGINE (RDKit)', description: 'Validates molecular modifications, enforces chemical rules, computes properties', type: 'engine' },
  { id: 'rubric-engine', label: 'RUBRIC ENGINE (GRADER)', description: 'Scores complete trajectories using 5-component reward function', type: 'engine' },
  { id: 'state-mapping', label: 'DYNAMIC STATE-MAPPING LAYER', description: 'Translates LLM site selections into RDKit atom indices', type: 'layer' },
  { id: 'fastapi', label: 'FASTAPI WRAPPER', description: 'HTTP endpoints: reset / step / state / health', type: 'wrapper' },
  { id: 'generator', label: 'GENERATOR AGENT', description: 'Proposes fragment additions and site selections using spatial reasoning', type: 'agent' },
  { id: 'critic', label: 'CRITIC AGENT', description: 'Validates proposals against Lipinski rules, PAINS filters, and heuristics', type: 'agent' },
];

export const apiEndpoints: ApiEndpoint[] = [
  { method: 'GET', path: '/health', description: 'Health check (no auth required)', response: '{ status: "ok" }' },
  { method: 'GET', path: '/auth/verify', description: 'Verify API key is valid', response: '{ status: "authenticated" }' },
  { method: 'GET', path: '/tasks', description: 'List available task definitions', response: '{ tasks: TaskDefinition[] }' },
  { method: 'POST', path: '/env/reset', description: 'Initialize a new episode with task configuration', requestBody: '{ task_id: number }', response: '{ observation: Observation }' },
  { method: 'POST', path: '/env/step', description: 'Execute an action and return updated observation', requestBody: '{ action_type, fragment_name?, site_id? }', response: '{ observation, reward }' },
  { method: 'GET', path: '/env/state', description: 'Get current environment state', response: '{ episode_id, step_count }' },
  { method: 'WS', path: '/ws/observe', description: 'WebSocket for real-time observation streaming', response: '{ type, data }' },
];

export const dataFlowSteps: DataFlowStep[] = [
  { step: 1, description: 'Inference calls reset() → receives initial observation with scaffold SMILES and target profile' },
  { step: 2, description: 'Generator calls get_valid_sites → enumerates modification sites with natural-language descriptions' },
  { step: 3, description: 'Generator proposes fragment + site based on current properties and target gap' },
  { step: 4, description: 'Critic validates proposal against chemical heuristics and Lipinski/PAINS filters' },
  { step: 5, description: 'Inference calls step(action) → Chemistry Engine applies modification → updated observation' },
  { step: 6, description: 'Repeat steps 2-5 until agent calls finish or reaches max_steps' },
  { step: 7, description: 'Rubric Engine scores complete trajectory → continuous score in [0.0, 1.0]' },
];
