import useFetchData from "./useFetchData";

const API_URL = "http://localhost:8000/history/mock_runs";

export default function useHistoryRuns() {
  const { data, loading, error } = useFetchData(API_URL, {}, []);

  return {
    runs: data ?? [],
    loading,
    error,
  };
}
