import { createContext, useEffect, useMemo, useState } from "react";

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => window.localStorage.getItem("manttoai_token") || "");
  const [user, setUser] = useState(() => {
    const stored = window.localStorage.getItem("manttoai_user");
    return stored ? JSON.parse(stored) : null;
  });

  useEffect(() => {
    if (token) {
      window.localStorage.setItem("manttoai_token", token);
    } else {
      window.localStorage.removeItem("manttoai_token");
    }
  }, [token]);

  useEffect(() => {
    if (user) {
      window.localStorage.setItem("manttoai_user", JSON.stringify(user));
    } else {
      window.localStorage.removeItem("manttoai_user");
    }
  }, [user]);

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token),
      login: (nextToken, nextUser) => {
        setToken(nextToken);
        setUser(nextUser);
      },
      logout: () => {
        setToken("");
        setUser(null);
      },
    }),
    [token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
