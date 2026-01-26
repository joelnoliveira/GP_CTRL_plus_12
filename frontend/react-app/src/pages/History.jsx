import React, { useState, useEffect, useRef } from 'react'
import { useAuth } from "../context/AuthContext";

import Menu from '../components/Menu'
import DropdownMenu from '../components/DropdownMenu'
import RunCard from '../components/RunCard'
import Button from '../components/Button'
import Checkbox from '../components/Checkbox';
import ExportIcon from '../components/ExportIcon';
import Toast from '../components/Toast';
import Logo from '../components/Logo';

import useHistoryFilters from "../hooks/useHistoryFilters";
import useHistoryRuns from "../hooks/useHistoryRuns";
import { useExperimentData } from "../hooks/useExperimentData";

import "../styles/pages/history.css"
import RunModal from '../components/RunModal';

const History = () => {
  const { isLoggedIn, user, token, logout} = useAuth();

  const {
    scenarios: scenarioList,
    templates: templateList,
    rolePlayOptions: rolePlayOptionList,
    models: modelList
  } = useExperimentData();

  const [toastConfig, setToastConfig] = useState(null);

  const [selectedFilters, setSelectedFilters] = useState({});
  const { runs, loading, error } = useHistoryRuns(selectedFilters);

  const [showFilters, setShowFilters] = useState(false);
  const [showExportDropdown, setShowExportDropdown] = useState(false);

  const [bulkSelectMode, setBulkSelectMode] = useState(null);
  const [selectedRunIds, setSelectedRunIds] = useState(new Set());

  // MODAL CONTROL
  const [isRunModalOpen, setIsRunModalOpen] = useState(false);
  const [selectedRun, setSelectedRun] = useState(null);

  const exportRef = useRef(null);
  const filtersRef = useRef(null);
  const deleteRef = useRef(null);

  const filters = [
    {
      key: "scenario",
      placeholder: "Scenario",
      items: [
        ...scenarioList.map(s => s.label),
        "Custom",
      ],
    },
    {
      key: "attack_type",
      placeholder: "Attack Type",
      items: ["TEMPLATE_ATTACK", "CRESCENDO_ATTACK", "ROLE_PLAY_ATTACK"],
    },
    {
      key: "attack_model",
      placeholder: "Attack Model",
      items: modelList.map(m => m.label),
    },
    {
      key: "target_model",
      placeholder: "Target Model",
      items: modelList.map(m => m.label),
    },
    {
      key: "template",
      placeholder: "Template",
      items: [
        ...templateList.map(t => t.label),
        "Custom",
      ],
    },
    {
      key: "role_play",
      placeholder: "Role Play",
      items: [
        ...rolePlayOptionList.map(r => r.label),
        "Custom",
      ],
    },
    {
      key: "metric",
      placeholder: "Metric",
      items: ["metrics_aor", "metrics_orr", "metrics_asr", "static_metric"],
      items_labels: [ "AOR", "ORR", "ASR", "Static Metric"],
    },
  ];

  const formatDate = (isoString) => {
    if (!isoString) return "-";
    const date = new Date(isoString);
    return date.toLocaleString("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  };

  const getUsernameFromEmail = (email) => {
    if (!email) return "-";
    return email.split("@")[0];
  };

  const statusParser = (status) => {
    if (status.toLowerCase() === "completed") return "Finished";
    return status; // fallback
  };

  /* ───── UI toggles ───── */

  const handleDelete = async () => {
    const response = await fetch("http://localhost:8000/gdpr/delete", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        }
      });
    
      const newSuccess = { type: "success", message: "Information successfully deleted!" };
      setToastConfig(newSuccess);
      logout();
  };

  const handleShowFilters = () => {
    setShowFilters(prev => !prev);
    setShowExportDropdown(false);
  };

  const handleExportClick = () => {
    setShowExportDropdown(prev => !prev);
    setShowFilters(false);
  };

  const handleRunModalOpen = (run) => {
    setSelectedRun(run);
    setIsRunModalOpen(true);
  };

  const handleRunModalClose = () => {
    setSelectedRun(null);
    setIsRunModalOpen(false);
  };

  /* ───── Manual selection ───── */

  const toggleRunSelection = (runId) => {
    setSelectedRunIds(prev => {
      const next = new Set(prev);
      next.has(runId) ? next.delete(runId) : next.add(runId);
      return next;
    });
  };

  /* ───── Helper: build attack configuration ───── */

  const buildAttackConfiguration = (run) => {
    if (run.attack_type === "over_refusal_test") {
      return {
        type: run.attack_type,
        target_model: run.target_model,
      };
    }
    if (run.attack_template) {
      return {
        type: run.attack_type,
        attack_template: {
          id: run.attack_template.id,
          name: run.attack_template.name,
          description: run.attack_template.description ?? null,
        },
        target_model: run.target_model,
      };
    }
    return {
      type: run.attack_type,
      attack_model: run.attack_model,
      target_model: run.target_model,
    };
  };

  /* ───── Export Runs ───── */

  const exportSelectedRuns = () => {
    if (selectedRunIds.size === 0) return;

    // Collect only selected runs
    const selectedRuns = runs.filter(run => selectedRunIds.has(run.id));

    // Prepare runs with metrics and attack configuration
    const exportedRuns = selectedRuns.map(run => ({
      run_id: run.id,
      run_name: `RUN-${run.id}`,
      user: getUsernameFromEmail(run.users?.email),
      scenario: run.scenarios?.name ?? null,
      role_play: run.role_play_options?.name ?? null,
      started_at: run.started_at,
      ended_at: run.ended_at,
      status: statusParser(run.status.trim()),
      attack_configuration: buildAttackConfiguration(run),
      metrics: {
        ASR: run.metrics_asr,
        ORR: run.metrics_orr,
        AOR: run.metrics_aor,
        majority_verdict: run.metrics_veridict_majority,
        static_metric: run.static_metric,
      },
    }));

    // Export JSON
    const payload = {
      exportedAt: new Date().toISOString(),
      totalRuns: exportedRuns.length,
      runs: exportedRuns,
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `runs_export_${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  /* ───── Bulk selection logic ───── */

  useEffect(() => {
    if (!bulkSelectMode) {
      if (selectedRunIds.size !== 0) {
        setSelectedRunIds(new Set());
      }
      return;
    }

    let nextIds = [];

    if (bulkSelectMode === "page") {
      nextIds = runs.map(r => r.id);
    }

    if (bulkSelectMode === "user" && user) {
      nextIds = runs
        .filter(r => r.users?.email === user.email)
        .map(r => r.id);
    }

    const nextSet = new Set(nextIds);

    // ✅ Prevent infinite loop
    const isSame =
      nextSet.size === selectedRunIds.size &&
      [...nextSet].every(id => selectedRunIds.has(id));

    if (!isSame) {
      setSelectedRunIds(nextSet);
    }
  }, [bulkSelectMode, runs, user, selectedRunIds]);

  /* ───── Click outside ───── */

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (exportRef.current && !exportRef.current.contains(event.target)) setShowExportDropdown(false);
      if (filtersRef.current && !filtersRef.current.contains(event.target)) setShowFilters(false);
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);


  return (
    <div className="history-page">
      <Menu currentPage={"History"} />

      {isLoggedIn ? (
      <div className="history-page__content">
        {toastConfig && (
          <Toast
            icon_size="large"
            type={toastConfig.type}
            message={toastConfig.message}
            onClose={() => setToastConfig(null)} 
          />
        )}

        {/* TOP BAR */}
        <div className="history-page__top-bar">
          <div className="history-page__top-actions">

            {/* DELETE */}
            <div className="relative" ref={deleteRef}>
              <Button size="small" variant="alternative" text="Delete all information" onClick={handleDelete} />
            </div>

            {/* EXPORT */}
            <div className="relative" ref={exportRef}>
              <Button size="small" variant="alternative" text="Export" onClick={handleExportClick} />

              <div className={`dropdown-panel wide-export ${showExportDropdown ? "open" : "closed"}`}>
                <Checkbox
                  label="Select all user's runs"
                  checked={bulkSelectMode === "user"}
                  onChange={(checked) => setBulkSelectMode(checked ? "user" : null)}
                />
                <Checkbox
                  label="Select all runs"
                  checked={bulkSelectMode === "page"}
                  onChange={(checked) => setBulkSelectMode(checked ? "page" : null)}
                />
                <Button
                  size="small"
                  variant="default"
                  disabled={selectedRunIds.size === 0}
                  styles="flex items-center justify-center"
                  onClick={exportSelectedRuns}
                >
                  <ExportIcon size="medium" hasWrapper={false} />
                </Button>
              </div>
            </div>

            {/* FILTERS */}
            <div className="relative" ref={filtersRef}>
              <Button size="small" variant="alternative" text="Filter" onClick={handleShowFilters} />
              <div className={`dropdown-panel wide-filters ${showFilters ? "open" : "closed"}`}>
                {loading && <p>Loading filters...</p>}
                {error && <p className="text-red-500">{error}</p>}
                {!loading && !error &&
                  filters.map((filter, index) => (
                    <DropdownMenu
                      key={index}
                      placeholder={filter.placeholder}
                      items={filter.items_labels ?? filter.items}
                      value={selectedFilters[filter.key]}
                      onSelect={(value) =>
                        setSelectedFilters(prev => ({
                          ...prev,
                          [filter.key]: value,
                        }))
                      }
                      hasDefault={true}
                    />
                  ))}
              </div>
            </div>

          </div>
        </div>

        {/* RUNS */}
        <div className="history-page__runs-container">
          {runs.map((run) => (
            <React.Fragment key={run.id}>
              <RunCard
                run_name_id={`RUN-${run.id}`}
                username={getUsernameFromEmail(run.users?.email)}
                attack_type={run.attack_type}
                date={formatDate(run.started_at)}
                status={statusParser(run.status.trim())}
                attack_model={run.attack_model}
                target_model={run.target_model}
                isPublicValue={run.visibility === "public"}
                exportMode={true}
                isSelected={selectedRunIds.has(run.id)}
                onSelect={() => toggleRunSelection(run.id)}
                onClick={() => handleRunModalOpen(run)}
                canChangeStatus={isLoggedIn && user?.email === run.users?.email}
              />
              {selectedRun && (
                <RunModal run_data={selectedRun} isOpen={isRunModalOpen} handleOnOpen={handleRunModalClose} />
              )}
            </React.Fragment>
          ))}
        </div>

      </div>
      ):(
          <div className="flex flex-col items-center justify-center h-64">
            <Logo 
              size="large"
            />
            <h2 className="text-xl text-black">Please log in to view history</h2>
          </div>
        )}
    </div>
  )
}

export default History;
