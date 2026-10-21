import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/employes";

const formulaireInitial = {
  matricule: "",
  nom: "",
  prenom: "",
  telephone: "",
  email: "",
  date_embauche: "",
};

function App() {
  const [formulaire, setFormulaire] = useState(formulaireInitial);
  const [chargement, setChargement] = useState(false);
  const [message, setMessage] = useState("");
  const [erreur, setErreur] = useState(false);

  function gererChangement(e) {
    const { name, value } = e.target;

    setFormulaire((precedent) => ({
      ...precedent,
      [name]: value,
    }));
  }

  async function ajouterEmploye(e) {
    e.preventDefault();

    setChargement(true);
    setMessage("");
    setErreur(false);

    const donnees = {
      ...formulaire,
      telephone: formulaire.telephone || null,
      email: formulaire.email || null,
      date_embauche: formulaire.date_embauche || null,
    };

    try {
      const reponse = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(donnees),
      });

      const resultat = await reponse.json().catch(() => null);

      if (!reponse.ok) {
        throw new Error(
          resultat?.detail || "Impossible d'ajouter l'employé."
        );
      }

      setMessage("L'employé a été ajouté avec succès.");
      setFormulaire(formulaireInitial);
    } catch (err) {
      setErreur(true);

      if (err instanceof TypeError) {
        setMessage(
          "Impossible de contacter le serveur. Vérifiez que FastAPI fonctionne."
        );
      } else {
        setMessage(err.message);
      }
    } finally {
      setChargement(false);
    }
  }

  return (
    <main className="page">
      <header className="entete">
        <div className="logo">J</div>

        <div>
          <h1>JIRAMA</h1>
          <p>Gestion du personnel</p>
        </div>
      </header>

      <section className="contenu">
        <div className="navigation">
          <span>Personnel</span>
          <span className="separateur">/</span>
          <strong>Ajouter un employé</strong>
        </div>

        <div className="carte">
          <div className="carte-entete">
            <div>
              <h2>Nouvel employé</h2>
              <p>Renseignez les informations du personnel.</p>
            </div>

            <span className="badge">Nouveau dossier</span>
          </div>

          {message && (
            <div
              className={`message ${erreur ? "message-erreur" : "message-succes"}`}
              role="status"
            >
              {message}
            </div>
          )}

          <form onSubmit={ajouterEmploye}>
            <div className="section-titre">
              <span className="numero">01</span>
              <div>
                <h3>Informations personnelles</h3>
                <p>Identité de l'employé</p>
              </div>
            </div>

            <div className="grille">
              <div className="champ">
                <label htmlFor="matricule">
                  Matricule <span>*</span>
                </label>

                <input
                  id="matricule"
                  name="matricule"
                  value={formulaire.matricule}
                  onChange={gererChangement}
                  placeholder="Ex. JIR-2026-001"
                  maxLength={15}
                  required
                />
              </div>

              <div className="champ">
                <label htmlFor="nom">
                  Nom <span>*</span>
                </label>

                <input
                  id="nom"
                  name="nom"
                  value={formulaire.nom}
                  onChange={gererChangement}
                  placeholder="Nom de famille"
                  maxLength={100}
                  required
                />
              </div>

              <div className="champ">
                <label htmlFor="prenom">
                  Prénom <span>*</span>
                </label>

                <input
                  id="prenom"
                  name="prenom"
                  value={formulaire.prenom}
                  onChange={gererChangement}
                  placeholder="Prénom"
                  maxLength={100}
                  required
                />
              </div>

              <div className="champ">
                <label htmlFor="date_embauche">
                  Date d'embauche
                </label>

                <input
                  id="date_embauche"
                  name="date_embauche"
                  type="date"
                  value={formulaire.date_embauche}
                  onChange={gererChangement}
                />
              </div>
            </div>

            <div className="section-titre section-suivante">
              <span className="numero">02</span>
              <div>
                <h3>Coordonnées</h3>
                <p>Informations de contact</p>
              </div>
            </div>

            <div className="grille">
              <div className="champ">
                <label htmlFor="telephone">Téléphone</label>

                <input
                  id="telephone"
                  name="telephone"
                  type="tel"
                  value={formulaire.telephone}
                  onChange={gererChangement}
                  placeholder="Numéro de téléphone"
                  maxLength={14}
                />
              </div>

              <div className="champ">
                <label htmlFor="email">Adresse e-mail</label>

                <input
                  id="email"
                  name="email"
                  type="email"
                  value={formulaire.email}
                  onChange={gererChangement}
                  placeholder="employe@exemple.mg"
                  maxLength={100}
                />
              </div>
            </div>

            <div className="note">
              <span>*</span>
              Les champs marqués d'un astérisque sont obligatoires.
            </div>

            <div className="actions">
              <button
                type="button"
                className="bouton-annuler"
                onClick={() => {
                  setFormulaire(formulaireInitial);
                  setMessage("");
                  setErreur(false);
                }}
                disabled={chargement}
              >
                Réinitialiser
              </button>

              <button
                type="submit"
                className="bouton-ajouter"
                disabled={chargement}
              >
                {chargement ? "Enregistrement..." : "Ajouter l'employé"}
              </button>
            </div>
          </form>
        </div>

        <footer>
          JIRAMA · Système de gestion du personnel
        </footer>
      </section>
    </main>
  );
}

export default App;