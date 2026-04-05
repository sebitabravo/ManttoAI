import { useCallback, useEffect, useState } from "react";

export default function usePolling(fetcher, intervalMs = 15000, initialData = null) {
  const [data, setData] = useState(initialData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const run = useCallback(async () => {
    setLoading(true);
    try {
      const nextData = await fetcher();
      setData(nextData);
      setError(null);
    } catch (fetchError) {
      setError(fetchError);
    } finally {
      setLoading(false);
    }
  }, [fetcher]);

  useEffect(() => {
    run();
    const timer = window.setInterval(run, intervalMs);
    return () => window.clearInterval(timer);
  }, [intervalMs, run]);

  return { data, loading, error, refresh: run };
}
