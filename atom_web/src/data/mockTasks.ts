import { Task } from '../types';

export const tasks: Task[] = [
  {
    id: 'task-1',
    difficulty: 'easy',
    title: 'SINGLE-PROPERTY OPTIMIZATION',
    scaffold: 'c1ccccc1',
    scaffoldName: 'Benzene',
    target: 'LogP ∈ [2.5, 3.0]',
    maxSteps: 5,
    baselineScore: 0.92,
    description: 'Modify benzene to achieve target lipophilicity. Tests basic fragment selection.',
  },
  {
    id: 'task-2',
    difficulty: 'medium',
    title: 'MULTI-PARAMETER BALANCING',
    scaffold: 'Cc1ccccc1',
    scaffoldName: 'Toluene derivative',
    target: 'LogP ∈ [1.0, 2.5] AND QED ≥ 0.6',
    maxSteps: 8,
    baselineScore: 0.71,
    description: 'Simultaneously reduce LogP while maximizing QED. Requires trade-off reasoning.',
  },
  {
    id: 'task-3',
    difficulty: 'hard',
    title: 'FULL TPP MATCHING',
    scaffold: 'c1cnc(N)nc1',
    scaffoldName: 'Pyrimidine-based (~350 Da)',
    target: 'LogP ∈ [2.0, 3.5] AND QED ≥ 0.65 AND SA_Score ≤ 4.0 AND MW ∈ [300, 500]',
    maxSteps: 12,
    baselineScore: 0.38,
    description: 'Navigate complex chemical space hitting a 4-parameter Target Product Profile with PAINS avoidance.',
  },
];
