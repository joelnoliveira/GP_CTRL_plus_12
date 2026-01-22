import React, { useState, useEffect, useRef } from 'react'
import { useAuth } from "../context/AuthContext";

import Menu from '../components/Menu'
import DropdownMenu from '../components/DropdownMenu'
import RunCard from '../components/RunCard'
import Button from '../components/Button'
import Checkbox from '../components/Checkbox';
import ExportIcon from '../components/ExportIcon';

import useHistoryFilters from "../hooks/useHistoryFilters";
import useHistoryRuns from "../hooks/useHistoryRuns";

import "../styles/pages/history.css"
import RunModal from '../components/RunModal';

const History = () => {
  const { isLoggedIn, user } = useAuth();
  const { filters } = useHistoryFilters();

  const [selectedFilters, setSelectedFilters] = useState({});
  const { runs, loading, error } = useHistoryRuns(selectedFilters);

  const [showFilters, setShowFilters] = useState(false);
  const [showExportDropdown, setShowExportDropdown] = useState(false);

  const [bulkSelectMode, setBulkSelectMode] = useState(null);
  // null | "page" | "user"

  const [selectedRunIds, setSelectedRunIds] = useState(new Set());

  // MODAL CONTROL
  const [isRunModalOpen, setIsRunModalOpen] = useState(false);
  const [selectedRun, setSelectedRun] = useState(null);

  const exportRef = useRef(null);
  const filtersRef = useRef(null);

  /* ───── UI toggles ───── */

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

  /* ───── Export Runs ───── */

  const exportSelectedRuns = () => {
    if (selectedRunIds.size === 0) return;

    // 1️⃣ Collect full run objects
    const selectedRuns = runs.filter(run =>
      selectedRunIds.has(run.run_name_id)
    );

    // 2️⃣ Convert to JSON
    const json = JSON.stringify(
      {
        exportedAt: new Date().toISOString(),
        totalRuns: selectedRuns.length,
        runs: selectedRuns,
      },
      null,
      2
    );

    // 3️⃣ Create a downloadable blob
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    // 4️⃣ Trigger download
    const link = document.createElement("a");
    link.href = url;
    link.download = `runs_export_${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();

    // 5️⃣ Cleanup
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  /* ───── Bulk selection logic (ONE EFFECT ONLY) ───── */

  useEffect(() => {
    if (bulkSelectMode === "page") {
      setSelectedRunIds(new Set(runs.map(r => r.run_name_id)));
    }

    else if (bulkSelectMode === "user" && user) {
      const userRuns = runs
        .filter(r => r.username === user.username)
        .map(r => r.run_name_id);

      setSelectedRunIds(new Set(userRuns));
    }

    else if (bulkSelectMode === null) {
      setSelectedRunIds(new Set());
    }
  }, [bulkSelectMode, runs, user]);

  /* ───── Click outside ───── */

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (exportRef.current && !exportRef.current.contains(event.target)) {
        setShowExportDropdown(false);
      }

      if (filtersRef.current && !filtersRef.current.contains(event.target)) {
        setShowFilters(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="history-page">
      <Menu currentPage="History" />

      <div className="history-page__content">

        {/* TOP BAR */}
        <div className="history-page__top-bar">
          <div className="history-page__top-actions">

            {/* EXPORT */}
            <div className="relative" ref={exportRef}>
              <Button
                size="small"
                variant="alternative"
                text="Export"
                onClick={handleExportClick}
              />

              <div className={`dropdown-panel wide-export ${showExportDropdown ? "open" : "closed"}`}>

                <Checkbox
                  label="Select all current user's runs"
                  checked={bulkSelectMode === "user"}
                  onChange={(checked) =>
                    setBulkSelectMode(checked ? "user" : null)
                  }
                />

                <Checkbox
                  label="Select all runs in page"
                  checked={bulkSelectMode === "page"}
                  onChange={(checked) =>
                    setBulkSelectMode(checked ? "page" : null)
                  }
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
              <Button
                size="small"
                variant="alternative"
                text="Filter"
                onClick={handleShowFilters}
              />

              <div className={`dropdown-panel wide-filters ${showFilters ? "open" : "closed"}`}>
                {loading && <p>Loading filters...</p>}
                {error && <p className="text-red-500">{error}</p>}

                {!loading && !error &&
                  filters.map((filter, index) => (
                    <DropdownMenu
                      key={index}
                      placeholder={filter.placeholder}
                      items={filter.items}
                      value={selectedFilters[filter.key]}
                      onSelect={(value) =>
                        setSelectedFilters(prev => ({
                          ...prev,
                          [filter.key]: value,
                        }))
                      }
                    />
                  ))}
              </div>
            </div>

          </div>
        </div>

        {/* RUNS */}
        <div className="history-page__runs-container">
          {runs.map((run, index) => (
            <>
              <RunCard
                key={index}
                run_name_id={run.run_name_id}
                username={run.username}
                attack_type={run.attack_type}
                date={run.date}
                status={run.status.charAt(0).toUpperCase() + run.status.slice(1)}
                attack_model={run.attack_model}
                target_model={run.target_model}
                isPublicValue={run.isPublicValue}
                exportMode={true}
                isSelected={selectedRunIds.has(run.run_name_id)}
                onSelect={() => toggleRunSelection(run.run_name_id)}
                onClick={() => handleRunModalOpen(run)}
                canChangeStatus={isLoggedIn && user?.username === run.username}
              />
            
              {selectedRun && (
                <RunModal
                  run_data={selectedRun}
                  isOpen={isRunModalOpen}
                  handleOnOpen={handleRunModalClose}
                />
              )}
            </>
          ))}
        </div>

      </div>
    </div>
  )
}

export default History;
