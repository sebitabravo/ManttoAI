import { createContext, useEffect, useState } from "react";

import { getCurrentUser, logout as logoutRequest } from "../api/auth";

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext(null);

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
