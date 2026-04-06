import { createContext, useEffect, useState } from "react";

import { getCurrentUser, logout as logoutRequest } from "../api/auth";

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext(null);

/**
 * Obtiene el valor de una cookie por nombre.
 */
function getCookieValue(cookieName) {
  const cookies = document.cookie.split(";").map((cookie) => cookie.trim());
  const match = cookies.find((cookie) => cookie.startsWith(`${cookieName}=`));
  return match ? decodeURIComponent(match.split("=").slice(1).join("=")) : "";
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
      // Intentar restaurar desde sessionStorage primero
      const storedUser = window.sessionStorage.getItem("manttoai_user");
      
      // Si no hay usuario en sessionStorage, verificar si hay cookie de sesión
      if (!storedUser) {
        const sessionCookie = getCookieValue("manttoai_session");
        if (!sessionCookie) {
          // No hay sesión previa, marcar como resuelto
          if (isMounted) {
            setUser(null);
            setIsAuthResolved(true);
          }
          return;
        }
      }

      // Si hay sessionStorage O cookie, validar con el backend
      try {
        const currentUser = await getCurrentUser();
        if (!isMounted) {
          return;
        }

        setUser(currentUser);
        window.sessionStorage.setItem("manttoai_user", JSON.stringify(currentUser));
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
      window.sessionStorage.setItem("manttoai_user", JSON.stringify(user));
    } else {
      window.sessionStorage.removeItem("manttoai_user");
    }
  }, [user]);

  async function login(nextUser) {
    setUser(nextUser);
    setIsAuthResolved(true);
    // Persist to sessionStorage immediately so restoreSession() can find it
    if (nextUser) {
      window.sessionStorage.setItem("manttoai_user", JSON.stringify(nextUser));
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
