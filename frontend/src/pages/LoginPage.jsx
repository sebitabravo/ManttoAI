import { useState } from "react";
import { useNavigate } from "react-router-dom";

import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import useAuth from "../hooks/useAuth";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "demo@example.com", password: "123456" });

  function handleChange(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    login("demo-token", { nombre: "Usuario Demo", email: form.email, rol: "admin" });
    navigate("/dashboard");
  }

  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: "2rem" }}>
      <section style={{ width: "100%", maxWidth: 420, border: "1px solid #d1d5db", borderRadius: 16, padding: 24 }}>
        <h1 style={{ marginTop: 0 }}>ManttoAI Predictivo</h1>
        <p>Entrá en modo demo para recorrer el dashboard inicial.</p>
        <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16 }}>
          <Input label="Email" name="email" value={form.email} onChange={handleChange} />
          <Input label="Contraseña" name="password" type="password" value={form.password} onChange={handleChange} />
          <Button type="submit">Entrar en modo demo</Button>
        </form>
      </section>
    </main>
  );
}
