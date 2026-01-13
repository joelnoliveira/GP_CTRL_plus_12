import React, {useState} from 'react'
import "../styles/pages/compare_results.css";
import "../styles/pages/home.css";
import { useAuth } from '../context/AuthContext';
import Menu from '../components/Menu'
import DropdownMenu from '../components/DropdownMenu'
import ToggleSwitch from '../components/ToggleSwitch'
import AddIcon from '../components/AddIcon'


const CompareResults = (
) => {
  const [isOnORR, setIsOnORR] = useState(false);
  const [isOnASR, setIsOnASR] = useState(false);
  const [isOnAOR, setIsOnAOR] = useState(false);
  const { isLoggedIn, login } = useAuth();

  const handleORR = (newValue) => {
      setIsOnORR(newValue);
  }

  const handleASR = (newValue) => {
      setIsOnASR(newValue);
  }

  const handleAOR = (newValue) => {
      setIsOnAOR(newValue);
  }

  return (
    <div className="compare_results">
      <Menu 
        currentPage={"Compare Results"}
      />

      {/* Main Content Area */}
      <div className="compare_results__main_area">

        {/* Content Wrapper */}
        <div className="compare_results__content">

          {/* Charts Area */}
          <div className="compare_results__charts">
            <div className="chart_card">
              <h3>Over-Refusal Rate</h3>
              <div className="chart_placeholder" />
            </div>

            <div className="chart_card">
              <h3>Attack Success Rate</h3>
              <div className="chart_placeholder" />
            </div>

            <div className="chart_card chart_card--wide">
              <h3>Achieved Objective Rate</h3>
              <div className="chart_placeholder" />
            </div>
          </div>

          {/* Right Panel */}
          <div className="compare_results__side_panel">
            <div className="side_card">
              <h4>Experiments to be compared</h4>

              <div className="experiment_selector blue">
                <span className="dot" />
                <DropdownMenu 
                  placeholder={"Experiment 1"} 
                  items={["Experiment 1"]}
                />
              </div>

              <div className="experiment_selector green">
                <span className="dot" />
                <DropdownMenu 
                  placeholder={"Experiment 2"} 
                  items={["Experiment 2"]}
                />
              </div>

              <AddIcon 
                size='medium'
                disabled={!isLoggedIn}
                onClick={() => console.log("Add clicked!")}
              />
            </div>

            <div className="side_card">
              <h4>Filters</h4>

              <label className="filter_item">
                <ToggleSwitch
                  checked={isOnORR}
                  onChange={handleORR}
                  options={["ORR","ORR"]}
                />
              </label>

              <label className="filter_item">
                <ToggleSwitch
                  checked={isOnASR}
                  onChange={handleASR}
                  options={["ASR","ASR"]}
                />
              </label>

              <label className="filter_item">
                <ToggleSwitch
                  checked={isOnAOR}
                  onChange={handleAOR}
                  options={["AOR","AOR"]}
                />
              </label>
            </div>
          </div>

        </div>
      </div>
      <div
        className="home__gray-polygon -z-5"
        style={{ clipPath: "polygon(0% 100%, 100% 0%, 100% 100%)" }}
      ></div>
    </div>
  )
}

export default CompareResults
