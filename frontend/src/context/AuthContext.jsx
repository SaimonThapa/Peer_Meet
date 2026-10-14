"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { AuthApi } from "@/api/endpoints";
import { setAuthFailureHandler } from "@/api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState("checking");

  async function refreshCurrentUser() {
    try {
      const data = await AuthApi.me();
      setUser(data.user);
      setStatus("authenticated");
    } catch {
      setUser(null);
      setStatus("unauthenticated");
    }
  }

  useEffect(() => {
    setAuthFailureHandler(() => {
      setUser(null);
      setStatus("unauthenticated");
    });
    refreshCurrentUser();
  }, []);

  async function login(credentials) {
    const data = await AuthApi.login(credentials);
    setUser(data.user);
    setStatus("authenticated");
  }

  async function register(payload) {
    const data = await AuthApi.register(payload);
    setUser(data.user);
    setStatus("authenticated");
  }

  async function logout() {
    await AuthApi.logout();
    setUser(null);
    setStatus("unauthenticated");
  }

  const value = useMemo(() => ({ user, status, login, register, logout, refreshCurrentUser }), [user, status]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
