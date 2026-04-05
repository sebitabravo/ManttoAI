import EquipoCard from "../components/equipos/EquipoCard";

const equipos = [
  { id: 1, nombre: "Compresor principal", estado: "operativo", dato: "42.5 °C" },
  { id: 2, nombre: "Motor bomba", estado: "monitoreo", dato: "0.68 riesgo" },
];

export default function EquiposPage() {
  return (
    <section>
      <h1>Equipos</h1>
      <div style={{ display: "grid", gap: 16, gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
        {equipos.map((equipo) => (
          <EquipoCard key={equipo.id} equipo={equipo} />
        ))}
      </div>
    </section>
  );
}
