export default function OledSimulator({ cue }) {
  return (
    <div
      style={{
        marginTop: 12,
        background: "#000",
        color: "#00ff66",
        fontFamily: "monospace",
        border: "1px solid #14532d",
        borderRadius: 6,
        padding: 8,
      }}
    >
      <div>OLED SIM</div>
      <div style={{ fontSize: 18 }}>{cue}</div>
    </div>
  );
}
