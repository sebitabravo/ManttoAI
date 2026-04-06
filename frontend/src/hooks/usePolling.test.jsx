import { renderHook, waitFor } from "@testing-library/react";

import usePolling from "./usePolling";

describe("usePolling", () => {
  test("ejecuta fetch inicial y refresco periódico", async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce({ total: 1 })
      .mockResolvedValue({ total: 2 });

    const { result } = renderHook(() => usePolling(fetcher, 25, []));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const callsAfterInitialLoad = fetcher.mock.calls.length;
    expect(callsAfterInitialLoad).toBeGreaterThanOrEqual(1);
    expect([{ total: 1 }, { total: 2 }]).toContainEqual(result.current.data);

    await waitFor(() => {
      expect(fetcher.mock.calls.length).toBeGreaterThan(callsAfterInitialLoad);
    });

    expect(result.current.data).toEqual({ total: 2 });
  });
});
