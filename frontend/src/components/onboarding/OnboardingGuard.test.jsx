import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import { getOnboardingStatus } from "../../api/onboarding";
import useAuth from "../../hooks/useAuth";
import OnboardingGuard from "./OnboardingGuard";

vi.mock("../../api/onboarding", () => ({
  getOnboardingStatus: vi.fn(),
}));

vi.mock("../../hooks/useAuth", () => ({
  default: vi.fn(),
}));

describe("OnboardingGuard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuth.mockReturnValue({ user: { rol: "visualizador" } });
    getOnboardingStatus.mockResolvedValue({ onboarding_completed: false });
  });

  it("deja pasar al visualizador sin consultar el endpoint restringido de onboarding", async () => {
    render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <OnboardingGuard>
          <div data-testid="protected-content">Dashboard demo</div>
        </OnboardingGuard>
      </MemoryRouter>
    );

    expect(await screen.findByTestId("protected-content")).toBeTruthy();
    await waitFor(() => expect(getOnboardingStatus).not.toHaveBeenCalled());
  });
});
