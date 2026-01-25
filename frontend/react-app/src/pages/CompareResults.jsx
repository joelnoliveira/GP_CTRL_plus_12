import React, { useState, useEffect } from "react";
import "../styles/pages/compare_results.css";
import "../styles/pages/home.css";

import { useAuth } from "../context/AuthContext";
import Menu from "../components/Menu";
import DropdownMenu from "../components/DropdownMenu";
import ToggleSwitch from "../components/ToggleSwitch";
import AddIcon from "../components/AddIcon";
import Logo from "../components/Logo";
import CloseIcon from "../components/CloseIcon";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const CompareResults = (
) => {
  const MAX_EXPERIMENTS = 8;
  const { isLoggedIn } = useAuth();

  /* =======================
     Filters
  ======================= */
  const [isOnORR, setIsOnORR] = useState(true);
  const [isOnASR, setIsOnASR] = useState(true);
  const [isOnAOR, setIsOnAOR] = useState(true);
  const [isOnSM, setIsOnSM] = useState(true);

  /* =======================
     Mock Experiments data - Replace With Backend Connection
  ======================= */
  const [experimentsMap, setExperimentsMap] = useState({});

  useEffect(() => {
  const get_results = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch("http://localhost:8000/runs-metrics/me", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
        });
        const data = await response.json();

        const experiments = Object.fromEntries(
        data.map((item) => [
            item.id,
            {
              ORR: item.metrics_orr,
              ASR: item.metrics_asr,
              AOR: item.metrics_aor,
              SM: item.static_metric,
            },
          ])
        );

        const colors = ["#2563eb", "#16a34a", "#dc2626", "#9333ea", "#c5ea33", "#33ccea", "#e133ea", "#000000"];

        const withColors = Object.fromEntries(
          Object.entries(experiments).map(([id, values], i) => [
            id,
            { ...values, color: colors[i % colors.length] },
          ])
        );

        setExperimentsMap(withColors);
      } catch (err) {
        console.error(err);
      }
    };

    get_results();
  }, []);
  
  

  /* =======================
     Selected experiments
  ======================= */
  const [selectedExperiments, setSelectedExperiments] = useState([]);

  const allExperimentNames = Object.keys(experimentsMap);

  const availableExperiments = allExperimentNames.filter(
    (e) => !selectedExperiments.includes(e)
  );

  const canAddExperiment =
    isLoggedIn && //Change to isLoggedIn - just testing
    selectedExperiments.length < MAX_EXPERIMENTS &&
    availableExperiments.length > 0;

  const updateExperiment = (index, newExperiment) => {
    setSelectedExperiments((prev) => {
      // If already selected elsewhere, ignore *Alterar para não deixar selecionar ou wtv*
      if (prev.includes(newExperiment) && prev[index] !== newExperiment) {
        return prev;
      }

      const updated = [...prev];
      updated[index] = newExperiment;
      return updated;
    });
  };

  const addExperiment = () => {
    setSelectedExperiments((prev) => {
      if (prev.length >= MAX_EXPERIMENTS) {
        return prev;
      }

      const available = Object.keys(experimentsMap).filter(
        (e) => !prev.includes(e)
      );

      if (available.length === 0) {
        return prev;
      }

      return [...prev, available[0]];
    });
  };

  /* =======================
     Chart data builder
  ======================= */
  const getChartData = (metric) =>
  selectedExperiments
    .filter((name) => experimentsMap[name])
    .map((name) => ({
      name,
      value: experimentsMap[name][metric],
      color: experimentsMap[name].color,
    }));

  /* =======================
     Chart component
  ======================= */
  const ExperimentBarChart = ({ data }) => (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data} margin={{ bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="name"
          angle={-50} 
          textAnchor="end" 
          interval={0}  
          height={85} />
        <YAxis domain={[0, 1]} />
        <Tooltip />
        <Bar dataKey="value">
          {data.map((entry, index) => (
            <Cell key={index} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );

  return (
    <div className="compare_results">
      <Menu currentPage={"Compare Results"} />

      <div className="compare_results__main_area">
        {isLoggedIn ? ( //Change to isLoggedIn - just testing
        <div className="compare_results__content">

          {/* =======================
              Charts Area
          ======================= */}
          <div className="compare_results__charts">
            {isOnORR && selectedExperiments.length !== 0 && (<div className="chart_card">
              <h3>Over-Refusal Rate</h3>
              <ExperimentBarChart data={getChartData("ORR")} />
            </div>
            )}

            {isOnASR && selectedExperiments.length !== 0 && (<div className="chart_card">
              <h3>Attack Success Rate</h3>
              <ExperimentBarChart data={getChartData("ASR")} />
            </div>
            )}

            {isOnAOR && selectedExperiments.length !== 0 && (<div className="chart_card chart_card--wide">
              <h3>Achieved Objective Rate</h3>
              <ExperimentBarChart data={getChartData("AOR")} />
            </div>
            )}

            {isOnSM && selectedExperiments.length !== 0 && (<div className="chart_card chart_card--wide">
              <h3>Static Metric</h3>
              <ExperimentBarChart data={getChartData("SM")} />
            </div>
            )}

            {!isOnORR && !isOnASR && !isOnAOR && !isOnSM && selectedExperiments.length !== 0 && (
              <div className="warning_message">
                <h1 className="warning_message__text">Please select a metric</h1>
              </div>
            )}

            {selectedExperiments.length === 0 &&(
              <div className="warning_message">
                <h1 className="warning_message__text">Please add an experiment to compare</h1>
              </div>
            )}
          </div>

          {/* =======================
              Side Panel
          ======================= */}
          <div className="compare_results__side_panel">
            <div className="side_card">
              <h4>Experiments to be compared</h4>

              {selectedExperiments.map((exp, index) => {
                const experiment = experimentsMap[exp];
                if (!experiment) return null;

                return (
                  <div key={index} className="experiment_selector">
                    <span
                      className="dot"
                      style={{ backgroundColor: experiment.color }}
                    />
                    <DropdownMenu
                      placeholder={exp}
                      items={Object.keys(experimentsMap)}
                      onSelect={(value) => updateExperiment(index, value)}
                    />

                    <CloseIcon
                      size="small"
                      onClick={() => {
                        setSelectedExperiments((prev) =>
                          prev.filter((_, i) => i !== index)
                        );
                      }}
                    />
                  </div>
                );
              })}

              <AddIcon
                size="medium"
                disabled={!canAddExperiment}
                onClick={addExperiment}
              />

              {!canAddExperiment && (
                <p className="text-xs text-gray-300 mt-2">
                  {selectedExperiments.length >= MAX_EXPERIMENTS
                    ? "Maximum of 8 experiments reached"
                    : "No more experiments available"}
                </p>
              )}
            </div>

            <div className="side_card">
              <h4>Filters</h4>

              <label className="filter_item">
                <ToggleSwitch
                  checked={isOnORR}
                  onChange={setIsOnORR}
                  options={["ORR", "ORR"]}
                  styles="toggle_switch_text"
                />
              </label>

              <label className="filter_item">
                <ToggleSwitch
                  checked={isOnASR}
                  onChange={setIsOnASR}
                  options={["ASR", "ASR"]}
                  styles="toggle_switch_text"
                />
              </label>

              <label className="filter_item">
                <ToggleSwitch
                  checked={isOnAOR}
                  onChange={setIsOnAOR}
                  options={["AOR", "AOR"]}
                  styles="toggle_switch_text"
                />
              </label>

              <label className="filter_item">
                <ToggleSwitch
                  checked={isOnSM}
                  onChange={setIsOnSM}
                  options={["SM", "SM"]}
                  styles="toggle_switch_text"
                />
              </label>
            </div>
          </div>
        </div>
        ):(
          <div className="flex flex-col items-center justify-center h-64">
            <Logo 
              size="large"
            />
            <h2 className="text-xl text-black">Please log in to view results</h2>
            <p className="text-gray-800">Comparison tools are restricted to authenticated users.</p>
          </div>
        )}
      </div>

      {/* Background polygon */}
      <div
        className="home__gray-polygon -z-5"
        style={{ clipPath: "polygon(0% 100%, 100% 0%, 100% 100%)" }}
      />
    </div>
  );
};

export default CompareResults;