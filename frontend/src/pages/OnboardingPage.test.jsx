import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import useAuth from "../hooks/useAuth";
import OnboardingPage from "./OnboardingPage";

vi.mock("../hooks/useAuth", () => ({
  default: vi.fn(),
}));

vi.mock("../components/onboarding/OnboardingWizard", () => ({
  default: () => <div data-testid="onboarding-wizard">Wizard</div>,
}));

describe("OnboardingPage", () => {
  it("redirige al visualizador al dashboard sin montar el wizard", async () => {
    useAuth.mockReturnValue({ user: { rol: "visualizador" } });

    render(
      <MemoryRouter initialEntries={["/onboarding"]}>
        <Routes>
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="/dashboard" element={<div data-testid="dashboard">Dashboard</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByTestId("dashboard")).toBeTruthy();
    expect(screen.queryByTestId("onboarding-wizard")).toBeNull();
  });
});
