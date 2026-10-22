import { useAuth } from "../../auth";
import { useFetch } from "../../api";
import { Badge, Empty, Notice, TYPE_POINTAGE, fmtDate, fmtDateTime, jours } from "../../components/ui";

export default function DashboardEmp() {
  const { user } = useAuth();
  const id = user.employe_id;
  const emp = useFetch(`/employes/${id}`);
  const conges = useFetch(`/conges?employe_id=${id}&limit=5`);
  const avert = useFetch(`/avertissements?employe_id=${id}&statut=actif&limit=100`);
  const point = useFetch(`/pointages?employe_id=${id}&limit=1`);

  const dernier = point.data?.[0];
  const nb = avert.data?.length ?? 0;
  const demandes = conges.data ?? [];

  return (
    <>
      <div className="head">
        <h1>Bonjour {user.employe.prenom}</h1>
        <p className="muted">Voici votre situation du jour.</p>
      </div>
      <Notice>{emp.error || conges.error || avert.error || point.error}</Notice>

      <div className="card solde">
        <b>{emp.data ? Number(emp.data.solde_conge) : "…"}</b>
        <span>jours de congé restants</span>
      </div>

      <div className="grid2">
        <div className="card">
          <h2>Dernier pointage</h2>
          {dernier
            ? <p>{TYPE_POINTAGE[dernier.type]} le {fmtDateTime(dernier.timestamp)}</p>
            : <p className="muted">Aucun pointage enregistré.</p>}
        </div>
        <div className="card">
          <h2>Avertissements actifs</h2>
          <p>{nb === 0 ? "Aucun avertissement actif." : `${nb} avertissement${nb > 1 ? "s" : ""} actif${nb > 1 ? "s" : ""}.`}</p>
        </div>
      </div>

      <div className="card">
        <h2>Mes dernières demandes de congé</h2>
        {demandes.length === 0 ? (
          <Empty>Vous n’avez fait aucune demande. Rendez-vous dans « Mes congés et permissions ».</Empty>
        ) : (
          <div className="scroll">
            <table>
              <thead><tr><th>Période</th><th>Jours</th><th>Statut</th></tr></thead>
              <tbody>
                {demandes.map((d) => (
                  <tr key={d.id}>
                    <td>{fmtDate(d.date_debut)} au {fmtDate(d.date_fin)}</td>
                    <td>{jours(d.date_debut, d.date_fin)}</td>
                    <td><Badge value={d.statut} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
