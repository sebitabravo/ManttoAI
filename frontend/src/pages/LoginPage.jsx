import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { getCurrentUser, login as loginRequest } from "../api/auth";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import useAuth from "../hooks/useAuth";
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
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: "2rem" }}>
      <section style={{ width: "100%", maxWidth: 420, border: "1px solid #d1d5db", borderRadius: 16, padding: 24 }}>
        <h1 style={{ marginTop: 0 }}>ManttoAI Predictivo</h1>
        <p>Iniciá sesión contra el backend para acceder al dashboard.</p>
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
