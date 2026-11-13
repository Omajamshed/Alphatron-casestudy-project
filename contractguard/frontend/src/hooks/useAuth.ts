import { useState, useEffect } from "react";
import { apiRequest } from "../api/client";
import { User } from "../types";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("contractguard_token")
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchMe() {
      try {
        const u = await apiRequest<User>("/auth/me");
        setUser(u);
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    }
    fetchMe();
  }, [token]);

  const login = async (email: string, pass: string) => {
    const res = await apiRequest<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password: pass }),
    });
    localStorage.setItem("contractguard_token", res.access_token);
    setToken(res.access_token);
    const u = await apiRequest<User>("/auth/me");
    setUser(u);
  };

  const register = async (email: string, pass: string) => {
    await apiRequest("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password: pass }),
    });
    await login(email, pass);
  };

  const logout = () => {
    localStorage.removeItem("contractguard_token");
    setToken(null);
    setUser(null);
  };

  return { user, token, loading, login, register, logout };
}
