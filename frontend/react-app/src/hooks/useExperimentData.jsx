import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";

export const useExperimentData = () => {
  const { token } = useAuth();
  const [scenarios, setScenarios] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [rolePlayOptions, setRolePlayOptions] = useState([]);
  const [models, setModels] = useState([]);

  const fetchScenarios = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:8000/scenarios", {
                method: "GET",
                headers: {
                  "Content-Type": "application/json",
                  "Authorization": `Bearer ${token}`,
                },
              });
      if (!res.ok) throw new Error("Failed to fetch scenarios");

      const data = await res.json();
      setScenarios(
        Array.isArray(data)
          ? data.map(s => ({ key: s.id, label: s.description }))
          : []
      );
    } catch (err) {
      console.error("fetchScenarios failed:", err);
      setScenarios([]);
    }
  }, []);

  const fetchTemplates = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:8000/template-datasets", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
        });
      if (!res.ok) throw new Error("Failed to fetch templates");

      const data = await res.json();
      setTemplates(
        Array.isArray(data?.datasets)
          ? data.datasets.map(t => ({ key: t.id, label: t.description }))
          : []
      );
    } catch (err) {
      console.error("fetchTemplates failed:", err);
      setTemplates([]);
    }
  }, []);

  const fetchRolePlayOptions = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:8000/role-play-options", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
        });
      if (!res.ok) throw new Error("Failed to fetch role play options");

      const data = await res.json();
      setRolePlayOptions(
        Array.isArray(data)
          ? data.map(r => ({ key: r.id, label: r.description }))
          : []
      );
    } catch (err) {
      console.error("fetchRolePlayOptions failed:", err);
      setRolePlayOptions([]);
    }
  }, []);

  const fetchModels = useCallback(async () => {
    try {
      const res = await fetch("http://10.3.1.241:8080/api/tags");
      if (!res.ok) throw new Error("Failed to fetch models");

      const data = await res.json();
      const modelsArray = Array.isArray(data?.models) ? data.models : [];

      setModels(
        modelsArray.map(m => ({ key: m.name, label: m.name }))
      );
    } catch (err) {
      console.error("fetchModels failed:", err);
      setModels([]);
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
