const colors = {
  tunnel: "#6b7280",
  urban: "#2563eb",
  open_road: "#16a34a",
  indoor: "#f59e0b",
};

export default function SceneBadge({ scene }) {
  const bg = colors[scene] ?? colors.urban;
  return (
    <div style={{ marginTop: 10 }}>
      <span style={{ background: bg, padding: "4px 8px", borderRadius: 12 }}>Scene: {scene}</span>
    </div>
  );
}
