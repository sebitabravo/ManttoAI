import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { getOnboardingStatus } from "../../api/onboarding";

/**
 * Componente que verifica si el usuario completó el onboarding.
 *
 * Si el usuario está autenticado pero no completó el onboarding,
 * redirige automáticamente a la página del wizard.
 * Bloquea el render de hijos hasta resolver el primer chequeo
 * para evitar flash del dashboard antes del redirect.
 *
 * Este componente debe usarse dentro de un contexto autenticado.
 */
export default function OnboardingGuard({ children }) {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    async function checkOnboardingStatus() {
      try {
        const status = await getOnboardingStatus();

        // Si no completó el onboarding y no está ya en la página del wizard
        if (!status.onboarding_completed && pathname !== "/onboarding") {
          navigate("/onboarding", { replace: true });
          return;
        }
      } catch (err) {
        console.error("Error al verificar estado del onboarding:", err);
        // Si hay un error de red, mostrar estado de carga y redirigir al onboarding
        // para evitar saltar el wizard involuntariamente
        if (pathname !== "/onboarding") {
          navigate("/onboarding", { replace: true });
          return;
        }
      } finally {
        setChecking(false);
      }
    }

    checkOnboardingStatus();
  }, [pathname, navigate]);

  // Mostrar loading mientras resuelve el estado del onboarding
  // Nunca renderizar hijos hasta confirmar el estado
  if (checking) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-neutral-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    );
  }

  return <>{children}</>;
}
