import { Navigate } from "react-router-dom";

import OnboardingWizard from "../components/onboarding/OnboardingWizard";
import useAuth from "../hooks/useAuth";
import { canManageOnboarding } from "../utils/onboardingAccess";

/**
 * Página del wizard de onboarding.
 *
 * Esta página muestra el componente del wizard que guía al usuario
 * a través de la configuración inicial del sistema.
 */
export default function OnboardingPage() {
  const { user } = useAuth();

  if (!canManageOnboarding(user)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <OnboardingWizard />;
}
