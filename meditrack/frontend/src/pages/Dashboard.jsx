import { Link } from "react-router-dom"; import useFetch from "../hooks/useFetch"; import { useAuth } from "../context/Auth.jsx";
import { Card, Stat, Loading, Empty, Alert, Badge, Table } from "../components/ui.jsx";

const Bars = ({ data }) => { const max = Math.max(1, ...data.map(d => d[1])); return <div className="space-y-2">{data.map(([l, v]) => <div key={l} className="flex items-center gap-2 text-xs"><span className="w-24 truncate">{l}</span><div className="bg-teal-500 h-4 rounded" style={{ width: `${(v / max) * 100}%`, minWidth: v ? 4 : 0 }} /><b>{v}</b></div>)}</div>; };

function Patient() {
  const a = useFetch("/appointments"), r = useFetch("/medical-records"), p = useFetch("/prescriptions");
  if (a.loading || r.loading || p.loading) return <Loading />;
  const today = new Date().toISOString().slice(0, 10);
  const next = (a.data || []).filter(x => x.date >= today && ["PENDING", "CONFIRMED"].includes(x.status)).sort((x, y) => (x.date + x.time).localeCompare(y.date + y.time))[0];
  return <><Alert msg={a.error || r.error || p.error} />
    <div className="grid sm:grid-cols-3 gap-4 mb-4"><Stat label="Total appointments" value={a.data?.length} /><Stat label="Medical records" value={r.data?.length} /><Stat label="Prescriptions" value={p.data?.length} /></div>
    <div className="grid md:grid-cols-2 gap-4"><Card title="Upcoming appointment">{next ? <p>{next.date} at {next.time} with <b>{next.doctor}</b> <Badge s={next.status} /></p> : <Empty text="No upcoming appointments" />}</Card>
      <Card title="Quick actions"><div className="flex flex-wrap gap-2">{[["/doctors", "Book Appointment"], ["/appointments", "My Appointments"], ["/medical-history", "Medical History"], ["/prescriptions", "Prescriptions"], ["/profile", "Profile"]].map(([t, l]) => <Link key={t} to={t} className="px-3 py-1.5 bg-teal-50 text-teal-700 rounded-lg text-sm">{l}</Link>)}</div></Card>
      <Card title="Recent records">{r.data?.length ? r.data.slice(0, 3).map(x => <p key={x.id} className="text-sm py-1">{x.date} — {x.diagnosis}</p>) : <Empty text="No records yet" />}</Card>
      <Card title="Recent prescriptions">{p.data?.length ? p.data.slice(0, 3).map(x => <p key={x.id} className="text-sm py-1">{x.medicine_name} — {x.dosage}, {x.frequency}</p>) : <Empty text="No prescriptions yet" />}</Card></div></>;
}
function Doctor() {
  const s = useFetch("/doctor/stats"), a = useFetch("/appointments");
  if (s.loading || a.loading) return <Loading />;
  return <><Alert msg={s.error || a.error} /><div className="grid sm:grid-cols-4 gap-4 mb-4"><Stat label="Today" value={s.data?.today} /><Stat label="Pending" value={s.data?.pending} /><Stat label="Completed" value={s.data?.completed} /><Stat label="Total patients" value={s.data?.total_patients} /></div>
    <Card title="Recent appointments">{a.data?.length ? <Table head={["Date", "Time", "Patient", "Status"]}>{a.data.slice(0, 6).map(x => <tr key={x.id} className="border-b"><td className="py-2">{x.date}</td><td>{x.time}</td><td>{x.patient}</td><td><Badge s={x.status} /></td></tr>)}</Table> : <Empty text="No appointments" />}
      <Link to="/appointments" className="text-teal-700 text-sm">Manage appointments →</Link></Card></>;
}
function Admin() {
  const { data: d, loading, error } = useFetch("/admin/statistics");
  if (loading) return <Loading />; if (!d) return <Alert msg={error} />;
  return <><div className="grid sm:grid-cols-3 gap-4 mb-4"><Stat label="Total users" value={d.total_users} /><Stat label="Patients" value={d.total_patients} /><Stat label="Doctors" value={d.total_doctors} /><Stat label="Appointments" value={d.total_appointments} /><Stat label="Pending" value={d.pending_appointments} /><Stat label="Completed" value={d.completed_appointments} /></div>
    <div className="grid md:grid-cols-3 gap-4"><Card title="Appointments by status"><Bars data={Object.entries(d.appointments_by_status)} /></Card>
      <Card title="Appointments (last 30 days)">{d.appointments_over_time.length ? <Bars data={d.appointments_over_time.map(x => [x.date, x.count])} /> : <Empty text="No data" />}</Card>
      <Card title="Patients vs doctors"><Bars data={[["Patients", d.total_patients], ["Doctors", d.total_doctors]]} /></Card></div></>;
}
export default function Dashboard() {
  const { user } = useAuth();
  return <><h2 className="text-2xl font-bold mb-4">Welcome, {user.name}</h2>{user.role === "PATIENT" ? <Patient /> : user.role === "DOCTOR" ? <Doctor /> : <Admin />}</>;
}
