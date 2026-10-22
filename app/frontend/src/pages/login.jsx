import { useState } from "react";
import { useAuth } from "../auth";
import { Notice } from "../components/ui";
import logo from "../../static/icon/logo_jirama.jpg";

export default function Login() {
  const { login } = useAuth();
  const [f, setF] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(f.username.trim(), f.password);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <main className="login">
      <form className="card" onSubmit={submit}>
        <img src={logo} alt="Jirama" />
        <h1>Connexion</h1>
        <p className="muted">Utilisez l’identifiant fourni par l’administrateur.</p>
        <Notice>{error}</Notice>
        <label>Identifiant
          <input value={f.username} onChange={set("username")} autoComplete="username" required autoFocus />
        </label>
        <label>Mot de passe
          <input type="password" value={f.password} onChange={set("password")} autoComplete="current-password" required />
        </label>
        <button className="btn primary" disabled={busy}>{busy ? "Connexion…" : "Se connecter"}</button>
      </form>
    </main>
  );
}
