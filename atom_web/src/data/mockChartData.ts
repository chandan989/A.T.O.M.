import { RewardComponent } from '../types';

export const rewardComponents: RewardComponent[] = [
  { name: 'Target Adherence', weight: 40, description: 'How closely the final molecule matches the target property profile.', color: '#7B3EFC' },
  { name: 'Trajectory Quality', weight: 25, description: 'Monotonic improvement trend, minimal backtracking, consistent progress.', color: '#CCFF00' },
  { name: 'Step Efficiency', weight: 15, description: 'Achieving target in fewer steps is rewarded. Penalizes unnecessary actions.', color: '#FF5415' },
  { name: 'Chemical Validity', weight: 10, description: 'All intermediates pass valency checks, PAINS filters, Lipinski rules.', color: '#FFFFFF' },
  { name: 'Exploration Diversity', weight: 10, description: 'Variety of fragment types and modification sites explored.', color: '#E5E5E5' },
];

export const baselineScores = [
  { task: 'Task 1', difficulty: 'easy', score: 0.92, color: '#CCFF00', notes: 'Single property — achievable with greedy strategy' },
  { task: 'Task 2', difficulty: 'medium', score: 0.71, color: '#FF5415', notes: 'Multi-parameter — requires trade-off reasoning' },
  { task: 'Task 3', difficulty: 'hard', score: 0.38, color: '#E63946', notes: 'Full TPP — requires sophisticated planning' },
];
