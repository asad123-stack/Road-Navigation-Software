export default function NavigationCue({ cue, nextStep }) {
  return (
    <div style={{ marginTop: 12 }}>
      <strong>Navigation Cue:</strong> {cue}
      {nextStep && (
        <div style={{ marginTop: 4, opacity: 0.85 }}>
          <strong>Next Turn:</strong> {nextStep}
        </div>
      )}
    </div>
  );
}
