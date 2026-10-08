import axios from "axios";
const api = axios.create({ baseURL: (import.meta.env.VITE_API_URL || "http://localhost:8000") + "/api" });
api.interceptors.request.use(c => { const t = localStorage.getItem("token"); if (t) c.headers.Authorization = `Bearer ${t}`; return c; });
api.interceptors.response.use(r => r, e => {
  if (e.response?.status === 401 && !e.config.url.includes("/auth/login")) { localStorage.clear(); window.location.href = "/login"; }
  return Promise.reject(e);
});
export const err = e => { const d = e.response?.data?.detail; return typeof d === "string" ? d : Array.isArray(d) ? d.map(x => x.msg).join(", ") : "Cannot reach server or unexpected error"; };
export default api;
