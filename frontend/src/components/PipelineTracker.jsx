function PipelineTracker({ status, currentStep, jobId, steps, error }) {
  return (
    <article className="panel status-panel">
      <h2>Pipeline Tracker</h2>
      <p>
        <span className="label">Job ID:</span> {jobId || "Not started"}
      </p>
      <p>
        <span className="label">Status:</span> {status || "idle"}
      </p>
      <p>
        <span className="label">Current Step:</span> {currentStep || "Waiting"}
      </p>
      {steps?.length > 0 && (
        <div className="step-history">
          {steps.map((item, index) => (
            <p key={`${item.step}-${index}`} className="step-item">
              {item.step} - {item.status}
            </p>
          ))}
        </div>
      )}
      {error && <p className="error">{error}</p>}
    </article>
  );
}

export default PipelineTracker;
