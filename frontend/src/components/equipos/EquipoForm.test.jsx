import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import EquipoForm from "./EquipoForm";

describe("EquipoForm", () => {
  test("muestra errores requeridos cuando faltan campos", async () => {
    const user = userEvent.setup();

    render(<EquipoForm onSubmit={vi.fn()} submitLabel="Guardar" />);

    await user.clear(screen.getByLabelText("Nombre del equipo"));
    await user.clear(screen.getByLabelText("Ubicación"));
    fireEvent.change(screen.getByLabelText("Tipo"), { target: { value: "" } });
    fireEvent.change(screen.getByLabelText("Estado"), { target: { value: "" } });
    fireEvent.submit(screen.getByRole("button", { name: "Guardar" }).closest("form"));

    expect(screen.getByText("El nombre del equipo es obligatorio.")).toBeTruthy();
    expect(screen.getByText("La ubicación es obligatoria.")).toBeTruthy();
    expect(screen.getByText("El tipo es obligatorio.")).toBeTruthy();
    expect(screen.getByText("El estado es obligatorio.")).toBeTruthy();
  });

  test("envía payload normalizado sin espacios extra", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockResolvedValue(undefined);

    render(<EquipoForm onSubmit={onSubmit} submitLabel="Guardar" />);

    await user.clear(screen.getByLabelText("Nombre del equipo"));
    await user.type(screen.getByLabelText("Nombre del equipo"), "  Compresor A  ");
    await user.clear(screen.getByLabelText("Ubicación"));
    await user.type(screen.getByLabelText("Ubicación"), "  Planta Norte  ");
    await user.selectOptions(screen.getByLabelText("Tipo"), "Compresor");
    await user.selectOptions(screen.getByLabelText("Estado"), "operativo");
    await user.click(screen.getByRole("button", { name: "Guardar" }));

    expect(onSubmit).toHaveBeenCalledWith({
      nombre: "Compresor A",
      ubicacion: "Planta Norte",
      tipo: "Compresor",
      estado: "operativo",
    });
  });
});
