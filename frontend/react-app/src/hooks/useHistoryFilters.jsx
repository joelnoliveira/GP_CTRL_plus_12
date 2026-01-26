import useFetchData from "./useFetchData";

const API_URL = "http://10.17.0.159:8000/runs-filters";

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
