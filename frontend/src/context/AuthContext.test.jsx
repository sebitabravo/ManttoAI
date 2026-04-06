import { render, screen, waitFor } from "@testing-library/react";

vi.mock("../api/auth", () => ({
  getCurrentUser: vi.fn(),
  logout: vi.fn(),
}));

import { getCurrentUser } from "../api/auth";
import { AuthProvider, AuthContext } from "./AuthContext";

function AuthProbe() {
  return (
    <AuthContext.Consumer>
      {(value) => (
        <div>
          <span data-testid="resolved">{String(value?.isAuthResolved)}</span>
          <span data-testid="authenticated">{String(value?.isAuthenticated)}</span>
          <span data-testid="user-email">{value?.user?.email || ""}</span>
        </div>
      )}
    </AuthContext.Consumer>
  );
}

describe("AuthProvider", () => {
  test("limpia sesión local cuando el backend rechaza restauración", async () => {
    window.sessionStorage.setItem(
      "manttoai_user",
      JSON.stringify({ email: "stale@example.com" })
    );
    getCurrentUser.mockRejectedValueOnce(new Error("401"));

    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("resolved").textContent).toBe("true");
    });

    expect(screen.getByTestId("authenticated").textContent).toBe("false");
    expect(screen.getByTestId("user-email").textContent).toBe("");
    expect(window.sessionStorage.getItem("manttoai_user")).toBeNull();
  });
});
