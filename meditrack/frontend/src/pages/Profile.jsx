import { useState, useEffect } from "react"; import api, { err } from "../services/api";
import { Card, Alert, Btn, Loading, inp } from "../components/ui.jsx";
export default function Profile() {
  const [f, setF] = useState(null), [m, setM] = useState(""), [e, setE] = useState("");
  useEffect(() => { api.get("/auth/me").then(r => setF({ name: r.data.name, phone: r.data.phone || "", email: r.data.email, ...(r.data.profile || {}), patient: !!r.data.profile })).catch(x => setE(err(x))); }, []);
  const set = k => x => setF({ ...f, [k]: x.target.value });
  const save = async ev => { ev.preventDefault(); setM(""); setE(""); const { email, patient, ...body } = f; if (!body.date_of_birth) delete body.date_of_birth;
    try { await api.put("/auth/me", body); localStorage.setItem("user", JSON.stringify({ ...JSON.parse(localStorage.user), name: f.name })); setM("Profile saved"); } catch (x) { setE(err(x)); } };
  if (!f) return e ? <Alert msg={e} /> : <Loading />;
  return <Card title="My profile" className="max-w-lg"><Alert msg={e} /><Alert msg={m} ok /><form onSubmit={save}>
    <input className={inp} value={f.email} disabled /><input className={inp} placeholder="Name" value={f.name} onChange={set("name")} /><input className={inp} placeholder="Phone" value={f.phone} onChange={set("phone")} />
    {f.patient && <><input className={inp} type="date" value={f.date_of_birth || ""} onChange={set("date_of_birth")} /><input className={inp} placeholder="Gender" value={f.gender || ""} onChange={set("gender")} /><input className={inp} placeholder="Blood group" value={f.blood_group || ""} onChange={set("blood_group")} />
      <input className={inp} placeholder="Address" value={f.address || ""} onChange={set("address")} /><input className={inp} placeholder="Emergency contact" value={f.emergency_contact || ""} onChange={set("emergency_contact")} /></>}
    <Btn>Save</Btn></form></Card>;
}
