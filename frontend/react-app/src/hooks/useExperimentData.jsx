import { useState, useEffect, useCallback } from "react";

export const useExperimentData = () => {
  const [scenarios, setScenarios] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [rolePlayOptions, setRolePlayOptions] = useState([]);
  const [models, setModels] = useState([]);

  const fetchScenarios = useCallback(async () => {
    const res = await fetch("http://localhost:8000/scenarios");
    if (!res.ok) throw new Error("Failed to fetch scenarios");
    const data = await res.json();
    setScenarios(data.map(s => ({ key: s.id, label: s.description })));
  }, []);

  const fetchTemplates = useCallback(async () => {
    const res = await fetch("http://localhost:8000/template-datasets");
    if (!res.ok) throw new Error("Failed to fetch templates");
    const data = await res.json();
    setTemplates(data.datasets.map(t => ({ key: t.id, label: t.description })));
  }, []);

  const fetchRolePlayOptions = useCallback(async () => {
    const res = await fetch("http://localhost:8000/role-play-options");
    if (!res.ok) throw new Error("Failed to fetch role play options");
    const data = await res.json();
    setRolePlayOptions(data.map(r => ({ key: r.id, label: r.description })));
  }, []);

  const fetchModels = useCallback(async () => {
    const res = await fetch("http://10.3.1.241:8080/api/tags");
    if (!res.ok) throw new Error("Failed to fetch models");
    const data = await res.json();
	if (data.models && Array.isArray(data.models)) {
    setModels(
      (data.models || []).map(m => ({ key: m.name, label: m.name }))
    );
	}
  }, []);

  useEffect(() => {
    fetchScenarios();
    fetchTemplates();
    fetchRolePlayOptions();
    fetchModels();
  }, [
    fetchScenarios,
    fetchTemplates,
    fetchRolePlayOptions,
    fetchModels
  ]);

  return {
    scenarios,
    templates,
    rolePlayOptions,
    models,
    refetch: {
      scenarios: fetchScenarios,
      templates: fetchTemplates,
      rolePlayOptions: fetchRolePlayOptions,
      models: fetchModels
    }
  };
};
