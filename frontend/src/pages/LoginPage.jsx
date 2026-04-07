import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { getCurrentUser, login as loginRequest } from "../api/auth";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Logo from "../components/ui/Logo";
import useAuth from "../hooks/useAuth";
import { FONT_SIZE, RADIUS, SPACING, SURFACE, TEXT_COLOR } from "../styles/tokens";
import { getApiErrorMessage } from "../utils/errorHandling";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleChange(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setErrorMessage("");
    setIsSubmitting(true);

    try {
      const normalizedEmail = form.email.trim();
      const result = await loginRequest({
        email: normalizedEmail,
        password: form.password,
      });

      if (!result?.access_token) {
        throw new Error("Respuesta de autenticación inválida");
      }

      const currentUser = await getCurrentUser();
      await login(currentUser);
      navigate("/dashboard", { replace: true });
    } catch (error) {
      setErrorMessage(
        getApiErrorMessage(error, "No pudimos iniciar sesión. Revisá tus credenciales y el backend.")
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: "2rem", background: SURFACE.bg }}>
      <section style={{ width: "100%", maxWidth: 420, border: `1px solid ${SURFACE.borderInput}`, borderRadius: RADIUS.lg, padding: SPACING.xxxl, background: SURFACE.bgCard }}>
        {/* Branding: logo semántico con title ya que aparece sin texto equivalente visible */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: SPACING.md, marginBottom: SPACING.xxl }}>
          <Logo size={52} title="ManttoAI — Mantenimiento Predictivo" />
          <div style={{ textAlign: "center" }}>
            <h1 style={{ margin: 0, fontSize: FONT_SIZE.lg, fontWeight: 700, color: TEXT_COLOR.primary }}>ManttoAI</h1>
            <p style={{ margin: "4px 0 0", fontSize: FONT_SIZE.sm, color: TEXT_COLOR.muted }}>Mantenimiento Predictivo</p>
          </div>
        </div>

        <p style={{ marginTop: 0, marginBottom: SPACING.xl, fontSize: FONT_SIZE.base, color: TEXT_COLOR.secondary }}>
          Iniciá sesión para acceder al dashboard.
        </p>

        <form onSubmit={handleSubmit} style={{ display: "grid", gap: SPACING.lg }}>
          <Input label="Email" name="email" type="email" value={form.email} onChange={handleChange} required />
          <Input
            label="Contraseña"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            required
          />
          {errorMessage ? (
            <div style={{ color: "#dc2626", fontSize: FONT_SIZE.base }} role="alert">
              {errorMessage}
            </div>
          ) : null}
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Ingresando..." : "Iniciar sesión"}
          </Button>
        </form>
      </section>
    </main>
  );
}
