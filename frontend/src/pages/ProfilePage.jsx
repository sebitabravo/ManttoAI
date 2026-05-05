import { useState } from "react";
import useAuth from "../hooks/useAuth";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import { updateProfile } from "../api/user";
import { getApiErrorMessage } from "../utils/errorHandling";
import { AVATARES } from "../utils/constants";

export default function ProfilePage() {
  const { user, login } = useAuth();
  const [form, setForm] = useState({ nombre: user?.nombre || "", avatar: user?.avatar || "user" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((s) => ({ ...s, [name]: value }));
  }

  function handleAvatarSelect(avatarId) {
    setForm((s) => ({ ...s, avatar: avatarId }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!form.nombre || form.nombre.trim().length < 2) {
      setError("Nombre debe tener al menos 2 caracteres");
      return;
    }

    setLoading(true);
    try {
      const updated = await updateProfile({ nombre: form.nombre.trim(), avatar: form.avatar });
      if (login) login(updated);
      setSuccess("Perfil actualizado correctamente");
    } catch (err) {
      setError(getApiErrorMessage(err, "No fue posible actualizar el perfil"));
    } finally {
      setLoading(false);
    }
  }

  return (
    // Comentario: Ajustes visuales al estilo Apple — eliminar bordes visibles en contenedores
    <div className="p-6">
      <h1 className="mb-2 text-2xl font-semibold text-neutral-800">Mi Perfil</h1>
      <p className="mb-6 text-sm text-neutral-600">Actualiza tu información personal.</p>

      <form onSubmit={handleSubmit} className="max-w-md">
        {error ? <div className="mb-4 rounded-2xl bg-danger-50 px-3 py-2 text-sm text-danger-700">{error}</div> : null}
        {success ? <div className="mb-4 rounded-2xl bg-success-50 px-3 py-2 text-sm text-success-700">{success}</div> : null}

        {/* Selector de avatar */}
        <div className="mb-6">
          <label className="mb-2 block text-sm font-medium text-neutral-700">Avatar</label>
          <div className="flex flex-wrap gap-2">
            {AVATARES.map((av) => (
              <button
                key={av.id}
                type="button"
                onClick={() => handleAvatarSelect(av.id)}
                className={`flex h-12 w-12 items-center justify-center rounded-full text-xl transition-all ${
                  form.avatar === av.id
                    ? "ring-2 ring-primary-500 ring-offset-2 bg-primary-50"
                    : "bg-neutral-100 hover:bg-neutral-200"
                }`}
                title={av.label}
              >
                {av.emoji}
              </button>
            ))}
          </div>
        </div>

        <Input label="Nombre" name="nombre" value={form.nombre} onChange={handleChange} />
        
        {/* Teléfono: solo lectura, se configura desde admin */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-neutral-700">Teléfono</label>
          <div className="mt-1 flex items-center gap-2 rounded-xl bg-neutral-50 px-3 py-2 text-sm text-neutral-600">
            <span>{user?.telefono || "No configurado"}</span>
            <span className="text-xs text-neutral-400">(configurado por admin)</span>
          </div>
        </div>

        <div className="mt-6">
          <Button type="submit" disabled={loading}>{loading ? "Guardando..." : "Guardar"}</Button>
        </div>
      </form>
    </div>
  );
}
