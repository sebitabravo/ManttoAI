import { createContext, useEffect, useMemo, useState } from "react";

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext(null);

function parseJwtPayload(token) {
  try {
    const payloadBase64 = token.split(".")[1];
    if (!payloadBase64) {
      return null;
    }

    const normalizedBase64 = payloadBase64.replace(/-/g, "+").replace(/_/g, "/");
    const paddedBase64 = normalizedBase64.padEnd(Math.ceil(normalizedBase64.length / 4) * 4, "=");
    return JSON.parse(window.atob(paddedBase64));
  } catch {
    return null;
  }
}

function isTokenExpired(token) {
  if (!token) {
    return true;
  }

  const payload = parseJwtPayload(token);
  if (!payload || typeof payload.exp !== "number") {
    return true;
  }

  return payload.exp * 1000 <= Date.now();
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => {
    const storedToken = window.localStorage.getItem("manttoai_token") || "";
    if (!storedToken) {
      return "";
    }

    if (isTokenExpired(storedToken)) {
      window.localStorage.removeItem("manttoai_token");
      window.localStorage.removeItem("manttoai_user");
      return "";
    }

    return storedToken;
  });
  const [user, setUser] = useState(() => {
    const stored = window.localStorage.getItem("manttoai_user");
    if (!stored) {
      return null;
    }

    try {
      return JSON.parse(stored);
    } catch {
      window.localStorage.removeItem("manttoai_user");
      return null;
    }
  });

  useEffect(() => {
    if (token && isTokenExpired(token)) {
      setToken("");
      setUser(null);
      return;
    }

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
