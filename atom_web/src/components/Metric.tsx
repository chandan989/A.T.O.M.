interface MetricProps {
  value: string | number;
  label: string;
  color?: string;
}

const Metric = ({ value, label, color }: MetricProps) => (
  <div className="metric">
    <div className="metric-value" style={{ color }}>{value}</div>
    <div className="metric-label">{label}</div>
  </div>
);

export default Metric;
