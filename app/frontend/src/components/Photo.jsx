import { useEffect, useState } from "react";
import { BASE, getToken } from "../api";

const initiales = (e) => `${(e.prenom || "")[0] ?? ""}${(e.nom || "")[0] ?? ""}`.toUpperCase();

/** Photo d’un employé, ou ses initiales s’il n’en a pas. */
export default function Photo({ employe, size = 44, rond = true, version = 0 }) {
  const [src, setSrc] = useState(null);

  useEffect(() => {
    let annule = false;
    let url = null;
    setSrc(null);
    fetch(`${BASE}/employes/${employe.id}/photo`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
      .then((r) => (r.ok ? r.blob() : Promise.reject()))
      .then((b) => {
        if (annule) return;
        url = URL.createObjectURL(b);
        setSrc(url);
      })
      .catch(() => {});             // pas de photo : on garde les initiales
    return () => {
      annule = true;
      if (url) URL.revokeObjectURL(url);
    };
  }, [employe.id, version]);

  const forme = { width: size, height: size, borderRadius: rond ? "50%" : "10px" };
  if (!src) {
    return <span className="avatar-init" style={{ ...forme, fontSize: size * 0.38 }} aria-hidden="true">{initiales(employe)}</span>;
  }
  return <img className="photo" style={forme} alt="" src={src} />;
}