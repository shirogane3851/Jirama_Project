import { ROLES, useAuth } from "../auth";
import logo from "../../static/icon/logo_jirama.jpg";
import logoutIcon from "../../static/icon/logout.png";
import userIcon from "../../static/icon/user.png";

export default function Layout({ items, current, children }) {
  const { user, logout } = useAuth();
  return (
    <div className="shell">
      <header className="top">
        <div className="brand">
          <img src={logo} alt="Jirama" />
          <span>Gestion du personnel</span>
        </div>
        <div className="who">
          <img className="avatar" src={userIcon} alt="" />
          <div>
            <strong>{user.employe.prenom} {user.employe.nom}</strong>
            <small>{ROLES[user.role]}</small>
          </div>
          <button className="icon-btn" onClick={logout} aria-label="Se déconnecter" title="Se déconnecter">
            <img src={logoutIcon} width="20px" alt="" />
          </button>
        </div>
      </header>
      <div className="body">
        <section className="content">{children}</section>
        <nav className="menu" aria-label="Navigation principale">
          {items.map((p) => (
            <a key={p.key} href={`#${p.key}`} aria-current={p.key === current ? "page" : undefined}>
              {p.label}
            </a>
          ))}
        </nav>
      </div>
    </div>
  );
}
