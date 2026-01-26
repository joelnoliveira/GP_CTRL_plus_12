import React, { useState, useEffect } from "react";
import "../styles/pages/run_experiment.css";
import { useAuth } from '../context/AuthContext';
import Menu from '../components/Menu'
import DropdownMenu from '../components/DropdownMenu'
import ToggleSwitch from '../components/ToggleSwitch'
import AddIcon from '../components/AddIcon'
import Button from "../components/Button"
import Toast from "../components/Toast"
import UploadModal from "../components/UploadModal";

import { useExperimentData } from "../hooks/useExperimentData";
import { useApiConfigs } from "../hooks/useApiConfigs";

const RunExperiment = (
) => {
  // Hardcoded list of available external models
  const AVAILABLE_EXTERNAL_MODELS = [
    { key: "gpt-3.5-turbo", label: "gpt-3.5-turbo" },
    { key: "gpt-5.2-codex", label: "gpt-5.2-codex" },
    { key: "gpt-4o-mini-tts-2025-12-15", label: "gpt-4o-mini-tts-2025-12-15" },
    { key: "gpt-realtime-mini-2025-12-15", label: "gpt-realtime-mini-2025-12-15" },
  ];
  const [isPublic, setIsPublic] = useState(false);
  const handleIsPublic = (newValue) => {
    setIsPublic(newValue);
  }

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [uploadTarget, setUploadTarget] = useState(null);

  const [toastConfig, setToastConfig] = useState(null);

  const { isLoggedIn, token } = useAuth(); // From your AuthContext

  const [isLoading, setIsLoading] = useState(false);

  const attackTypeList = ['Attack', 'Attack Template'];
  const [attackType, setAttackType] = useState(attackTypeList[0]);
  const [selections, setSelections] = useState({
    template_datasets: '',
    scenarios: '',
    attack_option: '',
    role_play_options: '',
    attack_model_name: '',
    target_model_name: ''
  });

  // Provider selection: 'DEFAULT' uses 10.17.0.162:3001, 'EXTERNAL' uses external API
  const providerOptions = [
    { key: 'DEFAULT', label: 'Provider LLM (Default)' },
    { key: 'EXTERNAL', label: 'External API' }
  ];
  const [provider, setProvider] = useState('DEFAULT');
  const [selectedApiConfig, setSelectedApiConfig] = useState(null);

  // Get API configs from hook
  const { apiConfigs } = useApiConfigs();

  const handleSelect = (fieldId, value) => {
    setSelections(prev => ({
      ...prev,
      [fieldId]: value
    }));
  };

  // Reset target model when provider changes
  useEffect(() => {
    setSelections(prev => ({ ...prev, target_model_name: '' }));
    if (provider === 'DEFAULT') {
      setSelectedApiConfig(null);
    }
  }, [provider]);

  const [scenarioExpectedFormat, setScenarioExpectedFormat] = useState([{}]);
  const [templateExpectedFormat, setTemplateExpectedFormat] = useState([{}]);
  const [rolePlayExpectedFormat, setRolePlayExpectedFormat] = useState([{}]);

  useEffect(() => {
    const fetchFormats = async () => {
      try {
        const response = await fetch("http://10.17.0.159:8000/files/formats", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
        });
        if (!response.ok) throw new Error("Failed to fetch file formats");
        const data = await response.json();

        const formats = data.formats;


        const normalize = ({ name, label, language, forceArray }) => {
          const entry = formats.find(f => f.name === name);
          if (!entry) return [];

          return [
            {
              label,
              language,
              example: forceArray && !Array.isArray(entry.example)
                ? [entry.example]
                : entry.example
            }
          ];
        };

        setScenarioExpectedFormat(
          normalize({
            name: "scenarios",
            label: "Scenario format",
            language: "json",
            forceArray: true
          })
        );

        setTemplateExpectedFormat(
          normalize({
            name: "template_datasets",
            label: "Template dataset format",
            language: "yaml",
            forceArray: false
          })
        );

        setRolePlayExpectedFormat(
          normalize({
            name: "role_play_options",
            label: "Role play option format",
            language: "yaml",
            forceArray: false
          })
        );

      } catch (err) {
        console.error("Error fetching models:", err);
      }
    };
    fetchFormats();
  }, []);



  const {
    scenarios: scenarioList,
    templates: templateList,
    rolePlayOptions: rolePlayOptionList,
    models: fetchedModels,
    refetch
  } = useExperimentData();

  const [scenarioType, setScenarioType] = useState({});

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

  // Get target models based on provider selection
  const getTargetModels = () => {
    if (provider === 'EXTERNAL') {
      return AVAILABLE_EXTERNAL_MODELS;
    }
    return fetchedModels;
  };

  const attackFormFields = [
    { id: 'attack_option', placeholder: 'Attack LLM Type', options: attackOptionList },
    { id: 'role_play_options', placeholder: 'Role Playing Type', options: rolePlayOptionList },
    { id: 'attack_model_name', placeholder: 'Attack Model', options: fetchedModels },
    { id: 'target_model_name', placeholder: 'Target Model', options: getTargetModels() },
  ];
  const attackTemplateFormFields = [
    { id: 'target_model_name', placeholder: 'Target Model', options: getTargetModels() },
    { id: 'template_datasets', placeholder: 'Template', options: templateList },
  ];
  const attackOverRefusalFields = [
    { id: 'target_model_name', placeholder: 'Target Model', options: getTargetModels() },
  ];

  const getFormFields = () => {
    if (scenarioType.label === "Over Refusal Test") {
      return attackOverRefusalFields;
    } else {
      if (attackType === "Attack") {
        return attackFormFields
      } else {
        return attackTemplateFormFields
      }
    }
  }


  const handleUpload = (id) => () => {
    setUploadTarget(id);
    setIsModalOpen(true);
  };

  const onUploadSuccess = (newData) => {
    const newSuccess = { type: "success", message: "File uploaded and processed!" };
    setToastConfig(newSuccess);
    setIsModalOpen(false);

    refetch[uploadTarget]?.();
  };

  const handleExecute = async () => {
    // Validar que todos os campos foram preenchidos
    if (!selections.target_model_name) {
      const newError = { type: "error", message: "Please select an option for all fields." };
      setToastConfig(newError);
      return;
    }

    // Validate External API Config selection
    if (provider === 'EXTERNAL' && !selectedApiConfig) {
      const newError = { type: "error", message: "Please select an External API Configuration." };
      setToastConfig(newError);
      return;
    }

    setIsLoading(true);
    try {
      let endpoint = "";
      let payload = {};

      // Determine target_provider and api_key based on selection
      const target_provider = provider === 'EXTERNAL' ? 'OPEN_AI' : 'OLLAMA';
      const api_key = provider === 'EXTERNAL' && selectedApiConfig ? selectedApiConfig.api_key : null;

      if (scenarioType.label === "Over Refusal Test") {
        endpoint = "http://10.17.0.159:8000/over-refusal-test"; 
        payload = {
          target_model_name: selections.target_model_name,
          target_provider: target_provider,
          ...(api_key && { api_key })
        };

      } else {
        if (attackType === "Attack") {
          if (!selections.attack_model_name && selections.attack_option && ((selections.attack_option === "ROLE_PLAY_ATTACK") === selections.role_play_options)) {
            const newError = { type: "error", message: "Please select an option for all fields." };
            setToastConfig(newError);
            return;
          }

          endpoint = "http://10.17.0.159:8000/attack"; 
          payload = {
            attack_option: selections.attack_option,
            scenario_id: scenarioType.key,
            target_model_name: selections.target_model_name,
            attacker_model_name: selections.attack_model_name,
            role_play_options: selections.role_play_options,
            target_provider: target_provider,
            ...(api_key && { api_key })
          };
        } else if (attackType === "Attack Template") {
          if (!selections.template_datasets) {
            const newError = { type: "error", message: "Please select an option for all fields." };
            setToastConfig(newError);
            return;
          }

          endpoint = "http://10.17.0.159:8000/attack-template";
          payload = {
            scenario_id: scenarioType.key,
            target_model_name: selections.target_model_name,
            template_dataset_id: selections.template_datasets,
            target_provider: target_provider,
            ...(api_key && { api_key })
          };
        } else {
          const newError = { type: "error", message: "Please select a valid attack option." };
          setToastConfig(newError);
          return;
        }
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000);

      //Fazer a chamada ao backend
      const response = await fetch(endpoint, {
        method: "POST",
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Erro ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      const newSuccess = { type: "success", message: "Attack successfully executed!" };
      setToastConfig(newSuccess);
    } catch (err) {
      if (err.name === 'AbortError') {
        setToastConfig({ type: "caution", message: "Request timed out. The process will continue on the background." });
      } else {
        setToastConfig({ type: "error", message: err.message });
      }
    } finally {
      setIsLoading(false); // 3. Stop loading regardless of success/fail
    }
  };

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

      {uploadTarget === "scenarios" && (
        <UploadModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSuccess={onUploadSuccess}
          targetType={uploadTarget}
          expectedFormats={scenarioExpectedFormat}
        />)
      }
      {uploadTarget === "template_datasets" && (
        <UploadModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSuccess={onUploadSuccess}
          targetType={uploadTarget}
          expectedFormats={templateExpectedFormat}
        />)
      }

      {uploadTarget === "role_play_options" && (
        <UploadModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSuccess={onUploadSuccess}
          targetType={uploadTarget}
          expectedFormats={rolePlayExpectedFormat}
        />)
      }

      {/* Main Content Area */}
      <div className="run_experiment__main_area">
        <div className="run_experiment__card-wrapper">
          {/* The Dark Card Container */}
          <div className="run_experiment__card">
            {/* Form Rows */}
            <div className="run_experiment__dropdown-list">
              <div className="run_experiment__row">
                <DropdownMenu
                  placeholder='Scenario'
                  items={scenarioList.map(opt => opt.label)}
                  value={scenarioType.label}
                  onSelect={(val) =>
                    setScenarioType(
                      scenarioList.find(opt => opt.label === val)
                    )
                  }
                />

                <AddIcon
                  size='large'
                  disabled={!isLoggedIn}
                  onClick={handleUpload("scenarios")}
                />

                {/* <ToggleSwitch
                  checked={isPublic}
                  onChange={handleIsPublic}
                /> */}
              </div>
            </div>
            {scenarioType.label !== "Over Refusal Test" && <div className="run_experiment__dropdown-list">
              <div className="run_experiment__row">
                <DropdownMenu
                  placeholder='Attack type'
                  items={attackTypeList}
                  value={attackType}
                  onSelect={(val) => setAttackType(val)}
                />
              </div>
            </div>}

            {/* Provider Selection */}
            <div className="run_experiment__dropdown-list">
              <div className="run_experiment__row">
                <DropdownMenu
                  placeholder='Target Provider'
                  items={providerOptions.map(opt => opt.label)}
                  value={providerOptions.find(opt => opt.key === provider)?.label}
                  onSelect={(val) => setProvider(providerOptions.find(opt => opt.label === val)?.key)}
                />
              </div>
            </div>

            {/* External API Config Selection (only when EXTERNAL is selected) */}
            {provider === 'EXTERNAL' && (
              <div className="run_experiment__dropdown-list">
                <div className="run_experiment__row">
                  <DropdownMenu
                    placeholder='Select API Configuration'
                    items={apiConfigs.map(cfg => cfg.name)}
                    value={selectedApiConfig?.name}
                    onSelect={(val) => setSelectedApiConfig(apiConfigs.find(cfg => cfg.name === val))}
                  />
                </div>
              </div>
            )}

            {getFormFields().map((field) => {
              if (field.id === "role_play_options" && selections.attack_option !== "ROLE_PLAY_ATTACK") {
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
                  {(field.id === "template_datasets" || field.id === "role_play_options") && (
                    <AddIcon
                      size='large'
                      disabled={!isLoggedIn}
                      onClick={handleUpload(field.id)}
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
