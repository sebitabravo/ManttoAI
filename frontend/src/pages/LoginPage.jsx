import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2 } from "lucide-react";

import { getCurrentUser, login as loginRequest } from "../api/auth";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Logo from "../components/ui/Logo";
import useAuth from "../hooks/useAuth";
import { getApiErrorMessage, isApiUnavailableError } from "../utils/errorHandling";

function getConfiguredDemoCredentials() {
  const email = String(import.meta.env.VITE_DEMO_EMAIL || "").trim();
  const password = String(import.meta.env.VITE_DEMO_PASSWORD || "");

  return email && password ? { email, password } : null;
}

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
  const [isWakingServer, setIsWakingServer] = useState(false);
  const demoCredentials = getConfiguredDemoCredentials();

  useEffect(() => {
    if (!isSubmitting) {
      setIsWakingServer(false);
      return undefined;
    }

    const timer = window.setTimeout(() => setIsWakingServer(true), 5000);
    return () => window.clearTimeout(timer);
  }, [isSubmitting]);

  function handleChange(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  function handleUseDemo() {
    setErrorMessage("");
    setForm(demoCredentials);
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
      const fallbackMessage = isApiUnavailableError(error)
        ? "El backend está despertando y puede tardar hasta un minuto. Reintentá en unos segundos."
        : "No pudimos iniciar sesión. Revisá tus credenciales y el backend.";
      setErrorMessage(
        isApiUnavailableError(error)
          ? fallbackMessage
          : getApiErrorMessage(error, fallbackMessage)
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
            Monitoreo IoT por Rubro
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

            {demoCredentials && (
              <div className="rounded-xl border border-primary-100 bg-primary-50 px-4 py-4">
                <p className="text-sm font-medium text-primary-900">
                  ¿Querés ver la demo?
                </p>
                <p className="mt-1 text-xs text-primary-800">
                  Usa una cuenta de solo lectura configurada por el despliegue.
                </p>
                <Button
                  type="button"
                  variant="outline"
                  className="mt-3 w-full"
                  onClick={handleUseDemo}
                  disabled={isSubmitting}
                >
                  Usar cuenta demo
                </Button>
              </div>
            )}
            
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
                  <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
                  Ingresando...
                </span>
              ) : (
                "Continuar"
              )}
            </Button>
            {isWakingServer && (
              <p className="text-center text-sm text-primary-700" role="status">
                El backend gratuito se está iniciando. No cierres esta ventana;
                puede tardar hasta un minuto.
              </p>
            )}
          </form>
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-xs text-neutral-400">
          Plataforma de monitoreo IoT por rubro: industrial, agrícola y comercial
        </p>
      </section>
    </main>
  );
}
