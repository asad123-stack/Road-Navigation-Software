export default function VideoFeed({ frame }) {
  return (
    <div className="visual-card">
      <div className="visual-title">Annotated Frame</div>
      {frame ? (
        <img src={frame} alt="Annotated" style={{ width: "100%", borderRadius: 10, border: "1px solid #334155" }} />
      ) : (
        <div style={{ opacity: 0.7 }}>Waiting for frame...</div>
      )}
    </div>
  );
}
