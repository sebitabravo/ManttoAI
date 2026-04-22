import { useCallback, useEffect, useState } from "react";

import client from "../api/client";
import Button from "../components/ui/Button";
import EmptyState from "../components/ui/EmptyState";
import { SkeletonTable } from "../components/ui/Skeleton";
import { getApiErrorMessage } from "../utils/errorHandling";
import { formatDate } from "../utils/formatDate";

export default function ChatHistoryPage() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await client.get("/chat/historial?limit=100");
      setMessages(response.data);
    } catch (err) {
      setError(getApiErrorMessage(err, "No pudimos cargar el historial del chat."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  return (
    <section className="grid grid-cols-1 gap-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="m-0 text-xl font-semibold text-neutral-900">Historial IA</h1>
          <p className="mb-0 mt-1.5 text-sm text-neutral-600">
            Registro de interacciones de los técnicos con el Asistente de Mantenimiento.
          </p>
        </div>
        <div>
          <Button type="button" variant="outline" onClick={loadHistory} disabled={loading}>
            {loading ? "Actualizando..." : "Actualizar"}
          </Button>
        </div>
      </div>

      {error ? (
        <div className="rounded-lg border border-danger-300 bg-danger-50 px-3 py-2 text-sm text-danger-800">
          {error}
        </div>
      ) : null}

      {loading ? (
        <div className="rounded-2xl bg-white p-5 shadow-sm">
          <SkeletonTable rows={10} cols={5} />
        </div>
      ) : null}

      {!loading && messages.length === 0 && !error ? (
        <EmptyState
          title="Sin historial de chat"
          description="Aún no hay interacciones registradas con el asistente."
        >
          <Button type="button" variant="outline" onClick={loadHistory} disabled={loading}>
            Actualizar historial
          </Button>
        </EmptyState>
      ) : null}

      {!loading && messages.length > 0 ? (
        <section className="rounded-2xl bg-white p-5 shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <caption className="pb-2 text-left text-sm text-neutral-600 sr-only">
                Historial de interacciones con el Asistente de IA.
              </caption>
              <thead>
                <tr className="border-b border-neutral-100">
                  <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700 w-1/6">Fecha</th>
                  <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700 w-1/6">Usuario</th>
                  <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700 w-2/6">Pregunta</th>
                  <th scope="col" className="pb-2 pr-4 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700 w-2/6">Respuesta IA</th>
                  <th scope="col" className="pb-2 text-left text-xs font-semibold uppercase tracking-wide text-neutral-700">Fuente</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {messages.map((msg) => (
                  <tr key={msg.id} className="hover:bg-neutral-50 transition-colors duration-150 ease-out-quart">
                    <td className="py-3 pr-4 text-xs text-neutral-500 align-top whitespace-nowrap">
                      {formatDate(msg.fecha_creacion)}
                    </td>
                    <td className="py-3 pr-4 text-sm text-neutral-900 font-medium align-top">
                      {msg.usuario?.nombre || "Desconocido"}
                      <div className="text-xs text-neutral-500 font-normal">{msg.usuario?.email}</div>
                    </td>
                    <td className="py-3 pr-4 text-sm text-neutral-800 align-top">
                      <div className="line-clamp-3 hover:line-clamp-none transition-all">{msg.mensaje_usuario}</div>
                    </td>
                    <td className="py-3 pr-4 text-sm text-neutral-600 align-top">
                      <div className="line-clamp-3 hover:line-clamp-none transition-all">{msg.respuesta_ia}</div>
                    </td>
                    <td className="py-3 text-xs align-top">
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 font-medium ${
                        msg.fuente === 'ollama' ? 'bg-primary-50 text-primary-700' :
                        msg.fuente === 'reglas' ? 'bg-success-50 text-success-700' :
                        'bg-warning-50 text-warning-700'
                      }`}>
                        {msg.fuente}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}
    </section>
  );
}
