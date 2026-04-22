import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";

import { getAlertas, marcarLeida } from "../../api/alertas";
import usePolling from "../../hooks/usePolling";
import { ALERTAS_POLLING_INTERVAL_MS } from "../../utils/constants";
import { getApiErrorMessage } from "../../utils/errorHandling";
import { formatDate } from "../../utils/formatDate";

/**
 * Panel de notificaciones — Estilo Apple.
 * 
 * Botón trigger: limpio, sin borders visibles pesados.
 * Panel: fondo blanco, sin borders, sombra Apple.
 * Items: cards sutiles sin borders.
 */

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

  const fetchAlertas = useCallback(async () => {
    const data = await getAlertas({ limite: 20 });
    return Array.isArray(data) ? data : [];
  }, []);

  const { data, loading, error, refresh } = usePolling(fetchAlertas, ALERTAS_POLLING_INTERVAL_MS, []);

  const alertas = useMemo(() => (Array.isArray(data) ? data : []), [data]);
  const noLeidas = useMemo(() => alertas.filter((a) => !a.leida), [alertas]);
  const preview = useMemo(() => alertas.slice(0, 6), [alertas]);

  useEffect(() => {
    if (!abierto) return undefined;

    function onPointerDown(event) {
      const target = event.target;
      if (!(target instanceof Node)) return;
      if (panelRef.current?.contains(target) || triggerRef.current?.contains(target)) return;
      setAbierto(false);
    }

    function onKeyDown(event) {
      if (event.key === "Escape") { setAbierto(false); triggerRef.current?.focus(); }
    }

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
      setActionError(getApiErrorMessage(markError, "No pudimos marcar la alerta como leída."));
    } finally {
      setMarkingId(null);
    }
  }

  function togglePanel() { setActionError(""); setAbierto((s) => !s); }
  function closePanel() { setAbierto(false); }

  const totalNoLeidas = noLeidas.length;
  const badgeLabel = resolveBadgeLabel(totalNoLeidas);

  useEffect(() => {
    if (abierto) {
      const panel = panelRef.current;
      if (panel) {
        const first = panel.querySelector('a, button, [tabindex]:not([tabindex="-1"])');
        (first || panel).focus();
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
        className="relative inline-flex h-10 w-10 items-center justify-center rounded-xl text-neutral-500 transition-colors duration-200 hover:bg-neutral-100 hover:text-neutral-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" aria-hidden="true">
          <path d="M15 17h5l-1.4-1.4a2 2 0 0 1-.6-1.4V11a6 6 0 1 0-12 0v3.2a2 2 0 0 1-.6 1.4L4 17h5" />
          <path d="M9 17a3 3 0 0 0 6 0" />
        </svg>

        {totalNoLeidas > 0 && (
          <span className="absolute -right-0.5 -top-0.5 inline-flex min-h-[18px] min-w-[18px] items-center justify-center rounded-full bg-danger-500 px-1 text-[10px] font-semibold text-white">
            {badgeLabel}
          </span>
        )}
      </button>

      {abierto && (
        <section
          id="topbar-notificaciones-panel"
          ref={panelRef}
          tabIndex={-1}
          role="region"
          aria-label="Notificaciones recientes"
          className="fixed inset-x-3 top-[3.75rem] z-[120] rounded-2xl bg-white shadow-apple sm:absolute sm:inset-auto sm:right-0 sm:top-full sm:mt-3 sm:w-[24rem]"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-neutral-100">
            <div>
              <h2 className="m-0 text-sm font-semibold text-neutral-600">Notificaciones</h2>
              <p className="m-0 text-xs text-neutral-400">
                {totalNoLeidas === 0 ? "Todo al día" : `${totalNoLeidas} ${totalNoLeidas === 1 ? "pendiente" : "pendientes"}`}
              </p>
            </div>
            <Link
              to="/alertas"
              onClick={closePanel}
              className="text-xs font-medium text-primary-600 no-underline hover:text-primary-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 rounded-lg px-1"
            >
              Ver todas
            </Link>
          </div>

          {/* Lista */}
          <div className="max-h-80 overflow-y-auto p-3">
            {actionError && (
              <p className="mb-2 rounded-lg bg-danger-50 px-3 py-2 text-xs text-danger-600" role="alert">
                {actionError}
              </p>
            )}

            {error && preview.length === 0 && (
              <p className="mb-0 rounded-lg bg-warning-50 px-3 py-2 text-xs text-warning-700">
                No se pudieron cargar notificaciones.
              </p>
            )}

            {!loading && preview.length === 0 && (
              <p className="mb-0 px-1 py-3 text-sm text-neutral-400">No hay alertas recientes.</p>
            )}

            {preview.length > 0 && (
              <ul className="grid grid-cols-1 gap-2">
                {preview.map((alerta) => {
                  const isLeida = Boolean(alerta.leida);
                  const timestamp = resolveTimestamp(alerta);

                  return (
                    <li key={alerta.id || `${alerta.tipo}-${timestamp}`} className="rounded-xl bg-neutral-100 p-3">
                      <div className="flex items-center justify-between gap-2">
                        <strong className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
                          {resolveTipoLabel(alerta.tipo)}
                        </strong>
                        <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${isLeida ? "bg-success-50 text-success-600" : "bg-danger-50 text-danger-600"}`}>
                          {isLeida ? "Leída" : "Nueva"}
                        </span>
                      </div>

                      <p className="mt-1.5 text-sm text-neutral-600">{alerta.mensaje || "Alerta sin detalle."}</p>

                      <div className="mt-2 flex items-center justify-between gap-2">
                        <span className="text-xs text-neutral-400">{timestamp ? formatDate(timestamp) : "—"}</span>

                        {!isLeida && (
                          <button
                            type="button"
                            onClick={() => handleMarcarLeida(alerta.id)}
                            disabled={markingId === alerta.id}
                            className="rounded-lg px-2.5 py-1 text-xs font-medium text-primary-600 transition-colors duration-200 hover:bg-primary-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 disabled:opacity-50"
                          >
                            {markingId === alerta.id ? "..." : "Marcar leída"}
                          </button>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
