import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/layout/Layout";
import ProtectedRoute from "./components/layout/ProtectedRoute";
import OnboardingGuard from "./components/onboarding/OnboardingGuard";
import { AuthProvider } from "./context/AuthContext";
import useAuth from "./hooks/useAuth";

// Code splitting: cada pagina se carga bajo demanda
const AdminPage = lazy(() => import("./pages/AdminPage"));
const AlertasPage = lazy(() => import("./pages/AlertasPage"));
const ChatHistoryPage = lazy(() => import("./pages/ChatHistoryPage"));
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const EquipoDetallePage = lazy(() => import("./pages/EquipoDetallePage"));
const EquiposPage = lazy(() => import("./pages/EquiposPage"));
const HistorialPage = lazy(() => import("./pages/HistorialPage"));
const LoginPage = lazy(() => import("./pages/LoginPage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));
const OnboardingPage = lazy(() => import("./pages/OnboardingPage"));
const ProfilePage = lazy(() => import("./pages/ProfilePage"));

function AuthBootstrapFallback() {
  return <div className="flex min-h-screen items-center justify-center bg-neutral-50 text-sm text-neutral-600">Validando sesión...</div>;
}

// Fallback para paginas cargadas bajo demanda (code splitting)
function PageFallback() {
  return <div className="flex min-h-screen items-center justify-center bg-neutral-50 text-sm text-neutral-400">Cargando...</div>;
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

function AdminGuard({ children }) {
  const { isAuthenticated, isAuthResolved, user } = useAuth();

  if (!isAuthResolved) {
    return <AuthBootstrapFallback />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Verificar que el usuario es admin
  if (user && user.rol !== "admin") {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <Suspense fallback={<PageFallback />}>
          <Routes>
            <Route path="/login" element={<LoginRoute />} />
            <Route
              path="/"
              element={(
                <ProtectedRoute fallback={<AuthBootstrapFallback />}>
                  <OnboardingGuard>
                    <Layout />
                  </OnboardingGuard>
                </ProtectedRoute>
              )}
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="equipos" element={<EquiposPage />} />
              <Route path="equipos/:equipoId" element={<EquipoDetallePage />} />
              <Route path="alertas" element={<AlertasPage />} />
              <Route path="historial" element={<HistorialPage />} />
              <Route path="onboarding" element={<OnboardingPage />} />
              <Route path="perfil" element={<ProfilePage />} />
              <Route path="admin" element={<AdminGuard><AdminPage /></AdminGuard>} />
              <Route path="chat-historial" element={<AdminGuard><ChatHistoryPage /></AdminGuard>} />
            </Route>
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  );
}
