import { useState } from "react";
import { useAuth } from "../../auth";
import { api, useFetch } from "../../api";
import { Badge, Empty, Feedback, clean, fmtDate, jours, useFeedback } from "../../components/ui";

const KINDS = [
  ["/conges", "Congés", "congé"],
  ["/permissions", "Permissions", "permission"],
];
const VIDE = { date_debut: "", date_fin: "", motif: "" };

export default function MesConges() {
  const [kind, setKind] = useState(0);
  return (
    <>
      <div className="head"><h1>Mes congés et permissions</h1></div>
      <div className="tabs">
        {KINDS.map(([, label], i) => (
          <button key={label} className="btn" aria-pressed={kind === i} onClick={() => setKind(i)}>{label}</button>
        ))}
      </div>
      <Demandes key={kind} path={KINDS[kind][0]} noun={KINDS[kind][2]} />
    </>
  );
}

function Demandes({ path, noun }) {
  const { user } = useAuth();
  const list = useFetch(`${path}?employe_id=${user.employe_id}&limit=100`);
  const [form, setForm] = useState(VIDE);
  const [fb, run] = useFeedback();
  const rows = list.data ?? [];
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const envoyer = (e) => {
    e.preventDefault();
    run(async () => {
      await api(path, { method: "POST", body: { employe_id: user.employe_id, ...clean(form) } });
      setForm(VIDE);
      list.reload();
    }, `Votre demande de ${noun} a été envoyée.`);
  };

  const annuler = (id) => {
    if (!confirm("Annuler cette demande ?")) return;
    run(async () => {
      await api(`${path}/${id}`, { method: "DELETE" });
      list.reload();
    }, "Demande annulée.");
  };

  return (
    <>
      <form className="card form" onSubmit={envoyer}>
        <label>Du<input type="date" value={form.date_debut} onChange={set("date_debut")} required /></label>
        <label>Au<input type="date" value={form.date_fin} min={form.date_debut} onChange={set("date_fin")} required /></label>
        <label>Motif<input value={form.motif} maxLength={100} onChange={set("motif")} /></label>
        <button className="btn primary">Envoyer la demande</button>
      </form>
      <Feedback fb={fb} extra={list.error} />
      {!list.loading && rows.length === 0 ? (
        <Empty>Aucune demande pour le moment.</Empty>
      ) : (
        <div className="scroll">
          <table>
            <thead><tr><th>Période</th><th>Jours</th><th>Motif</th><th>Statut</th><th></th></tr></thead>
            <tbody>
              {rows.map((d) => (
                <tr key={d.id}>
                  <td>{fmtDate(d.date_debut)} au {fmtDate(d.date_fin)}</td>
                  <td>{jours(d.date_debut, d.date_fin)}</td>
                  <td>{d.motif || "—"}</td>
                  <td><Badge value={d.statut} /></td>
                  <td>
                    {d.statut === "en_attente" && (
                      <button className="btn danger" onClick={() => annuler(d.id)}>Annuler</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
