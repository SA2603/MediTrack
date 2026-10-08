import { createContext, useContext, useState } from "react";
import api from "../services/api";
const Ctx = createContext();
export const useAuth = () => useContext(Ctx);
export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem("user") || "null"));
  const save = d => { localStorage.setItem("token", d.access_token); localStorage.setItem("user", JSON.stringify(d.user)); setUser(d.user); };
  const login = async (email, password) => save((await api.post("/auth/login", { email, password })).data);
  const register = async body => save((await api.post("/auth/register", body)).data);
  const logout = () => { localStorage.clear(); setUser(null); };
  return <Ctx.Provider value={{ user, login, register, logout }}>{children}</Ctx.Provider>;
}
