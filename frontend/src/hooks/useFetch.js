import { useEffect, useState } from "react";

export default function useFetch(fetcher) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      try {
        const nextData = await fetcher();
        if (active) {
          setData(nextData);
          setError(null);
        }
      } catch (fetchError) {
        if (active) {
          setError(fetchError);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      active = false;
    };
  }, [fetcher]);

  return { data, loading, error };
}
