import { useState } from "react";
import { useAuth } from "../../auth";
import { useFetch } from "../../api";
import { Badge, Empty, Notice, TYPE_AVERT, TYPE_POINTAGE, fmtDateTime } from "../../components/ui";

export default function MonPointage() {
  const { user } = useAuth();
  const id = user.employe_id;
  const [du, setDu] = useState("");
  const [au, setAu] = useState("");
  const pointages = useFetch(`/pointages?employe_id=${id}&limit=100${du ? `&du=${du}` : ""}${au ? `&au=${au}` : ""}`);
  const avert = useFetch(`/avertissements?employe_id=${id}&limit=100`);
  const pts = pointages.data ?? [];
  const avs = avert.data ?? [];

  return (
    <>
      <div className="head"><h1>Mon pointage</h1></div>
      <Notice>{pointages.error || avert.error}</Notice>

      <div className="card form">
        <label>Du<input type="date" value={du} onChange={(e) => setDu(e.target.value)} /></label>
        <label>Au<input type="date" value={au} min={du} onChange={(e) => setAu(e.target.value)} /></label>
        <button className="btn" onClick={() => { setDu(""); setAu(""); }}>Effacer les dates</button>
      </div>

      <div className="grid2">
        <div>
          <h2>Pointages</h2>
          {!pointages.loading && pts.length === 0 ? <Empty>Aucun pointage sur cette période.</Empty> : (
            <div className="scroll">
              <table>
                <thead><tr><th>Date et heure</th><th>Type</th></tr></thead>
                <tbody>
                  {pts.map((p) => (
                    <tr key={p.id}><td>{fmtDateTime(p.timestamp)}</td><td>{TYPE_POINTAGE[p.type]}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
        <div>
          <h2>Avertissements</h2>
          {!avert.loading && avs.length === 0 ? <Empty>Aucun avertissement.</Empty> : (
            <div className="scroll">
              <table>
                <thead><tr><th>Date</th><th>Type</th><th>Motif</th><th>Statut</th></tr></thead>
                <tbody>
                  {avs.map((a) => (
                    <tr key={a.id}>
                      <td>{fmtDateTime(a.date_concernee)}</td>
                      <td>{TYPE_AVERT[a.type] ?? a.type}</td>
                      <td>{a.motif || "—"}{a.lifted_reason ? ` (levé : ${a.lifted_reason})` : ""}</td>
                      <td><Badge value={a.statut} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
