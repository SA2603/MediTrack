import { useState } from "react"; import useFetch from "../hooks/useFetch"; import api, { err } from "../services/api"; import { useAuth } from "../context/Auth.jsx";
import { Card, Loading, Empty, Alert, Btn, Modal, Table, inp } from "../components/ui.jsx";
export default function Records() {
  const { user } = useAuth(); const doc = user.role === "DOCTOR"; const { data, loading, error, reload } = useFetch("/medical-records"); const ap = useFetch("/appointments");
  const [open, setOpen] = useState(false), [f, setF] = useState({ patient_id: "", diagnosis: "", notes: "" }), [e, setE] = useState("");
  const pts = [...new Map((ap.data || []).map(a => [a.patient_id, a.patient])).entries()];
  const save = async ev => { ev.preventDefault(); try { await api.post("/medical-records", { ...f, patient_id: +f.patient_id }); setOpen(false); setF({ patient_id: "", diagnosis: "", notes: "" }); reload(); } catch (x) { setE(err(x)); } };
  if (loading) return <Loading />;
  return <><div className="flex justify-between mb-4"><h2 className="text-2xl font-bold">{doc ? "Medical records" : "Medical history"}</h2>{doc && <Btn onClick={() => { setOpen(true); setE(""); }}>+ Add record</Btn>}</div><Alert msg={error} />
    <Card>{!data?.length ? <Empty text="No medical records yet" /> : <Table head={["Date", ...(doc ? ["Patient"] : ["Doctor"]), "Diagnosis", "Notes"]}>{data.map(r => <tr key={r.id} className="border-b align-top"><td className="py-2">{r.date}</td><td>{doc ? r.patient : r.doctor}</td><td>{r.diagnosis}</td><td>{r.notes}</td></tr>)}</Table>}</Card>
    {open && <Modal title="Add medical record" onClose={() => setOpen(false)}><form onSubmit={save}><Alert msg={e} />
      <select className={inp} value={f.patient_id} onChange={x => setF({ ...f, patient_id: x.target.value })} required><option value="">Select patient</option>{pts.map(([id, n]) => <option key={id} value={id}>{n}</option>)}</select>
      <input className={inp} placeholder="Diagnosis" value={f.diagnosis} onChange={x => setF({ ...f, diagnosis: x.target.value })} required />
      <textarea className={inp} placeholder="Clinical notes" value={f.notes} onChange={x => setF({ ...f, notes: x.target.value })} /><Btn className="w-full">Save record</Btn></form></Modal>}</>;
}
