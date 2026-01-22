import React, { useState, useEffect } from "react";
import "../styles/pages/run_experiment.css";
import { useAuth } from '../context/AuthContext';
import Menu from '../components/Menu'
import DropdownMenu from '../components/DropdownMenu'
import ToggleSwitch from '../components/ToggleSwitch'
import AddIcon from '../components/AddIcon'
import Button from "../components/Button"
import Toast from "../components/Toast"

const RunExperiment = (
) => {
  const [isPublic, setIsPublic] = useState(false);
  const handleIsPublic = (newValue) => {
      setIsPublic(newValue);
  }

  const [toastConfig, setToastConfig] = useState(null);

  const { isLoggedIn, login } = useAuth(); // From your AuthContext

  const [isLoading, setIsLoading] = useState(false);

  const attackTypeList = ['Attack','Attack Template'];
  const [attackType, setAttackType] = useState(attackTypeList[0]);
  const [selections, setSelections] = useState({
    template_path: '',
    scenario: '',
    attack_option: '',
    role_play_option: '',
    attack_model_name: '',
    target_model_name: ''
  });

  const handleSelect = (fieldId, value) => {
    setSelections(prev => ({
      ...prev,
      [fieldId]: value
    }));
  };

  /*
  Adicioanr logica para ir buscar isto ao backend
  */
  const [fetchedModels, setFetchedModels] = useState([
    {
      key: '',
      label: ''
    }
  ]);
  const scenarioList = [
    {
      key: 'malicious_goals',
      label: 'External Attacker (Malicious)'
    },
    {
      key: 'vulnerable_goals',
      label: 'Internal Threat Actor (Vulnerable)'
    }
  ];
  const templateList = [
    {
      key: 'datasets/pliny_prompts_escaped.yaml',
      label: 'L1B3RT4S'
    },
    {
      key: 'datasets/JailBreakV_28K_clean.yaml',
      label: 'JailBreakV-28K'
    }
  ];
  const attackOptionList = [
    {
      key: 'CRESCENDO_ATTACK',
      label: 'Crescendo'
    },
    {
      key: 'ROLE_PLAY_ATTACK',
      label: 'Role Playing'
    }
  ]
  const rolePlayOptionList = [
    {
      key: 'VIDEO_GAME',
      label: 'Video-game'
    },
    {
      key: 'MR_ROBOT',
      label: 'Mr. Robot'
    } 
  ]

  const attackFormFields = [
    { id: 'scenario', placeholder: 'Scenario', options: scenarioList },
    { id: 'attack_option', placeholder: 'Attack LLM Type', options: attackOptionList },
    { id: 'role_play_option', placeholder: 'Role Playing Type', options: rolePlayOptionList },
    { id: 'attack_model_name', placeholder: 'Attack Model', options: fetchedModels },
    { id: 'target_model_name', placeholder: 'Target Model', options: fetchedModels },
  ]; 
  const attackTemplateFormFields = [
    { id: 'scenario', placeholder: 'Scenario', options: scenarioList },
    { id: 'target_model_name', placeholder: 'Target Model', options: fetchedModels },
    { id: 'template_path', placeholder: 'Template', options: templateList },
  ];

  const getFormFields = () => {
    if (attackType === "Attack") { 
      return attackFormFields
    } else {
      return attackTemplateFormFields
    }
  }

const handleExecute = async () => {
  // Validar que todos os campos foram preenchidos
  if (!selections.scenario || !selections.target_model_name) {
    const newError = {type: "error", message: "Please select an option for all fields."};
    setToastConfig(newError);
    return;
  }

  setIsLoading(true);
  try {
    let endpoint = "";
    let payload = {};

    if (attackType === "Attack") {
      if (!selections.attack_model_name && selections.attack_option && ((selections.attack_option==="ROLE_PLAY_ATTACK") === selections.role_play_option)) {
        const newError = {type: "error", message: "Please select an option for all fields."};
        setToastConfig(newError);
        return;
      }

      endpoint = "http://localhost:8000/attack"; 
      payload = {
        attack_option: selections.attack_option,
        label: selections.scenario,
        target_model_name: selections.target_model_name,
        attacker_model_name: selections.attack_model_name,        
        role_play_option: selections.role_play_option
      };
    } else if (attackType === "Attack Template") {
      if (!selections.template_path) {
        const newError = {type: "error", message: "Please select an option for all fields."};
        setToastConfig(newError);
        return;
      }

      endpoint = "http://localhost:8000/attack-template";
      payload = {
        label: selections.scenario,
        target_model_name: selections.target_model_name,
        template_path: selections.template_path
      };
    } else {
      const newError = {type: "error", message: "Please select a valid attack option."};
      setToastConfig(newError);
      return;
    }

    //Fazer a chamada ao backend
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Erro ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log("Attack successfully executed!", data);
    /**
     * Logica de mostrar o ataque no frontend (Usar um modal que tá no historico talvez)
     */
    const newSuccess = {type: "success", message: "Attack successfully executed!"};
    setToastConfig(newSuccess);
  } catch (err) {
    console.error("Error executing attack:", err);
    const newError = { type: "error", message: `Error executing attack: ${err.message}.`};
    setToastConfig(newError);
  } finally {
    setIsLoading(false); // 3. Stop loading regardless of success/fail
  }
};

  useEffect(() => {
    const fetchModels = async () => {
      try {
        console.log("teste")
        const response = await fetch("http://10.3.1.241:8080/api/tags", {
          method: "GET"
        });
        console.log(response)
        if (!response.ok) throw new Error("Failed to fetch models");
        const data = await response.json();
        console.log(data)
        if (data.models && Array.isArray(data.models)) {
          const models = data.models.map(m => {
            return {
              key: m.name,
              label: m.name
            };
          });
          setFetchedModels(models);
          console.log(models)
        }
      } catch (err) {
        console.error("Error fetching models:", err);
      }
    };
    fetchModels();
  }, []);

  return (
    <div className="run_experiment"> 
      <Menu 
        currentPage={"Run Experiment"}
      />

      {toastConfig && (
				<Toast
					icon_size="large"
					type={toastConfig.type}
					message={toastConfig.message}
					onClose={() => setToastConfig(null)} 
				/>
			)}

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
                  items={attackTypeList}
                  value={attackType}
                  onSelect={(val) => setAttackType(val)}
                />
                <ToggleSwitch
                  checked={isPublic}
                  onChange={handleIsPublic}
                />
              </div>
            </div>
            
            {getFormFields().map((field) => {
              if (field.id === "role_play_option" && selections.attack_option !== "ROLE_PLAY_ATTACK") {
                return null;
              };

              return (
                <div key={field.id} className='run_experiment__row'>
                  <DropdownMenu
                    placeholder={field.placeholder}
                    items={field.options.map(opt => opt.label)}
                    value={selections[field.id]?.label}
                    onSelect={(val) =>
                      handleSelect(
                        field.id,
                        field.options.find(opt => opt.label === val).key
                      )
                    }
                  />
                  {(field.id === "scenario" || field.id === "template_path") && (
                  <AddIcon
                    size='large'
                    disabled={!isLoggedIn}
                    onClick={() => console.log('Add clicked!')}
                  />)
                  }
                </div>
              );
            })}
          </div>

          <Button
            onClick={handleExecute}
            type="submit"
            variant="default"
            size="large"
            styles="w-full mt-6"
            text={isLoading ? "Processing..." : "Execute Attack"} // Change text
            disabled={!isLoggedIn || isLoading}
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
