import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { getCurrentUser, login as loginRequest } from "../api/auth";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Logo from "../components/ui/Logo";
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
    <main className="grid min-h-screen place-items-center bg-neutral-50 p-8">
      <section className="w-full max-w-md rounded-lg border border-neutral-300 bg-neutral-100 p-8 shadow">
        {/* Branding: logo semántico con title ya que aparece sin texto equivalente visible */}
        <div className="mb-8 flex flex-col items-center gap-4">
          <Logo size={52} title="ManttoAI — Mantenimiento Predictivo" />
          <div className="text-center">
            <h1 className="text-xl font-semibold text-neutral-800 tracking-tight">ManttoAI</h1>
            <p className="mt-1 text-sm text-neutral-500">Mantenimiento Predictivo</p>
          </div>
        </div>

        <p className="mb-6 mt-0 text-base text-neutral-600">
          Iniciá sesión para acceder al dashboard.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
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
            <div className="rounded-lg border border-danger-500 bg-danger-50 px-4 py-3 text-sm text-danger-700" role="alert">
              {errorMessage}
            </div>
          ) : null}
          
          <Button type="submit" disabled={isSubmitting} className="w-full">
            {isSubmitting ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Ingresando...
              </span>
            ) : (
              "Iniciar sesión"
            )}
          </Button>
        </form>
      </section>
    </main>
  );
}
