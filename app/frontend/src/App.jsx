import { useEffect, useState } from "react";
import "./App.css";
import { useAuth } from "./auth";
import Layout from "./components/Layout";
import Login from "./pages/login";
import GestionCompte from "./pages/admin/gestioncompte";
import Pointage from "./pages/pointage/pointage";
import DemandesConges from "./pages/validateur/demadesConges";
import DemandesPermissions from "./pages/validateur/demandesPermissions";
import DashboardEmp from "./pages/employe/dashboardEmp";
import MesConges from "./pages/employe/mesConges";
import MonPointage from "./pages/employe/monPointage";
import AuditLog from "./pages/admin/auditlog";

const ALL = ["EMPLOYE", "AGENT_POINTAGE", "VALIDATEUR_CONGE", "ADMIN_COMPTES"];

// Les pages propres à un rôle viennent en premier : c’est la page d’accueil de ce rôle.
const PAGES = [
  { key: "comptes", label: "Gestion des comptes", C: GestionCompte, roles: ["ADMIN_COMPTES"] },
  { key: "pointage", label: "Saisie des pointages", C: Pointage, roles: ["AGENT_POINTAGE"] },
  { key: "demandes-conges", label: "Demandes de congés", C: DemandesConges, roles: ["VALIDATEUR_CONGE"] },
  { key: "demandes-permissions", label: "Demandes de permissions", C: DemandesPermissions, roles: ["VALIDATEUR_CONGE"] },
  { key: "accueil", label: "Tableau de bord", C: DashboardEmp, roles: ALL },
  { key: "mes-conges", label: "Mes congés et permissions", C: MesConges, roles: ALL },
  { key: "mon-pointage", label: "Mon pointage", C: MonPointage, roles: ALL },
  { key: "audit", label: "Journal d’audit", C: AuditLog, roles: ["ADMIN_COMPTES"] },
];

export default function App() {
  const { user, ready } = useAuth();
  const [hash, setHash] = useState(location.hash.slice(1));

  useEffect(() => {
    const onChange = () => setHash(location.hash.slice(1));
    addEventListener("hashchange", onChange);
    return () => removeEventListener("hashchange", onChange);
  }, []);

  if (!ready) return <p className="boot">Chargement…</p>;
  if (!user) return <Login />;

  const items = PAGES.filter((p) => p.roles.includes(user.role));
  const current = items.find((p) => p.key === hash) ?? items[0];
  const Page = current.C;

  return (
    <Layout items={items} current={current.key}>
      <Page key={current.key} />
    </Layout>
  );
}
