interface StatItem {
  value: string;
  label: string;
  bgColor: string;
  textColor: string;
}

interface StatsGridProps {
  stats: StatItem[];
}

const StatsGrid = ({ stats }: StatsGridProps) => (
  <div className="stats-grid section">
    {stats.map((stat, i) => (
      <div className="stat-cell" key={i} style={{ backgroundColor: stat.bgColor, color: stat.textColor }}>
        <div className="stat-value">{stat.value}</div>
        <div className="stat-label">{stat.label}</div>
      </div>
    ))}
  </div>
);

export default StatsGrid;
