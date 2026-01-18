import useFetchData from "./useFetchData";

const API_URL = "http://localhost:8000/history/mock_filters";

export default function useHistoryFilters() {
  const { data, loading, error } = useFetchData(API_URL, {}, []);

  return {
    filters: data ?? [],
    loading,
    error,
  };
}
