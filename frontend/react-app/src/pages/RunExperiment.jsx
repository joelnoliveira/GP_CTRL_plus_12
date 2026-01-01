import React, { useState, useEffect } from "react";
import "../styles/pages/run_experiment.css";
import { useAuth } from '../context/AuthContext';
import Menu from '../components/Menu'
import DropdownMenu from '../components/DropdownMenu'
import ToggleSwitch from '../components/ToggleSwitch'
import AddIcon from '../components/AddIcon'
import Button from "../components/Button"

const RunExperiment = (
) => {
  const [isPublic, setIsPublic] = useState(false);
  const handleIsPublic = (newValue) => {
      setIsPublic(newValue);
  }

  const { isLoggedIn, login } = useAuth(); // From your AuthContext

  /*
  Adicioanr logica para ir buscar isto ao backend
  */
  const models = ['Model 1','Model 2', 'Model 3'];
  const scenarioList = ['Scenario 1','Scenario 2','Scenario 3'];
  const workloadList = ['Workload 1','Workload 2','Workload 3'];
  const attackList = ['Attack 1','Attack 2','Attack 3'];

  const formFields = [
    { id: 'target', placeholder: 'Target LLM', options: models },
    { id: 'scenario', placeholder: 'Scenario', options: scenarioList },
    { id: 'workload', placeholder: 'Workload', options: workloadList },
    { id: 'jury', placeholder: 'Jury Model', options: models },
    { id: 'attack', placeholder: 'Attack LLM', options: models },
  ];

  return (
    <div className="run_experiment"> 
      <Menu 
        currentPage={"Run Experiment"}
      />

      {/* Main Content Area */}
      <div className="run_experiment__main_area">
        <div className="run_experiment__card-wrapper">
          {/* The Dark Card Container */}
          <div className="run_experiment__card">
            {/* Form Rows */}
            <div className="run_experiment__dropdown-list">
              <div className="run_experiment__row">
                <DropdownMenu
                  placeholder='Attack type'
                  items={attackList}
                />
                <ToggleSwitch
                  checked={isPublic}
                  onChange={handleIsPublic}
                />
              </div>
            </div>

            {formFields.map((field) => (
              <div key={field.id} className="run_experiment__row">
                <DropdownMenu 
                  placeholder={field.placeholder} 
                  items={field.options}
                />
                <AddIcon 
                  size='large'
                  disabled={!isLoggedIn}
                  onClick={() => console.log("Add clicked!")}
                />
              </div>
            ))}
          </div>

          <Button
            type="submit"
            variant="default"
            size="large"
            text="Execute Attack"
            styles="w-full mt-6"
            disabled={!isLoggedIn}
          />
        </div>
      </div>

      <div
        className="home__gray-polygon -z-5"
        style={{ clipPath: "polygon(0% 100%, 100% 0%, 100% 100%)" }}
      ></div>
      
    </div>
  )
}

export default RunExperiment
