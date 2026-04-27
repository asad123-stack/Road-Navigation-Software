export default function PipelineStatus({ steps }) {
  return (
    <div style={{ marginTop: 12 }}>
      <h4>Pipeline Status</h4>
      {steps.map((s) => (
        <div key={s}>✓ {s}</div>
      ))}
    </div>
  );
}
