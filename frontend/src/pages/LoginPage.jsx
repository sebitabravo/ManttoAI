import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { getCurrentUser, login as loginRequest } from "../api/auth";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Logo from "../components/ui/Logo";
import useAuth from "../hooks/useAuth";
import { getApiErrorMessage } from "../utils/errorHandling";

/**
 * Página de login — Estilo Apple.
 * 
 * Características:
 * - Centrado elegante en pantalla
 * - Card limpia sin bordes pesados
 * - Tipografía refinada
 * - Espaciado generoso
 */
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
    <main className="min-h-screen flex items-center justify-center bg-neutral-100 p-6">
      {/* Card de login */}
      <section className="w-full max-w-md">
        {/* Branding centrado */}
        <div className="mb-10 flex flex-col items-center">
          <Logo size={64} />
          <h1 className="mt-6 text-display-md font-semibold text-neutral-600 tracking-tight">
            ManttoAI
          </h1>
          <p className="mt-2 text-base text-neutral-400">
            Mantenimiento Predictivo
          </p>
        </div>

        {/* Card del formulario */}
        <div className="rounded-2xl bg-white p-8 shadow-apple">
          <h2 className="text-xl font-semibold text-neutral-600 tracking-tight">
            Iniciar sesión
          </h2>
          <p className="mt-2 text-sm text-neutral-400">
            Ingresá tus credenciales para acceder al dashboard.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-5">
            <Input 
              label="Email" 
              name="email" 
              type="email" 
              value={form.email} 
              onChange={handleChange} 
              placeholder="tu@email.com"
              autoComplete="email"
              required 
            />
            <Input
              label="Contraseña"
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              placeholder="••••••••"
              autoComplete="current-password"
              required
            />
            
            {/* Error message */}
            {errorMessage && (
              <div 
                className="rounded-lg bg-danger-50 px-4 py-3 text-sm text-danger-600" 
                role="alert"
              >
                {errorMessage}
              </div>
            )}
            
            <Button 
              type="submit" 
              disabled={isSubmitting} 
              className="w-full mt-2"
              size="lg"
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle 
                      className="opacity-25" 
                      cx="12" 
                      cy="12" 
                      r="10" 
                      stroke="currentColor" 
                      strokeWidth="3" 
                    />
                    <path 
                      className="opacity-75" 
                      fill="currentColor" 
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" 
                    />
                  </svg>
                  Ingresando...
                </span>
              ) : (
                "Continuar"
              )}
            </Button>
          </form>
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-xs text-neutral-400">
          Sistema de mantenimiento predictivo basado en IoT y Machine Learning
        </p>
      </section>
    </main>
  );
}
