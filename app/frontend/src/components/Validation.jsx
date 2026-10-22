import { useState } from "react";
import { api, useFetch } from "../api";
import { Badge, Empty, Feedback, fmtDate, jours, useEmployes, useFeedback } from "./ui";

const FILTRES = [["en_attente", "En attente"], ["approuve", "Approuvées"], ["refuse", "Refusées"], ["", "Toutes"]];

/** Liste + décision (approuver / refuser) pour /conges ou /permissions. */
export default function Validation({ path, title }) {
  const { nom } = useEmployes();
  const [statut, setStatut] = useState("en_attente");
  const list = useFetch(`${path}?limit=200${statut ? `&statut=${statut}` : ""}`);
  const [fb, run] = useFeedback();
  const rows = list.data ?? [];

  const decide = (id, s) =>
    run(async () => {
      await api(`${path}/${id}/decision`, { method: "POST", body: { statut: s } });
      list.reload();
    }, s === "approuve" ? "Demande approuvée." : "Demande refusée.");

  return (
    <>
      <div className="head"><h1>{title}</h1></div>
      <div className="tabs">
        {FILTRES.map(([v, l]) => (
          <button key={v} className="btn" aria-pressed={statut === v} onClick={() => setStatut(v)}>{l}</button>
        ))}
      </div>
      <Feedback fb={fb} extra={list.error} />
      {!list.loading && rows.length === 0 ? (
        <Empty>Aucune demande dans cette catégorie.</Empty>
      ) : (
        <div className="scroll">
          <table>
            <thead>
              <tr><th>Employé</th><th>Période</th><th>Jours</th><th>Motif</th><th>Statut</th><th></th></tr>
            </thead>
            <tbody>
              {rows.map((d) => (
                <tr key={d.id}>
                  <td>{nom(d.employe_id)}</td>
                  <td>{fmtDate(d.date_debut)} au {fmtDate(d.date_fin)}</td>
                  <td>{jours(d.date_debut, d.date_fin)}</td>
                  <td>{d.motif || "—"}</td>
                  <td><Badge value={d.statut} /></td>
                  <td>
                    {d.statut === "en_attente" && (
                      <div className="row">
                        <button className="btn primary" onClick={() => decide(d.id, "approuve")}>Approuver</button>
                        <button className="btn danger" onClick={() => decide(d.id, "refuse")}>Refuser</button>
                      </div>
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
