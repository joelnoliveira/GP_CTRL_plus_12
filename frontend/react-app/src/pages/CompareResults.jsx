import React, { useState } from "react";
import "../styles/pages/compare_results.css";
import "../styles/pages/home.css";

import { useAuth } from "../context/AuthContext";
import Menu from "../components/Menu";
import DropdownMenu from "../components/DropdownMenu";
import ToggleSwitch from "../components/ToggleSwitch";
import AddIcon from "../components/AddIcon";
import Logo from "../components/Logo";

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

  /* =======================
     Mock Experiments data - Replace With Backend Connection
  ======================= */
  const experimentsMap = {
    "Experiment 1": { ORR: 0.6, ASR: 0.8, AOR: 0.7, color: "#2563eb" },
    "Experiment 2": { ORR: 0.3, ASR: 0.6, AOR: 0.1, color: "#16a34a" },
    "Experiment 3": { ORR: 0.5, ASR: 0.3, AOR: 0.9, color: "#dc2626" },
    "Experiment 4": { ORR: 0.6, ASR: 0.8, AOR: 0.7, color: "#2563eb" },
    "Experiment 5": { ORR: 0.3, ASR: 0.6, AOR: 0.1, color: "#16a34a" },
    "Experiment 6": { ORR: 0.5, ASR: 0.3, AOR: 0.9, color: "#dc2626" },
    "Experiment 7": { ORR: 0.6, ASR: 0.8, AOR: 0.7, color: "#2563eb" },
    "Experiment 8": { ORR: 0.3, ASR: 0.6, AOR: 0.1, color: "#16a34a" },
    "Experiment 9": { ORR: 0.5, ASR: 0.3, AOR: 0.9, color: "#dc2626" },
    "Experiment 10": { ORR: 0.6, ASR: 0.8, AOR: 0.7, color: "#2563eb" },
    "Experiment 11": { ORR: 0.3, ASR: 0.6, AOR: 0.1, color: "#16a34a" },
    "Experiment 12": { ORR: 0.5, ASR: 0.3, AOR: 0.9, color: "#dc2626" },
  };

  /* =======================
     Selected experiments
  ======================= */
  const [selectedExperiments, setSelectedExperiments] = useState([
    "Experiment 1",
    "Experiment 2",
  ]);

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
    selectedExperiments.map((name) => ({
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
            <div className="chart_card">
              <h3>Over-Refusal Rate</h3>
              {isOnORR && (
                <ExperimentBarChart data={getChartData("ORR")} />
              )}
            </div>

            <div className="chart_card">
              <h3>Attack Success Rate</h3>
              {isOnASR && (
                <ExperimentBarChart data={getChartData("ASR")} />
              )}
            </div>

            <div className="chart_card chart_card--wide">
              <h3>Achieved Objective Rate</h3>
              {isOnAOR && (
                <ExperimentBarChart data={getChartData("AOR")} />
              )}
            </div>
          </div>

          {/* =======================
              Side Panel
          ======================= */}
          <div className="compare_results__side_panel">
            <div className="side_card">
              <h4>Experiments to be compared</h4>

              {selectedExperiments.map((exp, index) => (
                <div key={index} className="experiment_selector">
                  <span
                    className="dot"
                    style={{
                      backgroundColor: experimentsMap[exp].color,
                    }}
                  />
                  <DropdownMenu
                    placeholder={exp}
                    items={Object.keys(experimentsMap)}
                    onSelect={(value) =>
                      updateExperiment(index, value)
                    }
                  />
                </div>
              ))}

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
                />
              </label>

              <label className="filter_item">
                <ToggleSwitch
                  checked={isOnASR}
                  onChange={setIsOnASR}
                  options={["ASR", "ASR"]}
                />
              </label>

              <label className="filter_item">
                <ToggleSwitch
                  checked={isOnAOR}
                  onChange={setIsOnAOR}
                  options={["AOR", "AOR"]}
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