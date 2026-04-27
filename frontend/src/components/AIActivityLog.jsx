export default function AIActivityLog({ logs }) {
  return (
    <div style={{ marginTop: 12 }}>
      <h4>AI Activity Log</h4>
      <div style={{ maxHeight: 220, overflow: "auto" }}>
        {logs.map((log, i) => (
          <div key={i}>{log}</div>
        ))}
      </div>
    </div>
  );
}
