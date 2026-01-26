import useFetchData from "./useFetchData";

const API_URL = "http://localhost:8000/runs-filters";

export default function useHistoryFilters() {
  const token = localStorage.getItem("token");

  const { data, loading, error } = useFetchData(
    API_URL,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    },
    []
  );

  return {
    filters: data ?? [],
    loading,
    error,
  };
}
