import { useState } from "react"; import useFetch from "../hooks/useFetch"; import api, { err } from "../services/api"; import { useAuth } from "../context/Auth.jsx";
import { Card, Loading, Empty, Alert, Btn, Badge, Table } from "../components/ui.jsx";
export default function Appointments() {
  const { user } = useAuth(); const { data, loading, error, reload } = useFetch("/appointments"); const [e, setE] = useState("");
  const act = async (id, status) => { setE(""); try { await api.put(`/appointments/${id}`, { status }); reload(); } catch (x) { setE(err(x)); } };
  const del = async id => { if (!confirm("Delete this appointment?")) return; try { await api.delete(`/appointments/${id}`); reload(); } catch (x) { setE(err(x)); } };
  if (loading) return <Loading />;
  const b = (id, s, l, c = "") => <Btn key={s} className={`mr-1 ${c}`} onClick={() => act(id, s)}>{l}</Btn>;
  return <><h2 className="text-2xl font-bold mb-4">Appointments</h2><Alert msg={error || e} />
    <Card>{!data?.length ? <Empty text="No appointments yet" /> : <Table head={["Date", "Time", "Patient", "Doctor", "Reason", "Status", "Actions"]}>{data.map(a => <tr key={a.id} className="border-b"><td className="py-2">{a.date}</td><td>{a.time}</td><td>{a.patient}</td><td>{a.doctor}</td><td className="max-w-xs truncate">{a.reason}</td><td><Badge s={a.status} /></td>
      <td>{user.role === "PATIENT" && a.status === "PENDING" && b(a.id, "CANCELLED", "Cancel", "!bg-red-600")}
        {user.role === "DOCTOR" && <>{a.status === "PENDING" && b(a.id, "CONFIRMED", "Confirm")}{["PENDING", "CONFIRMED"].includes(a.status) && b(a.id, "COMPLETED", "Complete", "!bg-green-600")}{["PENDING", "CONFIRMED"].includes(a.status) && b(a.id, "CANCELLED", "Cancel", "!bg-red-600")}</>}
        {user.role === "ADMIN" && <Btn className="!bg-red-600" onClick={() => del(a.id)}>Delete</Btn>}</td></tr>)}</Table>}</Card></>;
}
