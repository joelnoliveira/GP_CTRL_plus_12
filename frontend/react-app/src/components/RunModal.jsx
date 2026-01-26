import React, { useEffect } from 'react';
import "../styles/components/run_modal.css";

function RunModal({ run_data, isOpen, handleOnOpen }) {

  //* ESC key handler */
  useEffect(() => {
    if (!isOpen) return;

    const handleEsc = (event) => {
      if (event.key === "Escape") handleOnOpen();
    };

    document.addEventListener("keydown", handleEsc);
    return () => document.removeEventListener("keydown", handleEsc);
  }, [isOpen, handleOnOpen]);

  if (!isOpen || !run_data) return null;

  // Helpers
  const formatDate = (isoString) => {
    if (!isoString) return "-";
    const date = new Date(isoString);
    return date.toLocaleString("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    });
  };

  const statusParser = (status) => {
    if (!status) return "-";
    const trimmed = status.trim().toLowerCase();
    if (trimmed === "completed") return "Finished";
    if (trimmed === "loading") return "Loading";
    if (trimmed === "ongoing") return "Ongoing";
    return status; // fallback
  };

  const status = statusParser(run_data.status);
  const getUsername = (email) => email?.split("@")[0] ?? "-";

  return (
    <div className="run-modal__overlay" onClick={handleOnOpen}>
      <div
        className="run-modal__container relative max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* CLOSE BUTTON */}
        <button
          className="run-modal__close absolute top-4 right-4 text-gray-500 hover:text-gray-800 text-2xl"
          onClick={handleOnOpen}
          aria-label="Close modal"
        >
          ✕
        </button>

        {/* HEADER */}
        <div className="run-modal__header mb-6 border-b pb-4">
          <div className="run-modal__header-top">
            <p className="run-modal__header__title">{`RUN-${run_data.id}`}</p>
          </div>
          <div className="run-modal__header-info flex flex-wrap gap-4 mt-2 text-sm text-gray-600">
            <p className="run-modal__header-info__text">{getUsername(run_data.users?.email)}</p>
            <span className="run-modal__header-info__divisor" />
            <p className="run-modal__header-info__text">{run_data.attack_type}</p>
            <span className="run-modal__header-info__divisor" />
            <p className="run-modal__header-info__text">{formatDate(run_data.started_at)}</p>
            <span className="run-modal__header-info__divisor" />
            <p className="run-modal__header-info__text run-modal__header-info__status--finished">{status}</p>
          </div>
        </div>

        {/* BODY */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">

          {/* Attack Configuration */}
          <div>
            <h3 className="font-extrabold mb-1">Attack Configuration</h3>
            <ul className="list-disc list-inside">
              {run_data.attack_type !== "over_refusal_test" ? (
                <>
                  {run_data.template_datasets ? (
                    <>
                      <li>Template: {run_data.template_datasets.name}</li>
                      <li>Target Model: {run_data.target_model}</li>
                    </>
                  ) : (
                    <>
                      <li>Attack Model: {run_data.attack_model ?? "-"}</li>
                      <li>Target Model: {run_data.target_model}</li>
                    </>
                  )}
                </>
              ) : (
                <li>Target Model: {run_data.target_model}</li>
              )}
            </ul>
          </div>

          {/* Metrics */}
          <div>
            <h3 className="font-extrabold mb-1">Metrics</h3>
            <ul className="list-disc list-inside">
              <li>ASR: {run_data.metrics_asr ?? "-"}</li>
              <li>ORR: {run_data.metrics_orr ?? "-"}</li>
              <li>AOR: {run_data.metrics_aor ?? "-"}</li>
              <li>Majority Verdict: {run_data.metrics_veridict_majority?.toString() ?? "-"}</li>
              <li>Static Metric: {run_data.static_metric ?? "-"}</li>
            </ul>
          </div>

          {/* Scenario */}
          <div>
            <h3 className="font-extrabold mb-1">Scenario</h3>
            <p>{run_data.scenarios?.name ?? "-"}</p>
          </div>

          {/* Role Play */}
          <div>
            <h3 className="font-extrabold mb-1">Role Play</h3>
            <p>{run_data.role_play_options?.name ?? "-"}</p>
          </div>

          {/* User */}
          <div>
            <h3 className="font-extrabold mb-1">User</h3>
            <p>{getUsername(run_data.users?.email)}</p>
          </div>

          {/* Template */}
          <div>
            <h3 className="font-extrabold mb-1">Template</h3>
            <p>{run_data.template_datasets?.name ?? "-"}</p>
          </div>

          {/* Dates */}
          <div>
            <h3 className="font-extrabold mb-1">Started At</h3>
            <p>{formatDate(run_data.started_at)}</p>
          </div>
          <div>
            <h3 className="font-extrabold mb-1">Ended At</h3>
            <p>{formatDate(run_data.ended_at)}</p>
          </div>

        </div>
      </div>
    </div>
  );
}

export default RunModal;
