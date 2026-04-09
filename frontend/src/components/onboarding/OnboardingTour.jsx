import { useCallback, useEffect, useId, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import useAuth from "../../hooks/useAuth";
import Logo from "../ui/Logo";
import Button from "../ui/Button";

/**
 * Tour de onboarding guiado para nuevos usuarios.
 *
 * Recorre las secciones clave de la app con spotlight + tooltip:
 *   1. Bienvenida — modal centrado de presentación
 *   2. Sidebar — navegación principal
 *   3. Dashboard: Resumen — métricas operacionales
 *   4. Dashboard: Gráficos — tendencias de sensores
 *   5. Equipos — gestión de activos monitoreados
 *   6. Alertas — monitoreo de alertas activas
 *   7. Historial — trazabilidad y reportes
 *   8. Admin (solo rol admin) — panel de administración
 *
 * Comportamiento:
 * - Se muestra solo la primera vez (localStorage flag)
 * - Overlay semitransparente + spotlight sobre el elemento destacado
 * - Navega automáticamente a la ruta de cada paso
 * - Diferencia pasos según rol del usuario (admin ve paso extra)
 * - Cierre con Escape, botón Saltar, o click fuera
 * - Focus trap dentro del tooltip
 * - Respeta prefers-reduced-motion
 *
 * Selectores: usa `data-tour` attributes en las páginas para establecer
 * los elementos a destacar. Ver cada página para los atributos.
 */

const STORAGE_KEY = "manttoai_onboarding_done";

/**
 * Definición base de los pasos del tour.
 * Los pasos con `adminOnly: true` se incluyen solo si el usuario es admin.
 * El paso con `tipo: "welcome"` se muestra como modal centrado sin spotlight.
 */
const PASOS_BASE = [
  {
    tipo: "welcome",
    ruta: "/dashboard",
    titulo: "Bienvenido a ManttoAI",
    descripcion:
      "Esta plataforma de mantenimiento predictivo te permite monitorear equipos en tiempo real, recibir alertas automáticas y predecir fallas antes de que ocurran. Te mostramos las secciones clave en un tour rápido.",
    icono: true,
  },
  {
    ruta: "/dashboard",
    selector: "#nav-sidebar nav",
    titulo: "Navegación principal",
    descripcion:
      "Usá el menú lateral para moverte entre las secciones de la plataforma: Dashboard, Equipos, Alertas e Historial. Si sos admin, también verás la sección de administración.",
    posicion: "right",
  },
  {
    ruta: "/dashboard",
    selector: "[data-tour='dashboard-resumen']",
    titulo: "Resumen operativo",
    descripcion:
      "Acá ves las métricas críticas en tiempo real: alertas activas, equipos en riesgo, clasificación global y probabilidad de falla estimada por el modelo predictivo.",
    posicion: "bottom",
  },
  {
    ruta: "/dashboard",
    selector: "[data-tour='dashboard-graficos']",
    titulo: "Tendencias de sensores",
    descripcion:
      "Gráficos de temperatura y vibración actualizados en tiempo real. Te permiten detectar anomales visualmente antes de que se dispare una alerta.",
    posicion: "bottom",
  },
  {
    ruta: "/equipos",
    selector: "[data-tour='equipos-contenido']",
    titulo: "Gestión de equipos",
    descripcion:
      "Registrá y gestioná los activos monitoreados. Cada equipo muestra su estado, lecturas recientes, predicción de falla y umbrales configurados.",
    posicion: "bottom",
  },
  {
    ruta: "/alertas",
    selector: "[data-tour='alertas-contenido']",
    titulo: "Sistema de alertas",
    descripcion:
      "Las alertas aparecen cuando un sensor supera un umbral o el modelo detecta riesgo. Podés marcarlas como leídas y descargar el historial en CSV.",
    posicion: "bottom",
  },
  {
    ruta: "/historial",
    selector: "[data-tour='historial-contenido']",
    titulo: "Historial y reportes",
    descripcion:
      "Trazabilidad completa: lecturas históricas de sensores, registro de mantenciones y descarga de reportes ejecutivos en CSV y PDF para auditoría.",
    posicion: "bottom",
  },
  {
    ruta: "/admin",
    selector: "[data-tour='admin-contenido']",
    titulo: "Panel de administración",
    descripcion:
      "Solo visible para admins. Desde acá gestionás usuarios, generás API keys para dispositivos IoT y revisás el log de auditoría de acciones del sistema.",
    posicion: "bottom",
    adminOnly: true,
  },
];

/**
 * Indicador de progreso (dots) del tour.
 */
function StepDots({ total, actual }) {
  return (
    <div className="flex items-center gap-1.5" aria-hidden="true">
      {Array.from({ length: total }, (_, i) => (
        <span
          key={i}
          className={`inline-block h-1.5 rounded-full transition-all duration-200 ease-out-quart ${
            i === actual
              ? "w-4 bg-primary-600"
              : i < actual
              ? "w-1.5 bg-primary-300"
              : "w-1.5 bg-neutral-300"
          }`}
        />
      ))}
    </div>
  );
}

/**
 * Verifica si el onboarding ya fue completado.
 */
export function isOnboardingDone() {
  try {
    return localStorage.getItem(STORAGE_KEY) === "true";
  } catch {
    return false;
  }
}

/**
 * Marca el onboarding como completado.
 */
function markOnboardingDone() {
  try {
    localStorage.setItem(STORAGE_KEY, "true");
  } catch {
    // localStorage puede no estar disponible (ej. modo privado)
  }
}

/**
 * Componente principal del tour de onboarding.
 *
 * Se monta condicionalmente desde Layout.jsx solo si el usuario
 * no completó el tour anteriormente.
 */
export default function OnboardingTour({ onComplete }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const titleId = useId();

  // Filtrar pasos según rol
  const pasos = PASOS_BASE.filter((paso) => {
    if (paso.adminOnly) return user?.rol === "admin";
    return true;
  });

  const [pasoActual, setPasoActual] = useState(0);
  const [posicion, setPosicion] = useState({ top: 0, left: 0 });
  const [spotlightRect, setSpotlightRect] = useState(null);
  const [listo, setListo] = useState(false);
  const tooltipRef = useRef(null);

  const paso = pasos[pasoActual];
  const esUltimo = pasoActual === pasos.length - 1;
  const esWelcome = paso.tipo === "welcome";

  /**
   * Cierra el tour y marca como completado.
   */
  const cerrarTour = useCallback(() => {
    markOnboardingDone();
    onComplete?.();
  }, [onComplete]);

  /**
   * Avanza al siguiente paso o cierra si es el último.
   */
  const avanzar = useCallback(() => {
    if (esUltimo) {
      cerrarTour();
      return;
    }
    setListo(false);
    setPasoActual((prev) => prev + 1);
  }, [esUltimo, cerrarTour]);

  /**
   * Retrocede al paso anterior.
   */
  const retroceder = useCallback(() => {
    if (pasoActual === 0) return;
    setListo(false);
    setPasoActual((prev) => prev - 1);
  }, [pasoActual]);

  /**
   * Navega a la ruta del paso actual y recalcula posiciones.
   */
  useEffect(() => {
    navigate(paso.ruta, { replace: true });

    // Si es paso welcome, no necesita spotlight
    if (esWelcome) {
      setSpotlightRect(null);
      setListo(true);
      return;
    }

    // Esperar a que la navegación y el render ocurran
    const timer = setTimeout(() => {
      const target = paso.selector ? document.querySelector(paso.selector) : null;

      if (target) {
        const rect = target.getBoundingClientRect();
        setSpotlightRect({
          top: rect.top - 4,
          left: rect.left - 4,
          width: rect.width + 8,
          height: rect.height + 8,
        });

        // Calcular posición del tooltip según la posición preferida
        const gap = 16;
        let tooltipTop;
        let tooltipLeft;

        if (paso.posicion === "right") {
          tooltipTop = rect.top + rect.height / 2 - 60;
          tooltipLeft = rect.right + gap;
        } else if (paso.posicion === "bottom") {
          tooltipTop = rect.bottom + gap;
          tooltipLeft = rect.left + rect.width / 2 - 160; // centrado (320/2)
        } else {
          tooltipTop = rect.top + rect.height / 2 - 60;
          tooltipLeft = rect.right + gap;
        }

        // Clamp dentro del viewport
        tooltipTop = Math.max(16, Math.min(tooltipTop, window.innerHeight - 300));
        tooltipLeft = Math.max(16, Math.min(tooltipLeft, window.innerWidth - 340));

        setPosicion({ top: tooltipTop, left: tooltipLeft });
      } else {
        // Fallback: posición centrada-derecha
        setSpotlightRect(null);
        setPosicion({ top: 100, left: 260 });
      }

      setListo(true);
    }, 200);

    return () => clearTimeout(timer);
  }, [paso, navigate, esWelcome]);

  /**
   * Focus trap + Escape handler
   */
  useEffect(() => {
    if (!listo) return;

    function handleKeyDown(e) {
      if (e.key === "Escape") {
        e.preventDefault();
        cerrarTour();
        return;
      }

      if (e.key !== "Tab") return;

      const focusables = tooltipRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (!focusables || focusables.length === 0) {
        e.preventDefault();
        return;
      }

      const primero = focusables[0];
      const ultimo = focusables[focusables.length - 1];

      if (e.shiftKey && document.activeElement === primero) {
        e.preventDefault();
        ultimo.focus();
      } else if (!e.shiftKey && document.activeElement === ultimo) {
        e.preventDefault();
        primero.focus();
      }
    }

    // Enfocar el primer botón del tooltip
    const primerBoton = tooltipRef.current?.querySelector("button");
    primerBoton?.focus();

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [listo, cerrarTour]);

  // No renderizar hasta que la posición esté calculada
  if (!listo) return null;

  return (
    <>
      {/* Overlay semitransparente */}
      <div
        className="onboarding-overlay fixed inset-0 z-[200] bg-neutral-900/50"
        aria-hidden="true"
        onClick={cerrarTour}
      />

      {/* Spotlight sobre el elemento destacado (no en paso welcome) */}
      {!esWelcome && spotlightRect && (
        <div
          className="onboarding-spotlight fixed z-[201] rounded-md ring-2 ring-primary-400 ring-offset-2 ring-offset-neutral-900/50 pointer-events-none"
          style={{
            top: spotlightRect.top,
            left: spotlightRect.left,
            width: spotlightRect.width,
            height: spotlightRect.height,
          }}
        />
      )}

      {/* Tooltip / Modal del paso actual */}
      <div
        ref={tooltipRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className={`onboarding-tooltip fixed z-[202] rounded-lg border border-neutral-300 bg-neutral-100 p-5 shadow-md ${
          esWelcome ? "onboarding-tooltip--welcome" : "w-[340px]"
        }`}
        style={
          esWelcome
            ? undefined // Se posiciona via CSS (centrado)
            : {
                top: posicion.top,
                left: posicion.left,
              }
        }
      >
        {/* Contenido */}
        <div className="space-y-3">
          {/* Logo en paso welcome */}
          {esWelcome && paso.icono && (
            <div className="flex justify-center mb-2">
              <Logo size={48} title="ManttoAI" />
            </div>
          )}

          <div className="flex items-start justify-between gap-2">
            <h3 id={titleId} className={`font-semibold text-neutral-800 ${esWelcome ? "text-xl text-center flex-1" : "text-lg"}`}>
              {paso.titulo}
            </h3>
            <span className="flex-shrink-0 rounded-sm bg-primary-50 px-2 py-0.5 text-xs font-medium text-primary-600">
              {pasoActual + 1}/{pasos.length}
            </span>
          </div>

          <p className={`leading-relaxed text-neutral-600 ${esWelcome ? "text-base text-center" : "text-sm"}`}>
            {paso.descripcion}
          </p>

          <StepDots total={pasos.length} actual={pasoActual} />

          {/* Acciones */}
          <div className="flex items-center justify-between gap-2 pt-1">
            <button
              type="button"
              onClick={cerrarTour}
              className="text-sm text-neutral-500 transition-colors duration-150 hover:text-neutral-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-1 rounded-sm px-1"
            >
              Saltar tour
            </button>

            <div className="flex items-center gap-2">
              {pasoActual > 0 && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={retroceder}
                  className="px-3 text-sm"
                >
                  Anterior
                </Button>
              )}
              <Button
                type="button"
                variant="primary"
                onClick={avanzar}
                className="px-3 text-sm"
              >
                {esUltimo ? "Comenzar" : pasoActual === 0 ? "Comenzar tour" : "Siguiente"}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
