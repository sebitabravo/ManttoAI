import { useCallback, useEffect, useMemo, useState } from "react";

import { getEquipos } from "../api/equipos";
import { getLecturas } from "../api/lecturas";
import { getMantenciones } from "../api/mantenciones";
import Button from "../components/ui/Button";
import EmptyState from "../components/ui/EmptyState";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import { formatDate } from "../utils/formatDate";
import { formatMetric, resolveMaxVibration } from "../utils/metrics";

export default function HistorialPage() {
  const [lecturas, setLecturas] = useState([]);
  const [mantenciones, setMantenciones] = useState([]);
  const [equiposById, setEquiposById] = useState(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadHistorial = useCallback(async () => {
    setLoading(true);
    try {
      const [lecturasData, mantencionesData, equiposData] = await Promise.all([
        getLecturas(),
        getMantenciones(),
        getEquipos(),
      ]);

      setLecturas(Array.isArray(lecturasData) ? lecturasData : []);
      setMantenciones(Array.isArray(mantencionesData) ? mantencionesData : []);
      const nextEquiposById = new Map(
        (Array.isArray(equiposData) ? equiposData : []).map((equipo) => [
          Number(equipo.id),
          equipo.nombre,
        ])
      );
      setEquiposById(nextEquiposById);
      setError(null);
    } catch (fetchError) {
      setError(fetchError);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistorial();
  }, [loadHistorial]);

  const lecturasRecientes = useMemo(() => {
    return [...lecturas]
      .sort((current, next) => new Date(next.timestamp).getTime() - new Date(current.timestamp).getTime())
      .slice(0, 25);
  }, [lecturas]);

  const mantencionesRecientes = useMemo(() => {
    return [...mantenciones]
      .sort((current, next) => Number(next.id) - Number(current.id))
      .slice(0, 25);
  }, [mantenciones]);

  function resolveEquipoName(equipoId) {
    return equiposById.get(Number(equipoId)) || `Equipo #${equipoId}`;
  }

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <div>
          <h1 style={{ margin: 0 }}>Historial</h1>
          <p style={{ marginTop: 6, marginBottom: 0, color: "#6b7280" }}>
            Lecturas y mantenciones persistidas para trazabilidad del prototipo.
          </p>
        </div>
        <Button type="button" variant="outline" onClick={loadHistorial} disabled={loading}>
          {loading ? "Actualizando..." : "Actualizar"}
        </Button>
      </div>

      {loading ? <LoadingSpinner label="Cargando historial desde backend..." /> : null}

      {error ? (
        <div style={{ padding: 12, border: "1px solid #f59e0b", borderRadius: 12, background: "#fffbeb" }}>
          No se pudo cargar historial real de lecturas y mantenciones.
        </div>
      ) : null}

      {!loading && lecturasRecientes.length === 0 && mantencionesRecientes.length === 0 ? (
        <EmptyState
          title="Sin historial cargado"
          description="Acá conviven lecturas y mantenciones reales cuando ya existen datos en backend."
        />
      ) : null}

      <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
        <h2 style={{ marginTop: 0 }}>Lecturas recientes</h2>
        {lecturasRecientes.length === 0 ? (
          <p style={{ marginBottom: 0, color: "#6b7280" }}>No hay lecturas históricas para mostrar.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th align="left">Equipo</th>
                <th align="left">Temperatura</th>
                <th align="left">Humedad</th>
                <th align="left">Vibración máx.</th>
                <th align="left">Fecha</th>
              </tr>
            </thead>
            <tbody>
              {lecturasRecientes.map((lectura) => (
                <tr key={lectura.id || `${lectura.equipo_id}-${lectura.timestamp}`}>
                  <td>{resolveEquipoName(lectura.equipo_id)}</td>
                  <td>{formatMetric(lectura.temperatura, "°C")}</td>
                  <td>{formatMetric(lectura.humedad, "%")}</td>
                  <td>{formatMetric(resolveMaxVibration(lectura), "g")}</td>
                  <td>{formatDate(lectura.timestamp)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section style={{ padding: 16, border: "1px solid #e5e7eb", borderRadius: 16 }}>
        <h2 style={{ marginTop: 0 }}>Mantenciones recientes</h2>
        {mantencionesRecientes.length === 0 ? (
          <p style={{ marginBottom: 0, color: "#6b7280" }}>
            No hay mantenciones registradas para este período.
          </p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th align="left">ID</th>
                <th align="left">Equipo</th>
                <th align="left">Tipo</th>
                <th align="left">Descripción</th>
                <th align="left">Estado</th>
              </tr>
            </thead>
            <tbody>
              {mantencionesRecientes.map((mantencion) => (
                <tr key={mantencion.id}>
                  <td>{mantencion.id}</td>
                  <td>{resolveEquipoName(mantencion.equipo_id)}</td>
                  <td>{mantencion.tipo}</td>
                  <td>{mantencion.descripcion}</td>
                  <td>{mantencion.estado}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </section>
  );
}
