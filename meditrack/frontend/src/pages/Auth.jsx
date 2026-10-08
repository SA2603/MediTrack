import { useState } from "react"; import { Link } from "react-router-dom";
import { useAuth } from "../context/Auth.jsx"; import { err } from "../services/api"; import { Alert, Btn, inp } from "../components/ui.jsx";
export default function Auth({ register }) {
  const { login, register: reg } = useAuth(); const [f, setF] = useState({ name: "", email: "", password: "", phone: "" });
  const [e, setE] = useState(""), [busy, setB] = useState(false); const set = k => ev => setF({ ...f, [k]: ev.target.value });
  const submit = async ev => { ev.preventDefault(); setB(true); setE("");
    try { register ? await reg(f) : await login(f.email, f.password); } catch (x) { setE(err(x)); } setB(false); };
  return <div className="min-h-screen flex items-center justify-center p-4"><form onSubmit={submit} className="bg-white p-8 rounded-2xl shadow w-full max-w-sm">
    <h1 className="text-2xl font-bold text-teal-700 mb-1">✚ MEDTRACK</h1><p className="text-slate-500 text-sm mb-4">{register ? "Create patient account" : "Sign in to continue"}</p>
    <Alert msg={e} />
    {register && <><input className={inp} placeholder="Full name" value={f.name} onChange={set("name")} required minLength={2} /><input className={inp} placeholder="Phone" value={f.phone} onChange={set("phone")} /></>}
    <input className={inp} type="email" placeholder="Email" value={f.email} onChange={set("email")} required />
    <input className={inp} type="password" placeholder="Password (min 8 chars)" value={f.password} onChange={set("password")} required minLength={8} />
    <Btn disabled={busy} className="w-full py-2">{busy ? "Please wait…" : register ? "Register" : "Login"}</Btn>
    <p className="text-sm mt-4 text-center">{register ? <Link className="text-teal-700" to="/login">Have an account? Login</Link> : <Link className="text-teal-700" to="/register">New patient? Register</Link>}</p></form></div>;
}
