import { useState, useEffect } from "react"; import useFetch from "../hooks/useFetch"; import api, { err } from "../services/api";
import { Card, Loading, Empty, Alert, Btn, Modal, inp } from "../components/ui.jsx";
export default function Doctors() {
  const { data, loading, error } = useFetch("/doctors"); const [sel, setSel] = useState(null), [ok, setOk] = useState("");
  const [date, setDate] = useState(""), [slots, setSlots] = useState([]), [time, setTime] = useState(""), [reason, setReason] = useState(""), [e, setE] = useState("");
  useEffect(() => { setTime(""); if (sel && date) api.get(`/doctors/${sel.id}/slots`, { params: { date } }).then(r => setSlots(r.data)).catch(x => setE(err(x))); }, [date, sel]);
  const book = async ev => { ev.preventDefault(); setE("");
    try { await api.post("/appointments", { doctor_id: sel.id, appointment_date: date, appointment_time: time, reason }); setSel(null); setOk("Appointment booked! Awaiting doctor confirmation."); setDate(""); setReason(""); } catch (x) { setE(err(x)); } };
  if (loading) return <Loading />;
  return <><h2 className="text-2xl font-bold mb-4">Doctors</h2><Alert msg={error} /><Alert msg={ok} ok />
    {!data?.length ? <Empty text="No doctors available" /> : <div className="grid md:grid-cols-2 gap-4">{data.map(d => <Card key={d.id}><h3 className="font-semibold">{d.name}</h3><p className="text-teal-700 text-sm">{d.specialization}</p><p className="text-sm text-slate-500">{d.qualification} · {d.experience} yrs · {d.availability}</p><Btn className="mt-3" onClick={() => { setSel(d); setE(""); setOk(""); }}>Book appointment</Btn></Card>)}</div>}
    {sel && <Modal title={`Book with ${sel.name}`} onClose={() => setSel(null)}><form onSubmit={book}><Alert msg={e} />
      <input className={inp} type="date" min={new Date().toISOString().slice(0, 10)} value={date} onChange={x => setDate(x.target.value)} required />
      <select className={inp} value={time} onChange={x => setTime(x.target.value)} required><option value="">{date ? (slots.length ? "Select time" : "No slots free") : "Pick a date first"}</option>{slots.map(s => <option key={s}>{s}</option>)}</select>
      <textarea className={inp} placeholder="Reason for visit" value={reason} onChange={x => setReason(x.target.value)} required minLength={3} /><Btn className="w-full">Confirm booking</Btn></form></Modal>}</>;
}
