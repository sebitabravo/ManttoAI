import Button from "../ui/Button";
import Input from "../ui/Input";

export default function EquipoForm() {
  return (
    <form style={{ display: "grid", gap: 12 }}>
      <Input label="Nombre del equipo" name="nombre" value="" onChange={() => {}} />
      <Button type="button">Guardar</Button>
    </form>
  );
}
