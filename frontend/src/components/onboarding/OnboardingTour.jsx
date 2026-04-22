import { useCallback, useEffect, useId, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import useAuth from "../../hooks/useAuth";
import { markOnboardingDone } from "../../utils/onboardingStorage";
import Logo from "../ui/Logo";
import Button from "../ui/Button";

/**
 * Tour de onboarding guiado — Estilo Apple.
 *
 * Características Apple:
 * - Card blanca sin bordes, sombra sutil
 * - Tipografía tight con negative letter-spacing
 * - Apple Blue como único acento
 * - Pill buttons para CTAs
 * - Overlay oscuro suave
 */

const PASOS_BASE = [
  {
    tipo: "welcome",
    ruta: "/dashboard",
    titulo: "Bienvenido a ManttoAI",
    descripcion:
      "Esta plataforma de mantenimiento predictivo te permite monitorear equipos en tiempo real, recibir alertas automáticas y predecir fallas antes de que ocurran. Te mostramos las secciones clave.",
    icono: true,
  },
  {
    ruta: "/dashboard",
    selector: "#nav-sidebar nav",
    titulo: "Navegación principal",
    descripcion:
      "Usá el menú lateral para moverte entre las secciones: Dashboard, Equipos, Alertas e Historial. Si sos admin, también verás la sección de administración.",
    posicion: "right",
  },
  {
    ruta: "/dashboard",
    selector: "[data-tour='dashboard-resumen']",
    titulo: "Resumen operativo",
    descripcion:
      "Métricas críticas en tiempo real: alertas activas, equipos en riesgo, clasificación global y probabilidad de falla estimada.",
    posicion: "bottom",
  },
  {
    ruta: "/dashboard",
    selector: "[data-tour='dashboard-graficos']",
    titulo: "Tendencias de sensores",
    descripcion:
      "Gráficos de temperatura y vibración actualizados en tiempo real. Detectá anomalías visuales antes de que se dispare una alerta.",
    posicion: "bottom",
  },
  {
    ruta: "/equipos",
    selector: "[data-tour='equipos-contenido']",
    titulo: "Gestión de equipos",
    descripcion:
      "Registrá y gestioná los activos monitoreados. Cada equipo muestra su estado, lecturas, predicción y umbrales configurados.",
    posicion: "bottom",
  },
  {
    ruta: "/alertas",
    selector: "[data-tour='alertas-contenido']",
    titulo: "Sistema de alertas",
    descripcion:
      "Alertas automáticas cuando un sensor supera un umbral o el modelo detecta riesgo. Marcá como leídas y descargá historial.",
    posicion: "bottom",
  },
  {
    ruta: "/historial",
    selector: "[data-tour='historial-contenido']",
    titulo: "Historial y reportes",
    descripcion:
      "Trazabilidad completa: lecturas históricas, registro de mantenciones y descarga de reportes para auditoría.",
    posicion: "bottom",
  },
  {
    ruta: "/admin",
    selector: "[data-tour='admin-contenido']",
    titulo: "Panel de administración",
    descripcion:
      "Solo visible para admins. Gestioná usuarios, generá API keys para dispositivos IoT y revisá el log de auditoría.",
    posicion: "bottom",
    adminOnly: true,
  },
];

function StepDots({ total, actual }) {
  return (
    <div className="flex items-center gap-1.5" aria-hidden="true">
      {Array.from({ length: total }, (_, i) => (
        <span
          key={i}
          className={`inline-block h-1.5 rounded-full transition-all duration-200 ${
            i === actual
              ? "w-5 bg-primary-500"
              : i < actual
              ? "w-1.5 bg-primary-300"
              : "w-1.5 bg-neutral-300"
          }`}
        />
      ))}
    </div>
  );
}

export default function OnboardingTour({ onComplete }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const titleId = useId();

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

  const cerrarTour = useCallback(() => {
    markOnboardingDone();
    onComplete?.();
  }, [onComplete]);

  const avanzar = useCallback(() => {
    if (esUltimo) { cerrarTour(); return; }
    setListo(false);
    setPasoActual((prev) => prev + 1);
  }, [esUltimo, cerrarTour]);

  const retroceder = useCallback(() => {
    if (pasoActual === 0) return;
    setListo(false);
    setPasoActual((prev) => prev - 1);
  }, [pasoActual]);

  useEffect(() => {
    navigate(paso.ruta, { replace: true });

    if (esWelcome) {
      setSpotlightRect(null);
      setListo(true);
      return;
    }

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

        const gap = 16;
        let tooltipTop;
        let tooltipLeft;

        if (paso.posicion === "right") {
          tooltipTop = rect.top + rect.height / 2 - 80;
          tooltipLeft = rect.right + gap;
        } else if (paso.posicion === "bottom") {
          tooltipTop = rect.bottom + gap;
          tooltipLeft = rect.left + rect.width / 2 - 160;
        } else {
          tooltipTop = rect.top + rect.height / 2 - 80;
          tooltipLeft = rect.right + gap;
        }

        tooltipTop = Math.max(16, Math.min(tooltipTop, window.innerHeight - 320));
        tooltipLeft = Math.max(16, Math.min(tooltipLeft, window.innerWidth - 360));

        setPosicion({ top: tooltipTop, left: tooltipLeft });
      } else {
        setSpotlightRect(null);
        setPosicion({ top: 100, left: 280 });
      }

      setListo(true);
    }, 250);

    return () => clearTimeout(timer);
  }, [paso, navigate, esWelcome]);

  useEffect(() => {
    if (!listo) return;

    function handleKeyDown(e) {
      if (e.key === "Escape") { e.preventDefault(); cerrarTour(); return; }
      if (e.key !== "Tab") return;

      const focusables = tooltipRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (!focusables || focusables.length === 0) { e.preventDefault(); return; }

      const primero = focusables[0];
      const ultimo = focusables[focusables.length - 1];

      if (e.shiftKey && document.activeElement === primero) {
        e.preventDefault(); ultimo.focus();
      } else if (!e.shiftKey && document.activeElement === ultimo) {
        e.preventDefault(); primero.focus();
      }
    }

    const primerBoton = tooltipRef.current?.querySelector("button");
    primerBoton?.focus();

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [listo, cerrarTour]);

  if (!listo) return null;

  return (
    <>
      {/* Overlay — oscuro suave estilo Apple */}
      <div
        className="fixed inset-0 z-[200] bg-black/40 backdrop-blur-sm"
        aria-hidden="true"
        onClick={cerrarTour}
      />

      {/* Spotlight */}
      {!esWelcome && spotlightRect && (
        <div
          className="fixed z-[201] rounded-xl ring-2 ring-primary-500 ring-offset-2 ring-offset-black/40 pointer-events-none transition-all duration-300"
          style={{
            top: spotlightRect.top,
            left: spotlightRect.left,
            width: spotlightRect.width,
            height: spotlightRect.height,
          }}
        />
      )}

      {/* Tooltip Card — estilo Apple: blanco, sin borders, shadow */}
      <div
        ref={tooltipRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className={`fixed z-[202] rounded-2xl bg-white p-6 shadow-apple ${
          esWelcome
            ? "left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[calc(100vw-2rem)] max-w-[420px]"
            : "w-[340px]"
        }`}
        style={esWelcome ? undefined : { top: posicion.top, left: posicion.left }}
      >
        <div className="space-y-4">
          {esWelcome && paso.icono && (
            <div className="flex justify-center mb-3">
              <Logo size={56} title="ManttoAI" />
            </div>
          )}

          <div className="flex items-start justify-between gap-3">
            <h3
              id={titleId}
              className={`font-semibold text-neutral-600 tracking-tight ${esWelcome ? "text-xl text-center flex-1" : "text-lg"}`}
            >
              {paso.titulo}
            </h3>
            <span className="flex-shrink-0 rounded-full bg-primary-50 px-2.5 py-1 text-xs font-medium text-primary-600">
              {pasoActual + 1}/{pasos.length}
            </span>
          </div>

          <p className={`leading-relaxed text-neutral-500 ${esWelcome ? "text-base text-center" : "text-sm"}`}>
            {paso.descripcion}
          </p>

          <StepDots total={pasos.length} actual={pasoActual} />

          <div className="flex items-center justify-between gap-3 pt-2">
            <button
              type="button"
              onClick={cerrarTour}
              className="text-sm text-neutral-400 transition-colors duration-200 hover:text-neutral-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 rounded-lg px-2 py-1"
            >
              Saltar
            </button>

            <div className="flex items-center gap-2">
              {pasoActual > 0 && (
                <Button type="button" variant="ghost" onClick={retroceder} size="sm">
                  Anterior
                </Button>
              )}
              <Button type="button" variant="primary" onClick={avanzar} size="sm">
                {esUltimo ? "Comenzar" : pasoActual === 0 ? "Comenzar tour" : "Siguiente"}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
