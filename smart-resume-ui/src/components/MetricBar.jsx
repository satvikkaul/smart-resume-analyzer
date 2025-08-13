export default function MetricBar({ label, value }) {
  const pct = Math.max(0, Math.min(1, Number(value || 0))) * 100;
  return (
    <div className="metric">
      <div className="metric-head">
        <span>{label}</span>
        <span>{pct.toFixed(0)}%</span>
      </div>
      <div className="bar">
        <div className="fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
