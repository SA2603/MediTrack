import { useState } from "react"; import useFetch from "../hooks/useFetch"; import api, { err } from "../services/api"; import { useAuth } from "../context/Auth.jsx";
import { Card, Loading, Empty, Alert, Btn, Modal, inp } from "../components/ui.jsx";
const blank = { patient_id: "", medicine_name: "", dosage: "", frequency: "", duration: "", instructions: "" };
export default function Prescriptions() {
  const { user } = useAuth(); const doc = user.role === "DOCTOR"; const { data, loading, error, reload } = useFetch("/prescriptions"); const ap = useFetch("/appointments");
  const [open, setOpen] = useState(false), [f, setF] = useState(blank), [e, setE] = useState("");
  const pts = [...new Map((ap.data || []).map(a => [a.patient_id, a.patient])).entries()]; const set = k => x => setF({ ...f, [k]: x.target.value });
  const save = async ev => { ev.preventDefault(); try { await api.post("/prescriptions", { ...f, patient_id: +f.patient_id }); setOpen(false); setF(blank); reload(); } catch (x) { setE(err(x)); } };
  const del = async id => { if (confirm("Delete prescription?")) { try { await api.delete(`/prescriptions/${id}`); reload(); } catch (x) { setE(err(x)); } } };
  if (loading) return <Loading />;
  return <><div className="flex justify-between mb-4 noprint"><h2 className="text-2xl font-bold">Prescriptions</h2><div className="space-x-2"><Btn className="!bg-slate-600" onClick={() => window.print()}>Print</Btn>{doc && <Btn onClick={() => { setOpen(true); setE(""); }}>+ New prescription</Btn>}</div></div><Alert msg={error || e} />
    {!data?.length ? <Empty text="No prescriptions yet" /> : <div className="grid md:grid-cols-2 gap-4">{data.map(p => <Card key={p.id}><div className="flex justify-between"><h3 className="font-semibold text-teal-700">{p.medicine_name}</h3><span className="text-xs text-slate-400">{p.date}</span></div>
      <p className="text-sm">{p.dosage} · {p.frequency} · {p.duration}</p><p className="text-sm text-slate-500">{p.instructions}</p><p className="text-xs text-slate-400 mt-2">Patient: {p.patient} · Dr: {p.doctor}</p>
      {doc && <button className="text-red-600 text-xs mt-2 noprint" onClick={() => del(p.id)}>Delete</button>}</Card>)}</div>}
    {open && <Modal title="New prescription" onClose={() => setOpen(false)}><form onSubmit={save}><Alert msg={e} />
      <select className={inp} value={f.patient_id} onChange={set("patient_id")} required><option value="">Select patient</option>{pts.map(([id, n]) => <option key={id} value={id}>{n}</option>)}</select>
      {[["medicine_name", "Medicine"], ["dosage", "Dosage (e.g. 5 mg)"], ["frequency", "Frequency"], ["duration", "Duration"]].map(([k, l]) => <input key={k} className={inp} placeholder={l} value={f[k]} onChange={set(k)} required />)}
      <textarea className={inp} placeholder="Instructions" value={f.instructions} onChange={set("instructions")} /><Btn className="w-full">Save prescription</Btn></form></Modal>}</>;
}
