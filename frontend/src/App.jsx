import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/layout/Layout";
import { AuthProvider } from "./context/AuthContext";
import useAuth from "./hooks/useAuth";
import AlertasPage from "./pages/AlertasPage";
import DashboardPage from "./pages/DashboardPage";
import EquipoDetallePage from "./pages/EquipoDetallePage";
import EquiposPage from "./pages/EquiposPage";
import HistorialPage from "./pages/HistorialPage";
import LoginPage from "./pages/LoginPage";
import NotFoundPage from "./pages/NotFoundPage";

function AuthBootstrapFallback() {
  return <div className="flex min-h-screen items-center justify-center bg-neutral-50 text-sm text-neutral-600">Validando sesión...</div>;
}

function ProtectedLayout() {
  const { isAuthenticated, isAuthResolved } = useAuth();

  if (!isAuthResolved) {
    return <AuthBootstrapFallback />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Layout />;
}

function LoginRoute() {
  const { isAuthenticated, isAuthResolved } = useAuth();

  if (!isAuthResolved) {
    return <AuthBootstrapFallback />;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <LoginPage />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginRoute />} />
          <Route path="/" element={<ProtectedLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="equipos" element={<EquiposPage />} />
            <Route path="equipos/:equipoId" element={<EquipoDetallePage />} />
            <Route path="alertas" element={<AlertasPage />} />
            <Route path="historial" element={<HistorialPage />} />
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
