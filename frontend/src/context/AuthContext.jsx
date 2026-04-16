import { createContext, useEffect, useState } from "react";

import { getCurrentUser, logout as logoutRequest } from "../api/auth";

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext(null);

/**
 * Extrae solo los campos no sensibles del usuario para persistir en sessionStorage.
 * Evita almacenar datos innecesarios que podrían filtrarse ante un XSS.
 */
function sanitizeUserForStorage(user) {
  if (!user) return null;
  return {
    id: user.id,
    nombre: user.nombre,
    rol: user.rol,
    // email se incluye porque se usa para mostrar en la UI (Header)
    email: user.email,
    // avatar se incluye para mostrar en el UserMenu
    avatar: user.avatar,
  };
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = window.sessionStorage.getItem("manttoai_user");
    if (!stored) {
      return null;
    }

    try {
      return JSON.parse(stored);
    } catch {
      window.sessionStorage.removeItem("manttoai_user");
      return null;
    }
  });
  const [isAuthResolved, setIsAuthResolved] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function restoreSession() {
      // Validar sesión exclusivamente con /api/auth/me
      // Las cookies HttpOnly no son accesibles desde JavaScript
      try {
        const currentUser = await getCurrentUser();
        if (!isMounted) {
          return;
        }

        setUser(currentUser);
        window.sessionStorage.setItem("manttoai_user", JSON.stringify(sanitizeUserForStorage(currentUser)));
      } catch {
        if (!isMounted) {
          return;
        }

        setUser(null);
        window.sessionStorage.removeItem("manttoai_user");
      } finally {
        if (isMounted) {
          setIsAuthResolved(true);
        }
      }
    }

    restoreSession();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (user) {
      window.sessionStorage.setItem("manttoai_user", JSON.stringify(sanitizeUserForStorage(user)));
    } else {
      window.sessionStorage.removeItem("manttoai_user");
    }
  }, [user]);

  async function login(nextUser) {
    setUser(nextUser);
    setIsAuthResolved(true);
    // Persist to sessionStorage immediately so restoreSession() can find it
    if (nextUser) {
      window.sessionStorage.setItem("manttoai_user", JSON.stringify(sanitizeUserForStorage(nextUser)));
    }
  }

  async function logout() {
    try {
      await logoutRequest();
    } catch {
      // Mantiene cierre local incluso si backend no responde.
    } finally {
      setUser(null);
      setIsAuthResolved(true);
      window.sessionStorage.removeItem("manttoai_user");
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: Boolean(user),
        isAuthResolved,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
