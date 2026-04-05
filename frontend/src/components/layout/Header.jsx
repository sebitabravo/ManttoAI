import { Link } from "react-router-dom";

import Button from "../ui/Button";
import useAuth from "../../hooks/useAuth";

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: 20, borderBottom: "1px solid #e5e7eb" }}>
      <div>
        <strong>Plataforma de mantenimiento predictivo</strong>
      </div>
      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <span>{user?.nombre || "Invitado"}</span>
        <Link to="/login" onClick={logout}>
          <Button variant="outline">Salir</Button>
        </Link>
      </div>
    </header>
  );
}
