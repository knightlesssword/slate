import { useEffect, useState } from "react";
import { api, clearToken, getToken, setToken } from "../lib/api";
import { AuthContext } from "./useAuth";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Restore a session on refresh if a token is present.
    async function restore() {
      if (!getToken()) {
        setLoading(false);
        return;
      }
      try {
        setUser(await api.me());
      } catch {
        clearToken();
      } finally {
        setLoading(false);
      }
    }
    restore();
  }, []);

  async function login(email, password) {
    const { token } = await api.login(email, password);
    setToken(token);
    setUser(await api.me());
  }

  function logout() {
    clearToken();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
