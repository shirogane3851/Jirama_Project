import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, getToken, onUnauthorized, setToken } from "./api";

export const ROLES = {
  EMPLOYE: "Employé",
  AGENT_POINTAGE: "Agent de pointage",
  VALIDATEUR_CONGE: "Validateur de congés",
  ADMIN_COMPTES: "Administrateur",
};

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(!getToken());

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  const loadUser = useCallback(async () => {
    const compte = await api("/auth/me");
    const employe = await api(`/employes/${compte.employe_id}`);
    setUser({ ...compte, employe });
  }, []);

  useEffect(() => {
    onUnauthorized(logout);
    if (getToken()) loadUser().catch(logout).finally(() => setReady(true));
  }, [loadUser, logout]);

  async function login(username, password) {
    setToken(null);
    const { access_token } = await api("/auth/login", {
      method: "POST",
      form: { username, password },
    });
    setToken(access_token);
    try {
      await loadUser();
    } catch (e) {
      setToken(null);
      throw e;
    }
  }

  return (
    <AuthContext.Provider value={{ user, ready, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
