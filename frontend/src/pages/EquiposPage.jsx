import { useCallback, useEffect, useState } from "react";

import { getDashboardResumen } from "../api/dashboard";
import { getEquipos } from "../api/equipos";
import EquipoCard from "../components/equipos/EquipoCard";
import EmptyState from "../components/ui/EmptyState";
import LoadingSpinner from "../components/ui/LoadingSpinner";
import Button from "../components/ui/Button";

function resolveLatestDataLabel(equipoResumen) {
  if (!equipoResumen) {
    return "Sin lecturas registradas";
  }

  if (equipoResumen.ultima_temperatura !== null && equipoResumen.ultima_temperatura !== undefined) {
    return `${Number(equipoResumen.ultima_temperatura).toFixed(2)} °C`;
  }

  if (equipoResumen.ultima_probabilidad !== null && equipoResumen.ultima_probabilidad !== undefined) {
    return `${(Number(equipoResumen.ultima_probabilidad) * 100).toFixed(1)} % riesgo`;
  }

  return "Sin lecturas registradas";
}

export default function EquiposPage() {
  const [equipos, setEquipos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadEquipos = useCallback(async () => {
    setLoading(true);
    try {
      const [equiposData, resumen] = await Promise.all([
        getEquipos(),
        getDashboardResumen().catch(() => null),
      ]);

      const equiposResumen = Array.isArray(resumen?.equipos) ? resumen.equipos : [];
      const resumenById = new Map(
        equiposResumen.map((equipoResumen) => [Number(equipoResumen.id), equipoResumen])
      );

      const enrichedEquipos = equiposData.map((equipo) => {
        const equipoResumen = resumenById.get(Number(equipo.id));

        return {
          ...equipo,
          dato: resolveLatestDataLabel(equipoResumen),
          alertas_activas: Number(equipoResumen?.alertas_activas || 0),
        };
      });

      setEquipos(enrichedEquipos);
      setError(null);
    } catch (fetchError) {
      setError(fetchError);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadEquipos();
  }, [loadEquipos]);

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <h1 style={{ margin: 0 }}>Equipos</h1>
        <Button type="button" variant="outline" onClick={loadEquipos} disabled={loading}>
          {loading ? "Actualizando..." : "Actualizar"}
        </Button>
      </div>

      {loading ? <LoadingSpinner label="Cargando equipos desde backend..." /> : null}

      {error ? (
        <div style={{ padding: 12, border: "1px solid #f59e0b", borderRadius: 12, background: "#fffbeb" }}>
          No se pudieron cargar equipos. Verificá la conexión con el backend.
        </div>
      ) : null}

      {!loading && equipos.length === 0 ? (
        <EmptyState
          title="No hay equipos cargados"
          description="Creá equipos desde la API para habilitar monitoreo y detalle por activo."
        />
      ) : null}

      <div style={{ display: "grid", gap: 16, gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
        {equipos.map((equipo) => (
          <EquipoCard key={equipo.id} equipo={equipo} />
        ))}
      </div>
    </section>
  );
}
