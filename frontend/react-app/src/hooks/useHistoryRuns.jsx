import { useEffect } from "react";
import useFetchData from "./useFetchData";

const API_URL = "http://localhost:8000/runs-metrics";

export default function useHistoryRuns(filters = {}) {
  const queryParams = new URLSearchParams(
    Object.entries(filters).filter(([_, value]) => value)
  ).toString();

  const url = queryParams ? `${API_URL}?${queryParams}` : API_URL;

  const token = localStorage.getItem("token");

  const { data, loading, error } = useFetchData(
    url,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    },
    [url]
  );

  return {
    runs: data ?? [],
    loading,
    error,
  };
}


//const API_URL = "http://localhost:8000/history/mock_runs";