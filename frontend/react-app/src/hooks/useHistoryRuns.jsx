import { useEffect } from "react";
import useFetchData from "./useFetchData";

//const API_URL = "http://localhost:8000/history/mock_runs";
const API_URL = "http://localhost:8000/run-metrics";

export default function useHistoryRuns(filters = {}) {
  const queryParams = new URLSearchParams(
    Object.entries(filters).filter(([_, value]) => value)
  ).toString();

  const url = queryParams ? `${API_URL}?${queryParams}` : API_URL;

  const { data, loading, error } = useFetchData(url, {}, [url]);

  useEffect(() => {
    console.log("Fetching runs data with filters:", filters);
  }, []);

  return {
    runs: data ?? [],
    loading,
    error,
  };
}