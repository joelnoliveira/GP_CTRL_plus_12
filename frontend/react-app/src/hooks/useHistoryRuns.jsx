import useFetchData from "./useFetchData";

const API_URL = "http://localhost:8000/history/mock_runs";

export default function useHistoryRuns(filters = {}) {
  const queryParams = new URLSearchParams(
    Object.entries(filters).filter(([_, value]) => value)
  ).toString();

  const url = queryParams ? `${API_URL}?${queryParams}` : API_URL;

  const { data, loading, error } = useFetchData(url, {}, [url]);

  return {
    runs: data ?? [],
    loading,
    error,
  };
}