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
    { id: 'template_path', placeholder: 'Template', options: templateList },
  ]; 
  const attackTemplateFormFields = [
    { id: 'scenario', placeholder: 'Scenario', options: scenarioList },
    { id: 'target_model_name', placeholder: 'Target Model', options: fetchedModels },
    { id: 'template_path', placeholder: 'Template', options: templateList },
  ];

  const getFormFields = () => {
    if (attackType == "Attack") { 
      return attackFormFields
    } else {
      return attackTemplateFormFields
    }
  }

const handleExecute = async () => {
  // Validar que todos os campos obrigatórios foram preenchidos
  if (!selections.scenario || !selections.target_model_name) {
    alert("Por favor preenche todos os campos obrigatórios");
    return;
  }

  try {
    let endpoint = "";
    let payload = {};

    if (attackType === "Attack") {
      // Validação específica para Attack
      if (!selections.template_path) {
        alert("Por favor seleciona um template para o ataque");
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
      // Validação específica para Attack Template
      if (!selections.template_path) {
        alert("Por favor seleciona um template");
        return;
      }

      endpoint = "http://localhost:8000/attack-template";
      payload = {
        label: selections.scenario,
        target_model_name: selections.target_model_name,
        template_path: selections.template_path
      };
    } else {
      alert("Por favor seleciona um tipo de ataque válido");
      return;
    }

    // Fazer a chamada ao backend
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
    console.log("Ataque executado com sucesso:", data);
    alert("Ataque iniciado com sucesso!");

  } catch (err) {
    console.error("Erro ao executar ataque:", err);
    alert(`Erro ao executar ataque: ${err.message}`);
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
                  <AddIcon
                    size='large'
                    disabled={!isLoggedIn}
                    onClick={() => console.log('Add clicked!')}
                  />
                </div>
              );
            })}
          </div>

          <Button
            onClick={handleExecute}
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
