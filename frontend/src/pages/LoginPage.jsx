import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { getCurrentUser, login as loginRequest } from "../api/auth";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import useAuth from "../hooks/useAuth";
import { getApiErrorMessage } from "../utils/errorHandling";

/** Logo de marca: círculo azul con inicial "M", consistente con el favicon */
function ManttoAILogo({ size = 48 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      aria-hidden="true"
      focusable="false"
    >
      <circle cx="16" cy="16" r="16" fill="#1d4ed8" />
      <text
        x="16"
        y="22"
        fontSize="20"
        fontWeight="700"
        textAnchor="middle"
        fontFamily="system-ui, sans-serif"
        fill="white"
      >
        M
      </text>
    </svg>
  );
}

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
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: "2rem", background: "#f8fafc" }}>
      <section style={{ width: "100%", maxWidth: 420, border: "1px solid #d1d5db", borderRadius: 16, padding: 32, background: "#ffffff" }}>
        {/* Branding: logo + nombre de producto */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12, marginBottom: 24 }}>
          <ManttoAILogo size={52} />
          <div style={{ textAlign: "center" }}>
            <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700, color: "#111827" }}>ManttoAI</h1>
            <p style={{ margin: "4px 0 0", fontSize: 13, color: "#6b7280" }}>Mantenimiento Predictivo</p>
          </div>
        </div>

        <p style={{ marginTop: 0, marginBottom: 20, fontSize: 14, color: "#374151" }}>
          Iniciá sesión para acceder al dashboard.
        </p>

        <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16 }}>
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
            <div style={{ color: "#dc2626", fontSize: 14 }} role="alert">
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
