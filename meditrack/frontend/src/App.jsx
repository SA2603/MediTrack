import { Routes, Route, Navigate, NavLink, Outlet } from "react-router-dom";
import { useAuth } from "./context/Auth.jsx";
import Auth from "./pages/Auth.jsx"; import Dashboard from "./pages/Dashboard.jsx"; import Doctors from "./pages/Doctors.jsx";
import Appointments from "./pages/Appointments.jsx"; import Records from "./pages/Records.jsx"; import Prescriptions from "./pages/Prescriptions.jsx";
import Profile from "./pages/Profile.jsx"; import AdminList from "./pages/AdminList.jsx";

const NAV = { PATIENT: [["/dashboard", "Dashboard"], ["/doctors", "Doctors"], ["/appointments", "Appointments"], ["/medical-history", "History"], ["/prescriptions", "Prescriptions"], ["/profile", "Profile"]],
  DOCTOR: [["/dashboard", "Dashboard"], ["/appointments", "Appointments"], ["/medical-history", "Records"], ["/prescriptions", "Prescriptions"], ["/profile", "Profile"]],
  ADMIN: [["/dashboard", "Dashboard"], ["/admin/users", "Users"], ["/admin/doctors", "Doctors"], ["/admin/patients", "Patients"], ["/appointments", "Appointments"]] };

function Layout() {
  const { user, logout } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return <div><nav className="bg-teal-700 text-white px-4 py-3 flex flex-wrap items-center gap-4 noprint">
    <b className="text-lg">✚ MEDTRACK</b>
    {NAV[user.role].map(([to, l]) => <NavLink key={to} to={to} className={({ isActive }) => `text-sm ${isActive ? "underline font-semibold" : "opacity-80 hover:opacity-100"}`}>{l}</NavLink>)}
    <span className="ml-auto text-sm">{user.name} ({user.role})</span>
    <button onClick={logout} className="bg-white/20 px-3 py-1 rounded text-sm">Logout</button></nav>
    <main className="max-w-6xl mx-auto p-4"><Outlet /></main></div>;
}
const Guard = ({ roles, children }) => { const { user } = useAuth(); return roles.includes(user.role) ? children : <Navigate to="/dashboard" replace />; };

export default function App() {
  const { user } = useAuth(); const all = ["PATIENT", "DOCTOR", "ADMIN"];
  return <Routes>
    <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Auth />} />
    <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <Auth register />} />
    <Route element={<Layout />}>
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/doctors" element={<Guard roles={["PATIENT"]}><Doctors /></Guard>} />
      <Route path="/appointments" element={<Appointments />} />
      <Route path="/medical-history" element={<Guard roles={["PATIENT", "DOCTOR"]}><Records /></Guard>} />
      <Route path="/prescriptions" element={<Guard roles={["PATIENT", "DOCTOR"]}><Prescriptions /></Guard>} />
      <Route path="/profile" element={<Guard roles={["PATIENT", "DOCTOR"]}><Profile /></Guard>} />
      <Route path="/admin" element={<Navigate to="/dashboard" />} />
      {["users", "doctors", "patients"].map(k => <Route key={k} path={`/admin/${k}`} element={<Guard roles={["ADMIN"]}><AdminList kind={k} /></Guard>} />)}
      <Route path="/admin/appointments" element={<Guard roles={["ADMIN"]}><Appointments /></Guard>} />
    </Route>
    <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
  </Routes>;
}
