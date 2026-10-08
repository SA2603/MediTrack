import { useState } from "react"; import useFetch from "../hooks/useFetch"; import api, { err } from "../services/api";
import { Card, Loading, Empty, Alert, Btn, Modal, Table, inp } from "../components/ui.jsx";
const blank = { name: "", email: "", password: "", phone: "", specialization: "", qualification: "", experience: 0 };
export default function AdminList({ kind }) {
  const url = kind === "users" ? "/admin/users" : kind === "doctors" ? "/doctors" : "/admin/patients";
  const { data, loading, error, reload } = useFetch(url); const [open, setOpen] = useState(false), [f, setF] = useState(blank), [e, setE] = useState("");
  const set = k => x => setF({ ...f, [k]: x.target.value });
  const add = async ev => { ev.preventDefault(); try { await api.post("/admin/doctors", { ...f, experience: +f.experience }); setOpen(false); setF(blank); reload(); } catch (x) { setE(err(x)); } };
  const del = async id => { if (confirm("Delete this user and all their data?")) { try { await api.delete(`/admin/users/${id}`); reload(); } catch (x) { setE(err(x)); } } };
  if (loading) return <Loading />;
  const cols = { users: ["ID", "Name", "Email", "Role", ""], doctors: ["Name", "Specialization", "Qualification", "Experience"], patients: ["Name", "Email", "Phone", "Gender", "Blood"] }[kind];
  return <><div className="flex justify-between mb-4"><h2 className="text-2xl font-bold capitalize">{kind}</h2>{kind === "doctors" && <Btn onClick={() => { setOpen(true); setE(""); }}>+ Add doctor</Btn>}</div><Alert msg={error || e} />
    <Card>{!data?.length ? <Empty text={`No ${kind}`} /> : <Table head={cols}>{data.map(x => <tr key={x.id} className="border-b">
      {kind === "users" && <><td className="py-2">{x.id}</td><td>{x.name}</td><td>{x.email}</td><td>{x.role}</td><td><Btn className="!bg-red-600" onClick={() => del(x.id)}>Delete</Btn></td></>}
      {kind === "doctors" && <><td className="py-2">{x.name}</td><td>{x.specialization}</td><td>{x.qualification}</td><td>{x.experience} yrs</td></>}
      {kind === "patients" && <><td className="py-2">{x.name}</td><td>{x.email}</td><td>{x.phone}</td><td>{x.gender}</td><td>{x.blood_group}</td></>}</tr>)}</Table>}</Card>
    {open && <Modal title="Add doctor" onClose={() => setOpen(false)}><form onSubmit={add}><Alert msg={e} />
      {[["name", "Name"], ["email", "Email"], ["password", "Password (min 8)"], ["phone", "Phone"], ["specialization", "Specialization"], ["qualification", "Qualification"], ["experience", "Years of experience"]].map(([k, l]) => <input key={k} className={inp} placeholder={l} type={k === "password" ? "password" : k === "experience" ? "number" : "text"} value={f[k]} onChange={set(k)} required={k !== "phone" && k !== "qualification"} />)}
      <Btn className="w-full">Create doctor</Btn></form></Modal>}</>;
}
