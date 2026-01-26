import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";

const API_BASE_URL = "http://localhost:8000";

// Hardcoded list of available external models
export const AVAILABLE_EXTERNAL_MODELS = [
  { key: "gpt-3.5-turbo", label: "gpt-3.5-turbo" },
  { key: "gpt-5.2-codex", label: "gpt-5.2-codex" },
  { key: "gpt-4o-mini-tts-2025-12-15", label: "gpt-4o-mini-tts-2025-12-15" },
  { key: "gpt-realtime-mini-2025-12-15", label: "gpt-realtime-mini-2025-12-15" },
];

export const PROVIDERS = [
  { key: "OPEN_AI", label: "OpenAI" },
];

export const useApiConfigs = () => {
  const { token } = useAuth();
  const [apiConfigs, setApiConfigs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchConfigs = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api-key-configs/me`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!res.ok) throw new Error("Failed to fetch API configurations");

      const data = await res.json();
      setApiConfigs(data.configs || []);
    } catch (err) {
      console.error("fetchConfigs failed:", err);
      setError(err.message);
      setApiConfigs([]);
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  const createConfig = useCallback(async (configData) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api-key-configs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(configData),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to create API configuration");
      }

      const data = await res.json();
      await fetchConfigs(); // Refresh the list
      return { success: true, data };
    } catch (err) {
      console.error("createConfig failed:", err);
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setIsLoading(false);
    }
  }, [token, fetchConfigs]);

  const updateConfig = useCallback(async (configId, configData) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api-key-configs/${configId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(configData),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to update API configuration");
      }

      const data = await res.json();
      await fetchConfigs(); // Refresh the list
      return { success: true, data };
    } catch (err) {
      console.error("updateConfig failed:", err);
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setIsLoading(false);
    }
  }, [token, fetchConfigs]);

  const deleteConfig = useCallback(async (configId) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api-key-configs/${configId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to delete API configuration");
      }

      await fetchConfigs(); // Refresh the list
      return { success: true };
    } catch (err) {
      console.error("deleteConfig failed:", err);
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setIsLoading(false);
    }
  }, [token, fetchConfigs]);

  useEffect(() => {
    if (token) {
      fetchConfigs();
    }
  }, [token, fetchConfigs]);

  return {
    apiConfigs,
    isLoading,
    error,
    createConfig,
    updateConfig,
    deleteConfig,
    refetch: fetchConfigs,
  };
};
