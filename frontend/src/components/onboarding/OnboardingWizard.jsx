import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

import {
  getOnboardingStatus,
  updateOnboardingStep,
  completeOnboarding,
} from "../../api/onboarding";
import { createEquipo, getEquipos } from "../../api/equipos";
import { createUmbral } from "../../api/umbrales";
import { createApiKey } from "../../api/admin";
import Button from "../ui/Button";

/**
 * Wizard de onboarding guiado para nuevos usuarios.
 *
 * Pasos del wizard:
 * 1. Bienvenida y explicación del valor
 * 2. Crear primer equipo
 * 3. Configurar umbrales básicos
 * 4. Agregar dispositivo IoT (API key)
 * 5. Demo del dashboard
 *
 * Características:
 * - Progreso persistente en backend
 * - Puede saltar y volver después
 * - Validaciones en cada paso
 * - Loading states
 */
export default function OnboardingWizard() {
  const navigate = useNavigate();
  const location = useLocation();

  const [loading, setLoading] = useState(true);
  const [currentStep, setCurrentStep] = useState(1);
  const [showRedirectMessage, setShowRedirectMessage] = useState(false);

  // Estado del formulario
  const [equipoData, setEquipoData] = useState({
    nombre: "",
    ubicacion: "Laboratorio",
    tipo: "Motor",
  });
  const [umbralesData, setUmbralesData] = useState({
    temperatura_max: 80,
    vibracion_max: 0.5,
  });
  const [apiKeyData, setApiKeyData] = useState(null);

  // Estados de error y carga
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Cargar estado inicial del onboarding
  useEffect(() => {
    async function loadStatus() {
      try {
        const status = await getOnboardingStatus();
        if (status.onboarding_completed) {
          // Si ya completó el onboarding, redirigir al dashboard
          navigate("/dashboard", { replace: true });
          return;
        }
        // Si tenía un paso guardado, continuar desde ahí
        if (status.onboarding_step) {
          setCurrentStep(status.onboarding_step);

          // Si está en paso 3+ y no tiene equipoId en memoria,
          // buscar el último equipo creado para recuperar el ID
          if (status.onboarding_step >= 3) {
            try {
              const equipos = await getEquipos();
              if (equipos.length > 0) {
                // Tomar el equipo más reciente (último de la lista)
                const lastEquipo = equipos[equipos.length - 1];
                setApiKeyData((prev) => ({
                  ...prev,
                  equipoId: lastEquipo.id,
                }));
              }
            } catch {
              // Si falla la carga de equipos, el usuario puede retroceder al paso 2
            }
          }
        }
      } catch (err) {
        console.error("Error al cargar estado del onboarding:", err);
        setError("No se pudo cargar el estado del onboarding");
      } finally {
        setLoading(false);
        // Mostrar mensaje si vino por error de red
        if (location.state?.redirectReason === "error") {
          setShowRedirectMessage(true);
        }
      }
    }
    loadStatus();
  }, [navigate, location.state]);

  // Guardar progreso del paso actual
  const saveStepProgress = async (step) => {
    try {
      await updateOnboardingStep(step);
    } catch (err) {
      console.error("Error al guardar progreso:", err);
    }
  };

  // Manejar cambio de paso
  const handleNextStep = async () => {
    if (currentStep < 5) {
      const nextStep = currentStep + 1;
      setCurrentStep(nextStep);
      await saveStepProgress(nextStep);
    }
  };

  const handlePrevStep = async () => {
    if (currentStep > 1) {
      const prevStep = currentStep - 1;
      setCurrentStep(prevStep);
      await saveStepProgress(prevStep);
    }
  };

  const handleSkip = async () => {
    try {
      // Completar con el equipo si ya fue creado, o sin equipo si se salta desde el inicio
      await completeOnboarding({ equipo_id: apiKeyData?.equipoId ?? null });
      navigate("/dashboard", { replace: true });
    } catch (err) {
      console.error("Error al saltar onboarding:", err);
      setError("No se pudo saltar el onboarding");
    }
  };

  // Manejar creación de equipo (paso 2)
  // Crea el equipo y avanza al paso 3 para configurar umbrales
  const handleCreateEquipo = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      // Si ya existe un equipo vinculado, ir directamente a paso de umbrales
      if (apiKeyData?.equipoId) {
        await handleNextStep();
        return;
      }

      // Crear equipo primero (sin umbrales)
      const equipo = await createEquipo({
        nombre: equipoData.nombre,
        ubicacion: equipoData.ubicacion,
        tipo: equipoData.tipo,
      });

      setApiKeyData((prev) => ({ ...prev, equipoId: equipo.id }));
      await handleNextStep();
    } catch (err) {
      console.error("Error al crear equipo:", err);
      setError("No se pudo crear el equipo. Verifica los datos e intenta nuevamente.");
    } finally {
      setSubmitting(false);
    }
  };

  // Manejar configuración de umbrales (paso 3)
  // Usa el endpoint atómico para crear ambos umbrales en una transacción
  const handleConfigureUmbrales = async (e) => {
    e.preventDefault();
    if (!apiKeyData?.equipoId) {
      setError("No hay equipo seleccionado");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      // Usar el endpoint atómico para crear ambos umbrales
      await createUmbral(apiKeyData.equipoId, {
        equipo_id: apiKeyData.equipoId,
        variable: "temperatura",
        valor_min: 0,
        valor_max: umbralesData.temperatura_max,
      });
      await createUmbral(apiKeyData.equipoId, {
        equipo_id: apiKeyData.equipoId,
        variable: "vibracion",
        valor_min: 0,
        valor_max: umbralesData.vibracion_max,
      });

      await handleNextStep();
    } catch (err) {
      console.error("Error al configurar umbrales:", err);
      setError("No se pudieron configurar los umbrales. Intenta nuevamente.");
    } finally {
      setSubmitting(false);
    }
  };

  // Manejar generación de API key (paso 4)
  const handleGenerateApiKey = async () => {
    if (!apiKeyData?.equipoId) {
      setError("No hay equipo seleccionado");
      return;
    }

    // Si ya se generó la API key, avanzar al siguiente paso
    if (apiKeyData?.apiKey) {
      await handleNextStep();
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const result = await createApiKey({ device_id: `equipo_${apiKeyData.equipoId}` });
      setApiKeyData((prev) => ({ ...prev, apiKey: result.key, apiKeyId: result.id }));
      // No avanzamos automáticamente, dejamos que el usuario vea la API key
    } catch (err) {
      console.error("Error al generar API key:", err);
      setError("No se pudo generar la API key. Intenta nuevamente.");
    } finally {
      setSubmitting(false);
    }
  };

  // Manejar finalización del wizard (paso 5)
  const handleComplete = async () => {
    setSubmitting(true);
    setError(null);

    try {
      await completeOnboarding({
        equipo_id: apiKeyData?.equipoId ?? null,
        api_key_id: apiKeyData?.apiKeyId ?? null,
      });
      navigate("/dashboard", { replace: true });
    } catch (err) {
      console.error("Error al completar onboarding:", err);
      setError("No se pudo completar el onboarding. Intenta nuevamente.");
    } finally {
      setSubmitting(false);
    }
  };

  // Renderizar paso actual
  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-neutral-900 mb-2">
                Bienvenido a ManttoAI
              </h2>
              <p className="text-neutral-600">
                Esta plataforma de mantenimiento predictivo te permite monitorear equipos en tiempo real,
                recibir alertas automáticas y predecir fallas antes de que ocurran.
              </p>
            </div>
            <div className="bg-neutral-50 rounded-lg p-4 space-y-2">
              <h3 className="font-semibold text-neutral-800">Lo que configurarás:</h3>
              <ul className="list-disc list-inside text-neutral-600 space-y-1">
                <li>Tu primer equipo a monitorear</li>
                <li>Umbrales de alerta personalizados</li>
                <li>Conexión con tu dispositivo IoT</li>
                <li>Configuración de notificaciones</li>
              </ul>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-neutral-900 mb-2">
                Crea tu primer equipo
              </h2>
              <p className="text-neutral-600">
                Registra el equipo que deseas monitorear. Puedes agregar más equipos después.
              </p>
            </div>
            <form onSubmit={handleCreateEquipo} className="space-y-4">
              <div>
                <label htmlFor="nombre" className="block text-sm font-medium text-neutral-700 mb-1">
                  Nombre del equipo *
                </label>
                <input
                  id="nombre"
                  type="text"
                  required
                  value={equipoData.nombre}
                  onChange={(e) => setEquipoData({ ...equipoData, nombre: e.target.value })}
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Ej: Motor principal Bomba #1"
                />
              </div>
              <div>
                <label htmlFor="ubicacion" className="block text-sm font-medium text-neutral-700 mb-1">
                  Ubicación
                </label>
                <input
                  id="ubicacion"
                  type="text"
                  value={equipoData.ubicacion}
                  onChange={(e) => setEquipoData({ ...equipoData, ubicacion: e.target.value })}
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Ej: Planta Norte - Línea 3"
                />
              </div>
              <div>
                <label htmlFor="tipo" className="block text-sm font-medium text-neutral-700 mb-1">
                  Tipo de equipo
                </label>
                <select
                  id="tipo"
                  value={equipoData.tipo}
                  onChange={(e) => setEquipoData({ ...equipoData, tipo: e.target.value })}
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="Motor">Motor</option>
                  <option value="Bomba">Bomba</option>
                  <option value="Compresor">Compresor</option>
                  <option value="Ventilador">Ventilador</option>
                  <option value="Otro">Otro</option>
                </select>
              </div>
            </form>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-neutral-900 mb-2">
                Configura umbrales de alerta
              </h2>
              <p className="text-neutral-600">
                Define los valores límite para generar alertas automáticas.
              </p>
            </div>
            <form onSubmit={handleConfigureUmbrales} className="space-y-4">
              <div>
                <label htmlFor="temp_max" className="block text-sm font-medium text-neutral-700 mb-1">
                  Temperatura máxima (°C)
                </label>
                <input
                  id="temp_max"
                  type="number"
                  required
                  min="0"
                  max="200"
                  value={umbralesData.temperatura_max}
                  onChange={(e) =>
                    setUmbralesData({ ...umbralesData, temperatura_max: parseInt(e.target.value) })
                  }
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
                <p className="text-xs text-neutral-500 mt-1">
                  Se generará una alerta si la temperatura supera este valor
                </p>
              </div>
              <div>
                <label htmlFor="vib_max" className="block text-sm font-medium text-neutral-700 mb-1">
                  Vibración máxima (g)
                </label>
                <input
                  id="vib_max"
                  type="number"
                  required
                  min="0"
                  max="10"
                  step="0.1"
                  value={umbralesData.vibracion_max}
                  onChange={(e) =>
                    setUmbralesData({ ...umbralesData, vibracion_max: parseFloat(e.target.value) })
                  }
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
                <p className="text-xs text-neutral-500 mt-1">
                  Se generará una alerta si la vibración supera este valor
                </p>
              </div>
            </form>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-neutral-900 mb-2">
                Conecta tu dispositivo IoT
              </h2>
              <p className="text-neutral-600">
                Genera una API key para conectar tu ESP32 al sistema.
              </p>
            </div>
            {!apiKeyData?.apiKey ? (
              <div className="bg-neutral-50 rounded-lg p-4 space-y-3">
                <p className="text-neutral-600">
                  Al hacer clic en "Generar API Key", se creará una credencial única para tu dispositivo.
                  Guárdala de forma segura, ya que no se mostrará nuevamente.
                </p>
                <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                  <p className="text-sm text-yellow-800">
                    <strong>Importante:</strong> Esta API key se usará en el código de tu ESP32
                    para enviar datos al sistema.
                  </p>
                </div>
              </div>
            ) : (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 space-y-3">
                <h3 className="font-semibold text-green-800">API Key generada exitosamente</h3>
                <div className="bg-white rounded-md p-3 font-mono text-sm break-all">
                  {apiKeyData.apiKey}
                </div>
                <p className="text-xs text-green-700">
                  Copia esta key y guárdala en un lugar seguro. La necesitarás para configurar tu ESP32.
                </p>
              </div>
            )}
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-neutral-900 mb-2">
                ¡Todo listo!
              </h2>
              <p className="text-neutral-600">
                Has completado la configuración inicial. Ahora puedes comenzar a monitorear tu equipo.
              </p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 space-y-2">
              <h3 className="font-semibold text-green-800">Configuración completada:</h3>
              <ul className="list-disc list-inside text-green-700 space-y-1">
                <li>Equipo creado: {equipoData.nombre || "No especificado"}</li>
                <li>Umbrales configurados</li>
                <li>API Key generada</li>
              </ul>
            </div>
            <div className="bg-neutral-50 rounded-lg p-4 space-y-2">
              <h3 className="font-semibold text-neutral-800">Próximos pasos:</h3>
              <ul className="list-disc list-inside text-neutral-600 space-y-1">
                <li>Configura tu ESP32 con la API Key generada</li>
                <li>Verifica que los datos estén llegando al dashboard</li>
                <li>Ajusta los umbrales según tus necesidades</li>
                <li>Agrega más equipos si lo necesitas</li>
              </ul>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  // Renderizar botones de acción según el paso
  const renderActions = () => {
    return (
      <div className="flex items-center justify-between pt-4 border-t border-neutral-200">
        <div>
          {currentStep > 1 && (
            <Button type="button" variant="outline" onClick={handlePrevStep}>
              Anterior
            </Button>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleSkip}
            className="text-sm text-neutral-500 hover:text-neutral-700 focus:outline-none focus:underline px-2 py-1"
          >
            Saltar y configurar después
          </button>
          {currentStep === 1 && (
            <Button type="button" onClick={handleNextStep}>
              Comenzar
            </Button>
          )}
          {currentStep === 2 && (
            <Button type="button" onClick={handleCreateEquipo} disabled={submitting}>
              {submitting ? "Creando..." : "Siguiente"}
            </Button>
          )}
          {currentStep === 3 && (
            <Button type="button" onClick={handleConfigureUmbrales} disabled={submitting}>
              {submitting ? "Configurando..." : "Siguiente"}
            </Button>
          )}
          {currentStep === 4 && (
            <Button type="button" onClick={handleGenerateApiKey} disabled={submitting}>
              {submitting ? "Generando..." : apiKeyData?.apiKey ? "Siguiente" : "Generar API Key"}
            </Button>
          )}
          {currentStep === 5 && (
            <Button type="button" onClick={handleComplete} disabled={submitting}>
              {submitting ? "Finalizando..." : "Ir al Dashboard"}
            </Button>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-neutral-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-neutral-600">Cargando configuración...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-neutral-100 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header con progreso */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-bold text-neutral-900">Configuración inicial</h1>
            <span className="text-sm text-neutral-500">
              Paso {currentStep} de 5
            </span>
          </div>
          {/* Barra de progreso */}
          <div className="w-full bg-neutral-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / 5) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Contenido del paso */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
              {error}
            </div>
          )}
          {showRedirectMessage && (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-md mb-6">
              No pudimos verificar tu estado anterior. Por seguridad, te pedimos completar la configuración inicial.
            </div>
          )}
          {renderStep()}
          {renderActions()}
        </div>
      </div>
    </div>
  );
}
