import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import MantencionForm from "./MantencionForm";

describe("MantencionForm", () => {
  test("valida campos obligatorios antes de enviar", async () => {
    const user = userEvent.setup();

    render(<MantencionForm onSubmit={vi.fn()} submitLabel="Guardar mantención" />);

    await user.clear(screen.getByLabelText("Tipo"));
    await user.clear(screen.getByLabelText("Descripción"));
    await user.clear(screen.getByLabelText("Estado"));
    fireEvent.submit(
      screen.getByRole("button", { name: "Guardar mantención" }).closest("form")
    );

    expect(screen.getByText("El tipo de mantención es obligatorio.")).toBeTruthy();
    expect(screen.getByText("La descripción es obligatoria.")).toBeTruthy();
    expect(screen.getByText("El estado es obligatorio.")).toBeTruthy();
  });

  test("envía payload sin espacios sobrantes", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockResolvedValue(undefined);

    render(<MantencionForm onSubmit={onSubmit} submitLabel="Guardar mantención" />);

    await user.clear(screen.getByLabelText("Tipo"));
    await user.type(screen.getByLabelText("Tipo"), "  correctiva  ");
    await user.clear(screen.getByLabelText("Descripción"));
    await user.type(screen.getByLabelText("Descripción"), "  Cambio de rodamiento  ");
    await user.clear(screen.getByLabelText("Estado"));
    await user.type(screen.getByLabelText("Estado"), "  ejecutada  ");
    await user.click(screen.getByRole("button", { name: "Guardar mantención" }));

    expect(onSubmit).toHaveBeenCalledWith({
      tipo: "correctiva",
      descripcion: "Cambio de rodamiento",
      estado: "ejecutada",
    });
  });
});
