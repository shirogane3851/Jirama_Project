import { useState } from "react";
import { ROLES } from "../../auth";
import { api, useFetch } from "../../api";
import { Badge, Empty, Feedback, clean, useEmployes, useFeedback } from "../../components/ui";

const EMP0 = { nom: "", prenom: "", matricule: "", telephone: "", email: "", date_embauche: "", solde_conge: "" };
const CPT0 = { employe_id: "", username: "", role: "EMPLOYE", password: "" };

export default function GestionCompte() {
  const comptes = useFetch("/comptes?limit=500");
  const { list: employes, nom, reload: reloadEmployes } = useEmployes();
  const [mode, setMode] = useState("compte");
  const [emp, setEmp] = useState(EMP0);
  const [cpt, setCpt] = useState(CPT0);
  const [fb, run] = useFeedback();

  const rows = comptes.data ?? [];
  const avecCompte = new Set(rows.map((c) => c.employe_id));
  const libres = employes.filter((e) => !avecCompte.has(e.id));
  const setE = (k) => (e) => setEmp({ ...emp, [k]: e.target.value });
  const setC = (k) => (e) => setCpt({ ...cpt, [k]: e.target.value });

  const creerEmploye = (e) => {
    e.preventDefault();
    run(async () => {
      const body = clean(emp);
      body.solde_conge = Number(emp.solde_conge || 0);
      if (body.date_embauche) body.date_embauche = `${body.date_embauche}T00:00:00`;
      await api("/employes", { method: "POST", body });
      setEmp(EMP0);
      reloadEmployes();
    }, "Employé créé. Vous pouvez maintenant lui ouvrir un compte.");
  };

  const creerCompte = (e) => {
    e.preventDefault();
    run(async () => {
      await api("/comptes", { method: "POST", body: { ...cpt, employe_id: Number(cpt.employe_id) } });
      setCpt(CPT0);
      comptes.reload();
    }, "Compte créé.");
  };

  const maj = (id, body, ok) =>
    run(async () => {
      await api(`/comptes/${id}`, { method: "PATCH", body });
      comptes.reload();
    }, ok);

  const motDePasse = (c) => {
    const p = prompt(`Nouveau mot de passe pour ${c.username} (8 caractères minimum) :`);
    if (p) maj(c.id, { password: p }, "Mot de passe modifié.");
  };

  return (
    <>
      <div className="head"><h1>Gestion des comptes</h1></div>

      <div className="card">
        <div className="tabs">
          <button className="btn" aria-pressed={mode === "compte"} onClick={() => setMode("compte")}>Nouveau compte</button>
          <button className="btn" aria-pressed={mode === "employe"} onClick={() => setMode("employe")}>Nouvel employé</button>
        </div>

        {mode === "compte" ? (
          <form className="form" onSubmit={creerCompte}>
            <label>Employé
              <select value={cpt.employe_id} onChange={setC("employe_id")} required>
                <option value="">Choisir…</option>
                {libres.map((e) => <option key={e.id} value={e.id}>{e.nom} {e.prenom} ({e.matricule})</option>)}
              </select>
            </label>
            <label>Identifiant<input value={cpt.username} maxLength={50} onChange={setC("username")} required autoComplete="off" /></label>
            <label>Rôle
              <select value={cpt.role} onChange={setC("role")}>
                {Object.entries(ROLES).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </label>
            <label>Mot de passe<input type="password" minLength={8} value={cpt.password} onChange={setC("password")} required autoComplete="new-password" /></label>
            <button className="btn primary">Créer le compte</button>
          </form>
        ) : (
          <form className="form" onSubmit={creerEmploye}>
            <label>Nom<input value={emp.nom} maxLength={100} onChange={setE("nom")} required /></label>
            <label>Prénom<input value={emp.prenom} maxLength={100} onChange={setE("prenom")} required /></label>
            <label>Matricule<input value={emp.matricule} maxLength={15} onChange={setE("matricule")} required /></label>
            <label>Téléphone<input value={emp.telephone} maxLength={14} onChange={setE("telephone")} /></label>
            <label>E-mail<input type="email" value={emp.email} maxLength={100} onChange={setE("email")} /></label>
            <label>Date d’embauche<input type="date" value={emp.date_embauche} onChange={setE("date_embauche")} /></label>
            <label>Solde de congé (jours)<input type="number" min="0" max="999" step="0.5" value={emp.solde_conge} onChange={setE("solde_conge")} /></label>
            <button className="btn primary">Créer l’employé</button>
          </form>
        )}
      </div>

      <Feedback fb={fb} extra={comptes.error} />

      {!comptes.loading && rows.length === 0 ? <Empty>Aucun compte pour le moment.</Empty> : (
        <div className="scroll">
          <table>
            <thead><tr><th>Employé</th><th>Identifiant</th><th>Rôle</th><th>Statut</th><th></th></tr></thead>
            <tbody>
              {rows.map((c) => (
                <tr key={c.id}>
                  <td>{nom(c.employe_id)}</td>
                  <td>{c.username}</td>
                  <td>
                    <select value={c.role} aria-label={`Rôle de ${c.username}`}
                      onChange={(e) => maj(c.id, { role: e.target.value }, "Rôle modifié.")}>
                      {Object.entries(ROLES).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                    </select>
                  </td>
                  <td><Badge value={c.is_active ? "Actif" : "Inactif"} tone={c.is_active ? "ok" : "bad"} /></td>
                  <td>
                    <div className="row">
                      <button className="btn" onClick={() => maj(c.id, { is_active: !c.is_active }, c.is_active ? "Compte désactivé." : "Compte réactivé.")}>
                        {c.is_active ? "Désactiver" : "Réactiver"}
                      </button>
                      <button className="btn" onClick={() => motDePasse(c)}>Changer le mot de passe</button>
                    </div>
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
