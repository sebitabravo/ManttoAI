import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";

import { getAlertas, marcarLeida } from "../../api/alertas";
import usePolling from "../../hooks/usePolling";
import { ALERTAS_POLLING_INTERVAL_MS } from "../../utils/constants";
import { getApiErrorMessage } from "../../utils/errorHandling";
import { formatDate } from "../../utils/formatDate";

function resolveTipoLabel(tipo) {
  if (!tipo) return "Alerta";
  const resolved = String(tipo).trim();
  if (!resolved) return "Alerta";
  return resolved.charAt(0).toUpperCase() + resolved.slice(1);
}

function resolveTimestamp(alerta) {
  return alerta?.created_at || alerta?.fecha || null;
}

function resolveBadgeLabel(totalNoLeidas) {
  if (totalNoLeidas > 99) return "99+";
  return String(totalNoLeidas);
}

export default function TopbarNotifications() {
  const [abierto, setAbierto] = useState(false);
  const [markingId, setMarkingId] = useState(null);
  const [actionError, setActionError] = useState("");
  const triggerRef = useRef(null);
  const panelRef = useRef(null);

  // Polling liviano para resumen de alertas en topbar.
  const fetchAlertas = useCallback(async () => {
    const data = await getAlertas({ limite: 20 });
    return Array.isArray(data) ? data : [];
  }, []);

  const { data, loading, error, refresh } = usePolling(
    fetchAlertas,
    ALERTAS_POLLING_INTERVAL_MS,
    []
  );

  const alertas = useMemo(() => (Array.isArray(data) ? data : []), [data]);

  const noLeidas = useMemo(() => {
    return alertas.filter((alerta) => !alerta.leida);
  }, [alertas]);

  const preview = useMemo(() => {
    return alertas.slice(0, 6);
  }, [alertas]);

  useEffect(() => {
    if (!abierto) return undefined;

    function onPointerDown(event) {
      const target = event.target;
      if (!(target instanceof Node)) return;

      if (panelRef.current?.contains(target) || triggerRef.current?.contains(target)) {
        return;
      }

      setAbierto(false);
    }

    function onKeyDown(event) {
      if (event.key === "Escape") {
        setAbierto(false);
        triggerRef.current?.focus();
      }
    }

    // pointerdown cubre mouse + touch + stylus (móvil incluido).
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);

    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [abierto]);

  async function handleMarcarLeida(alertaId) {
    setMarkingId(alertaId);
    setActionError("");

    try {
      await marcarLeida(alertaId);
      await refresh();
    } catch (markError) {
      setActionError(
        getApiErrorMessage(markError, "No pudimos marcar la alerta como leída. Probá nuevamente.")
      );
    } finally {
      setMarkingId(null);
    }
  }

  function togglePanel() {
    setActionError("");
    setAbierto((state) => !state);
  }

  function closePanel() {
    setAbierto(false);
  }

  const totalNoLeidas = noLeidas.length;
  const badgeLabel = resolveBadgeLabel(totalNoLeidas);

  useEffect(() => {
    // Cuando el panel abre, mover foco al primer interactivo para que
    // usuarios de teclado puedan recorrer notificaciones de inmediato.
    if (abierto) {
      const panel = panelRef.current;
      if (panel) {
        const firstInteractive = panel.querySelector('a, button, [tabindex]:not([tabindex="-1"])');
        if (firstInteractive) {
          firstInteractive.focus();
        } else {
          panel.focus();
        }
      }
    }
  }, [abierto]);

  return (
    <div className="relative">
      <button
        type="button"
        ref={triggerRef}
        onClick={togglePanel}
        aria-label={`Notificaciones (${totalNoLeidas} no leídas)`}
        aria-expanded={abierto}
        aria-controls="topbar-notificaciones-panel"
        className="relative inline-flex min-h-[44px] min-w-[44px] items-center justify-center rounded-sm border border-neutral-300 bg-neutral-50 text-neutral-700 transition-all duration-150 ease-out-quart hover:bg-neutral-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
          <path d="M15 17h5l-1.4-1.4a2 2 0 0 1-.6-1.4V11a6 6 0 1 0-12 0v3.2a2 2 0 0 1-.6 1.4L4 17h5" />
          <path d="M9 17a3 3 0 0 0 6 0" />
        </svg>

        {totalNoLeidas > 0 ? (
          <span className="absolute -right-1 -top-1 inline-flex min-h-[20px] min-w-[20px] items-center justify-center rounded-full bg-danger-600 px-1 text-[10px] font-semibold text-neutral-50">
            {badgeLabel}
          </span>
        ) : null}
      </button>

        {abierto ? (
        <section
          id="topbar-notificaciones-panel"
          ref={panelRef}
          tabIndex={-1}
          role="region"
          aria-label="Notificaciones recientes"
          className="fixed inset-x-2 top-[4.25rem] z-[120] rounded-lg border border-neutral-300 bg-neutral-50 shadow-lg sm:absolute sm:inset-auto sm:right-0 sm:top-full sm:mt-2 sm:w-[24rem]"
        >
          <div className="flex items-center justify-between border-b border-neutral-200 px-3 py-2.5">
            <div>
              <h2 className="m-0 text-sm font-semibold text-neutral-800">Notificaciones</h2>
              <p className="m-0 text-xs text-neutral-500">
                {totalNoLeidas === 0
                  ? "No hay alertas pendientes"
                  : `${totalNoLeidas} ${totalNoLeidas === 1 ? "alerta pendiente" : "alertas pendientes"}`}
              </p>
            </div>

            <Link
              to="/alertas"
              onClick={closePanel}
              className="text-xs font-medium text-primary-700 no-underline hover:text-primary-800 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
            >
              Ver todas
            </Link>
          </div>

          <div className="max-h-80 overflow-y-auto p-2">
            {actionError ? (
              <p className="mb-2 rounded-sm border border-danger-300 bg-danger-50 px-2 py-1.5 text-xs text-danger-700" role="alert">
                {actionError}
              </p>
            ) : null}

            {error && preview.length === 0 ? (
              <p className="mb-0 rounded-sm border border-warning-300 bg-warning-50 px-2 py-1.5 text-xs text-warning-700">
                No se pudieron cargar notificaciones en tiempo real.
              </p>
            ) : null}

            {!loading && preview.length === 0 ? (
              <p className="mb-0 px-1 py-2 text-sm text-neutral-600">No hay alertas recientes para mostrar.</p>
            ) : null}

            {preview.length > 0 ? (
              <ul className="grid grid-cols-1 gap-2">
                {preview.map((alerta) => {
                  const isLeida = Boolean(alerta.leida);
                  const timestamp = resolveTimestamp(alerta);

                  return (
                    <li key={alerta.id || `${alerta.tipo}-${timestamp || "sin-fecha"}`} className="rounded-md border border-neutral-200 bg-neutral-100 p-2.5">
                      <div className="flex items-center justify-between gap-2">
                        <strong className="text-xs font-semibold uppercase tracking-wide text-neutral-700">
                          {resolveTipoLabel(alerta.tipo)}
                        </strong>

                        <span
                          className={`rounded-sm px-2 py-0.5 text-[10px] font-medium ${
                            isLeida ? "bg-success-50 text-success-700" : "bg-danger-50 text-danger-700"
                          }`}
                        >
                          {isLeida ? "Leída" : "Nueva"}
                        </span>
                      </div>

                      <p className="mt-1 text-sm text-neutral-700">{alerta.mensaje || "Alerta sin detalle."}</p>

                      <div className="mt-2 flex items-center justify-between gap-2">
                        <span className="text-xs text-neutral-500">{timestamp ? formatDate(timestamp) : "Sin fecha"}</span>

                        {!isLeida ? (
                          <button
                            type="button"
                            onClick={() => handleMarcarLeida(alerta.id)}
                            disabled={markingId === alerta.id}
                            className="rounded-sm border border-neutral-300 px-2 py-1 text-xs font-medium text-neutral-700 transition-all duration-150 ease-out-quart hover:bg-neutral-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 disabled:cursor-not-allowed disabled:opacity-60"
                          >
                            {markingId === alerta.id ? "Marcando..." : "Marcar leída"}
                          </button>
                        ) : null}
                      </div>
                    </li>
                  );
                })}
              </ul>
            ) : null}
          </div>
        </section>
      ) : null}
    </div>
  );
}
