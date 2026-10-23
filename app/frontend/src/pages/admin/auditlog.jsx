import { useState } from "react";
import { useFetch } from "../../api";
import { Badge, Empty, Notice, fmtDateTime } from "../../components/ui";

const PAGE = 50;
// action → [libellé, couleur du badge]
const ACTIONS = {
  LOGIN: ["Connexion", "ok"],
  LOGIN_FAILED: ["Échec de connexion", "bad"],
  CREATE: ["Création", "ok"],
  UPDATE: ["Modification", "warn"],
  DELETE: ["Suppression", "bad"],
  DECISION: ["Décision", "warn"],
  LIFT: ["Levée", "warn"],
};
const TABLES = ["compte", "employe", "conge", "permission", "pointage", "avertissement"];
const VIDE = { user_id: "", action: "", table_name: "", du: "", au: "" };

export default function AuditLog() {
  const [f, setF] = useState(VIDE);
  const [page, setPage] = useState(0);
  const comptes = useFetch("/comptes?limit=500");

  const qs = new URLSearchParams({ limit: PAGE + 1, skip: page * PAGE }); // +1 pour savoir s’il y a une suite
  Object.entries(f).forEach(([k, v]) => v && qs.set(k, v));
  const logs = useFetch(`/logs?${qs}`);

  const users = comptes.data ?? [];
  const nomUser = (id) => (id == null ? "—" : users.find((c) => c.id === id)?.username ?? `compte n° ${id}`);
  const rows = (logs.data ?? []).slice(0, PAGE);
  const suite = (logs.data?.length ?? 0) > PAGE;
  const set = (k) => (e) => { setF({ ...f, [k]: e.target.value }); setPage(0); };

  const exporter = () => {
    // Un champ commençant par = + - @ serait interprété comme une formule par Excel
    const esc = (v) => {
      const s = String(v ?? "");
      return `"${(/^[=+\-@]/.test(s) ? `'${s}` : s).replaceAll('"', '""')}"`;
    };
    const head = ["Date", "Utilisateur", "Action", "Table", "N°", "Détails", "Adresse IP"];
    const lines = rows.map((l) =>
      [fmtDateTime(l.timestamp), nomUser(l.user_id), ACTIONS[l.action]?.[0] ?? l.action,
        l.table_name, l.record_id, l.details, l.ip_address].map(esc).join(";"));
    const blob = new Blob(["\ufeff" + [head.map(esc).join(";"), ...lines].join("\n")], { type: "text/csv;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `audit-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <>
      <div className="head">
        <h1>Journal d’audit</h1>
        <p className="muted">Toutes les actions enregistrées par l’application, de la plus récente à la plus ancienne.</p>
      </div>

      <div className="card form">
        <label>Utilisateur
          <select value={f.user_id} onChange={set("user_id")}>
            <option value="">Tous</option>
            {users.map((c) => <option key={c.id} value={c.id}>{c.username}</option>)}
          </select>
        </label>
        <label>Action
          <select value={f.action} onChange={set("action")}>
            <option value="">Toutes</option>
            {Object.entries(ACTIONS).map(([v, [l]]) => <option key={v} value={v}>{l}</option>)}
          </select>
        </label>
        <label>Table
          <select value={f.table_name} onChange={set("table_name")}>
            <option value="">Toutes</option>
            {TABLES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>
        <label>Du<input type="date" value={f.du} onChange={set("du")} /></label>
        <label>Au<input type="date" value={f.au} min={f.du} onChange={set("au")} /></label>
        <button className="btn" onClick={() => { setF(VIDE); setPage(0); }}>Effacer les filtres</button>
      </div>

      <Notice>{logs.error || comptes.error}</Notice>

      {!logs.loading && rows.length === 0 ? <Empty>Aucune entrée pour ces critères.</Empty> : (
        <div className="scroll">
          <table>
            <thead>
              <tr><th>Date et heure</th><th>Utilisateur</th><th>Action</th><th>Table</th><th>N°</th><th>Détails</th><th>Adresse IP</th></tr>
            </thead>
            <tbody>
              {rows.map((l) => (
                <tr key={l.id}>
                  <td>{fmtDateTime(l.timestamp)}</td>
                  <td>{nomUser(l.user_id)}</td>
                  <td><Badge value={ACTIONS[l.action]?.[0] ?? l.action} tone={ACTIONS[l.action]?.[1] ?? "warn"} /></td>
                  <td>{l.table_name || "—"}</td>
                  <td>{l.record_id ?? "—"}</td>
                  <td>{l.details || "—"}</td>
                  <td>{l.ip_address || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="row pager">
        <button className="btn" disabled={page === 0} onClick={() => setPage(page - 1)}>Précédent</button>
        <span className="muted">Page {page + 1}</span>
        <button className="btn" disabled={!suite} onClick={() => setPage(page + 1)}>Suivant</button>
        <button className="btn" disabled={rows.length === 0} onClick={exporter}>Exporter cette page (CSV)</button>
      </div>
    </>
  );
}