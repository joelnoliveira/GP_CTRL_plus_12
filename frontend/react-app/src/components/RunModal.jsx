import React, { useState, useEffect } from 'react';
import ToggleSwitch from '../components/ToggleSwitch';
import "../styles/components/run_modal.css";

function RunModal({ 
    run_data,
    isOpen,
    handleOnOpen,
}) {

    const status_class = run_data.status === "Ongoing"
    ? "run-modal__header-info__status--ongoing"
    : run_data.status === "Loading" 
    ? "run-modal__header-info__status--loading"
    : run_data.status === "Finished"
    ? "run-modal__header-info__status--finished" 
    : ""

    //* ESC key handler */
    useEffect(() => {
        if (!isOpen) return;

        const handleEsc = (event) => {
        if (event.key === "Escape") {
            handleOnOpen();
        }
        };

        document.addEventListener("keydown", handleEsc);
        return () => document.removeEventListener("keydown", handleEsc);
    }, [isOpen, handleOnOpen]);

  /* Safe early return AFTER hooks */
  if (!isOpen || !run_data) return null;
    return (
        /* OVERLAY */
        <div
        className="run-modal__overlay"
        onClick={handleOnOpen} // click outside closes modal
        >
        {/* MODAL CARD */}
        <div
            className="run-modal__container"
            onClick={(e) => e.stopPropagation()} // prevent closing when clicking inside
        >
            {/* CLOSE BUTTON */}
            <button
            className="run-modal__close"
            onClick={handleOnOpen}
            aria-label="Close modal"
            >
            ✕
            </button>

            {/* HEADER */}
            <div className="run-modal__header">
            <div className="run-modal__header-top">
                <p className="run-modal__header__title">
                    {run_data.run_name_id}
                </p>
            </div>

            <div className="run-modal__header-info">
                <p className="run-modal__header-info__text">
                {run_data.username}
                </p>

                <span className="run-modal__header-info__divisor" />

                <p className="run-modal__header-info__text">
                {run_data.attack_type}
                </p>

                <span className="run-modal__header-info__divisor" />

                <p className="run-modal__header-info__text">
                {run_data.date}
                </p>

                <span className="run-modal__header-info__divisor" />

                <p
                className={`run-modal__header-info__text ${status_class}`}
                >
                {run_data.status === "Loading"
                    ? `${run_data.status}...`
                    : run_data.status}
                </p>
            </div>
            </div>
        </div>
        </div>
    );
}

export default RunModal;
