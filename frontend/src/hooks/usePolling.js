import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Polling hook with stale-while-revalidate behavior.
 * Shows old data while fetching new data for smoother UX.
 */
export default function usePolling(fetcher, intervalMs = 15000, initialData = null) {
  const [data, setData] = useState(initialData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Track if we have data to show (for stale-while-revalidate)
  const hasData = useRef(!!initialData);

  const run = useCallback(async () => {
    // Keep showing previous data while fetching (stale-while-revalidate)
    try {
      const nextData = await fetcher();
      setData(nextData);
      hasData.current = true;
      setError(null);
    } catch (fetchError) {
      // If we have previous data, keep showing it instead of error
      if (!hasData.current) {
        setError(fetchError);
      }
    } finally {
      setLoading(false);
    }
  }, [fetcher]);

  useEffect(() => {
    run();
    const timer = window.setInterval(run, intervalMs);
    return () => window.clearInterval(timer);
  }, [intervalMs, run]);

  // Return hasData flag for UI to show staleness indicator
  return { data, loading, error, refresh: run, hasData: hasData.current };
}
