import { Navigate, Outlet } from "react-router-dom";

import useAuth from "../../hooks/useAuth";

export default function ProtectedRoute({ children = null, fallback = null }) {
  const { isAuthenticated, isAuthResolved } = useAuth();

  if (!isAuthResolved) {
    return fallback;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children || <Outlet />;
}
