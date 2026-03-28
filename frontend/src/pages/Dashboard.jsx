import { useState, useEffect, useCallback } from "react";
import CandidateForm from "../components/CandidateForm";
import PipelineTracker from "../components/PipelineTracker";
import InterviewChat from "../components/InterviewChat";
import ProcessingScreen from "../components/ProcessingScreen";
import ResultsDashboard from "../components/ResultsDashboard";
import ErrorScreen from "../components/ErrorScreen";
import { createJob, getJobStatus, submitInterviewAnswer } from "../services/api";

const POLL_INTERVAL_MS = 2000;

function Dashboard() {
  const [jobId, setJobId] = useState(() => localStorage.getItem("jobId") || "");
  const [jobData, setJobData] = useState(null);
  const [polling, setPolling] = useState(false);

  const pollJobStatus = useCallback(async (id) => {
    try {
      const payload = await getJobStatus(id);
      setJobData(payload);

      if (payload.status === "done" || payload.status === "failed") {
        setPolling(false);
      }
    } catch (pollError) {
      setJobData((prev) => ({
        ...prev,
        status: "failed",
        error: pollError?.response?.data?.detail || pollError.message || "Failed to poll pipeline.",
      }));
      setPolling(false);
    }
  }, []);

  // Set up polling interval
  useEffect(() => {
    let timer;
    if (jobId && polling) {
      timer = window.setInterval(() => {
        pollJobStatus(jobId);
      }, POLL_INTERVAL_MS);
    }
    return () => clearInterval(timer);
  }, [jobId, polling, pollJobStatus]);

  // Initial load / resume session logic
  useEffect(() => {
    if (jobId && !jobData) {
      setPolling(true);
      pollJobStatus(jobId);
    }
  }, [jobId, jobData, pollJobStatus]);

  const handleSubmit = async (formData) => {
    setJobData(null);
    setPolling(false);

    try {
      // Trigger submission UI state
      setJobData({ status: "submitting" });
      const payload = await createJob(formData);

      const newJobId = payload.job_id;
      localStorage.setItem("jobId", newJobId);
      setJobId(newJobId);

      setJobData({ status: "queued" });
      setPolling(true);
      pollJobStatus(newJobId);
    } catch (submitError) {
      setJobData({
        status: "failed",
        error: submitError?.response?.data?.detail || submitError.message || "Unable to create job.",
      });
    }
  };

  const handleInterviewAnswer = async (answer) => {
    if (!jobId) return;

    try {
      const payload = await submitInterviewAnswer(jobId, answer);
      // Backend returns the updated job state, save it instantly
      setJobData(payload);
      
      // INSTANT FETCH AFTER CRITICAL ACTION TO PREVENT POLLING DRIFT
      pollJobStatus(jobId);
    } catch (submitError) {
      setJobData((prev) => ({
        ...prev,
        status: "failed",
        error: submitError?.response?.data?.detail || submitError.message || "Failed to submit answer.",
      }));
      setPolling(false);
    }
  };

  const handleRetry = () => {
    if (jobId) {
      setJobData(null);
      setPolling(true);
      pollJobStatus(jobId);
    }
  };

  const handleNewAnalysis = () => {
    localStorage.removeItem("jobId");
    setJobId("");
    setJobData(null);
    setPolling(false);
  };

  // Render logic completely controlled by backend state
  const renderContent = () => {
    // 1. Initial State
    if (!jobId) {
      return (
        <section className="grid">
          <CandidateForm onSubmit={handleSubmit} isLoading={jobData?.status === "submitting"} />
          <div
            className="right-column placeholder-panel"
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "#fdfdfd",
              borderRadius: "8px",
              padding: "2rem",
              textAlign: "center",
              color: "#aaa",
              border: "2px dashed #eaeaea",
            }}
          >
            <p>Submit a candidate to begin the autonomous pipeline.</p>
          </div>
        </section>
      );
    }

    // 2. Loading initial job state after refresh
    if (!jobData || jobData.status === "submitting") {
      return <ProcessingScreen message={jobData?.status === "submitting" ? "Submitting Candidate..." : "Fetching job status..."} />;
    }

    const { status, steps, interview, result, report_url, error } = jobData;

    // 3. Status mapping
    if (status === "queued" || status === "running") {
      return <PipelineTracker steps={steps} status={status} jobId={jobId} />;
    }

    if (status === "awaiting_interview" || status === "interviewing") {
      return <InterviewChat data={interview} jobId={jobId} onSubmitAnswer={handleInterviewAnswer} />;
    }

    if (status === "processing_decision") {
      return <ProcessingScreen message="Running multi-agent evaluation..." />;
    }

    if (status === "done") {
      return <ResultsDashboard result={result} reportUrl={report_url} />;
    }

    if (status === "failed") {
      return <ErrorScreen error={error} onRetry={handleRetry} onNewAnalysis={handleNewAnalysis} />;
    }

    // Catch-all processing screen for unknown or transitional states
    return <ProcessingScreen message={`Processing status: ${status}...`} />;
  };

  return (
    <main className="page-wrap">
      <section className="hero-card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <p className="eyebrow">Autonomous Hiring Pipeline</p>
            <h1>SmartHireX</h1>
          </div>
          {jobId && (
            <button
              onClick={handleNewAnalysis}
              style={{
                padding: "0.5rem 1rem",
                background: "transparent",
                border: "1px solid #ccc",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Start New Analysis
            </button>
          )}
        </div>
        <p className="lead" style={{ marginTop: "1rem" }}>
          Track real-time progression across parse, enrich, analyze, and decision stages.
        </p>
      </section>

      {/* Conditionally rendered UI based strictly on State */}
      <div style={{ marginTop: "2rem" }} className="fade-in" key={jobData ? jobData.status : "intake"}>
        {renderContent()}
      </div>
    </main>
  );
}

export default Dashboard;
