import { useState } from "react";
import { api, useFetch } from "../../api";
import {
  Badge, Empty, Feedback, TYPE_AVERT, TYPE_POINTAGE, fmtDateTime, nowLocal, useEmployes, useFeedback,
} from "../../components/ui";
import searchIcon from "../../../static/icon/search.png";
import Photo from "../../components/Photo";

export default function Pointage() {
  const { list, nom } = useEmployes();
  const [q, setQ] = useState("");
  const [employeId, setEmployeId] = useState("");
  const [av, setAv] = useState({ type: "retard", date_concernee: nowLocal(), motif: "" });
  const pointages = useFetch("/pointages?limit=30");
  const avert = useFetch("/avertissements?statut=actif&limit=100");
  const [fb, run] = useFeedback();

  const filtres = list.filter((e) => `${e.nom} ${e.prenom} ${e.matricule}`.toLowerCase().includes(q.toLowerCase()));
  const sel = list.find((e) => String(e.id) === employeId);
  const choisi = sel ? `${sel.prenom} ${sel.nom}` : "";
  const emp = (id) => list.find((e) => e.id === id) ?? { id, nom: "", prenom: "" };

  const pointer = (type) =>
    run(async () => {
      await api("/pointages", { method: "POST", body: { employe_id: Number(employeId), type } });
      pointages.reload();
    }, `${TYPE_POINTAGE[type]} enregistrée pour ${choisi}.`);

  const avertir = (e) => {
    e.preventDefault();
    run(async () => {
      await api("/avertissements", {
        method: "POST",
        body: { employe_id: Number(employeId), type: av.type, date_concernee: av.date_concernee, motif: av.motif || null },
      });
      setAv({ ...av, motif: "" });
      avert.reload();
    }, `Avertissement enregistré pour ${choisi}.`);
  };

  const lever = (id) => {
    const raison = prompt("Motif de la levée de l’avertissement :");
    if (!raison) return;
    run(async () => {
      await api(`/avertissements/${id}/lift`, { method: "POST", body: { lifted_reason: raison } });
      avert.reload();
    }, "Avertissement levé.");
  };

  const pts = pointages.data ?? [];
  const avs = avert.data ?? [];

  return (
    <>
      <div className="head"><h1>Saisie des pointages</h1></div>
      <Feedback fb={fb} extra={pointages.error || avert.error} />

      <div className="grid2">
        <div className="card">
          <h2>1. Choisir l’employé</h2>
          <label className="search">
            <span className="sr">Rechercher</span>
            <img src={searchIcon} alt="" />
            <input placeholder="Nom, prénom ou matricule" value={q} onChange={(e) => setQ(e.target.value)} />
          </label>
          {sel && (
            <div className="emp-choisi">
            <Photo key={sel.id} employe={sel} size={96} rond={false} />
            <div><h3>{sel.prenom} {sel.nom}</h3><p className="muted">{sel.matricule}</p></div>
            </div>
          )}
          <ul className="liste-emp" role="listbox" aria-label="Employés">
            {filtres.map((e) => (
              <li key={e.id}>
                <button type="button" role="option" aria-selected={String(e.id) === employeId}
                  className="emp-btn" onClick={() => setEmployeId(String(e.id))}>
                  <Photo employe={e} size={40} />
                  <span><strong>{e.nom} {e.prenom}</strong><small>{e.matricule}</small></span>
                </button>
              </li>
            ))}
          </ul>
          <div className="row">
            <button className="btn primary" disabled={!employeId} onClick={() => pointer("entree")}>Enregistrer l’entrée</button>
            <button className="btn primary" disabled={!employeId} onClick={() => pointer("sortie")}>Enregistrer la sortie</button>
          </div>
        </div>

        <form className="card form" onSubmit={avertir}>
          <h2 className="wide">Nouvel avertissement{choisi && ` pour ${choisi}`}</h2>
          <label>Type
            <select value={av.type} onChange={(e) => setAv({ ...av, type: e.target.value })}>
              {Object.entries(TYPE_AVERT).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </label>
          <label>Date concernée
            <input type="datetime-local" value={av.date_concernee} onChange={(e) => setAv({ ...av, date_concernee: e.target.value })} required />
          </label>
          <label className="wide">Motif
            <input value={av.motif} maxLength={100} onChange={(e) => setAv({ ...av, motif: e.target.value })} />
          </label>
          <button className="btn primary" disabled={!employeId}>Enregistrer l’avertissement</button>
        </form>
      </div>

      <h2>Derniers pointages</h2>
      {!pointages.loading && pts.length === 0 ? <Empty>Aucun pointage enregistré.</Empty> : (
        <div className="scroll">
          <table>
            <thead><tr><th>Employé</th><th>Type</th><th>Date et heure</th></tr></thead>
            <tbody>
              {pts.map((p) => (
                <tr key={p.id}><td><span className="cell-emp"><Photo employe={emp(p.employe_id)} size={28} />{nom(p.employe_id)}</span></td><td>{TYPE_POINTAGE[p.type]}</td><td>{fmtDateTime(p.timestamp)}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <h2 className="gap">Avertissements actifs</h2>
      {!avert.loading && avs.length === 0 ? <Empty>Aucun avertissement actif.</Empty> : (
        <div className="scroll">
          <table>
            <thead><tr><th>Employé</th><th>Type</th><th>Date</th><th>Motif</th><th>Statut</th><th></th></tr></thead>
            <tbody>
              {avs.map((a) => (
                <tr key={a.id}>
                  <td><span className="cell-emp"><Photo employe={emp(a.employe_id)} size={28} />{nom(a.employe_id)}</span></td>
                  <td>{TYPE_AVERT[a.type] ?? a.type}</td>
                  <td>{fmtDateTime(a.date_concernee)}</td>
                  <td>{a.motif || "—"}</td>
                  <td><Badge value={a.statut} /></td>
                  <td><button className="btn" onClick={() => lever(a.id)}>Lever</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
