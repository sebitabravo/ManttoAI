import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <main style={{ padding: 32 }}>
      <h1>404</h1>
      <p>La ruta solicitada no existe.</p>
      <Link to="/dashboard">Volver al dashboard</Link>
    </main>
  );
}
