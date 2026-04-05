import { Task } from '../types';

const difficultyColor: Record<string, string> = {
  easy: 'tag-green',
  medium: 'tag-orange',
  hard: 'tag-red',
};

const TaskCard = ({ task }: { task: Task }) => (
  <div className="task-card">
    <div className="task-card-header">
      <span className={`tag ${difficultyColor[task.difficulty]}`}>{task.difficulty}</span>
      <span className="task-card-title">{task.title}</span>
    </div>
    <div className="task-card-body">
      <p className="task-card-desc">{task.description}</p>
      <div className="task-card-smiles">{task.scaffold}</div>
      <div className="task-card-metric">
        <span>TARGET</span>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-mono)', fontWeight: 400 }}>{task.target}</span>
      </div>
      <div className="task-card-metric">
        <span>MAX STEPS</span>
        <span className="task-card-metric-value">{task.maxSteps}</span>
      </div>
      <div className="task-card-metric">
        <span>BASELINE</span>
        <span className="task-card-metric-value">{task.baselineScore}</span>
      </div>
    </div>
  </div>
);

export default TaskCard;
