import { useState } from "react";
import { useFetch } from "../api";

const parse = (d) => new Date(d.length === 10 ? `${d}T00:00:00` : d);
export const fmtDate = (d) => (d ? parse(d).toLocaleDateString("fr-FR") : "—");
export const fmtDateTime = (d) =>
  d ? parse(d).toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" }) : "—";
/** Nombre de jours, bornes comprises (même calcul que l’API pour le solde). */
export const jours = (debut, fin) => Math.round((parse(fin) - parse(debut)) / 864e5) + 1;
export const nowLocal = () =>
  new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16);
/** Chaînes vides → null (l’API refuse "" pour un e-mail, par exemple). */
export const clean = (o) =>
  Object.fromEntries(Object.entries(o).map(([k, v]) => [k, v === "" ? null : v]));

export const TYPE_POINTAGE = { entree: "Entrée", sortie: "Sortie" };
export const TYPE_AVERT = { retard: "Retard", absence: "Absence" };
const LABELS = { en_attente: "En attente", approuve: "Approuvé", refuse: "Refusé", actif: "Actif", leve: "Levé" };
const TONES = { en_attente: "warn", approuve: "ok", refuse: "bad", actif: "bad", leve: "ok" };

export function Badge({ value, tone }) {
  return <span className={`badge b-${tone ?? TONES[value] ?? "warn"}`}>{LABELS[value] ?? value}</span>;
}

export function Notice({ kind = "error", children }) {
  if (!children) return null;
  return (
    <p className={`notice ${kind}`} role={kind === "error" ? "alert" : "status"}>
      {children}
    </p>
  );
}

export const Empty = ({ children }) => <p className="muted empty">{children}</p>;

/** Messages de succès / d’erreur autour d’une action. */
export function useFeedback() {
  const [fb, setFb] = useState({ error: "", ok: "" });
  const run = async (fn, okText) => {
    setFb({ error: "", ok: "" });
    try {
      await fn();
      if (okText) setFb({ error: "", ok: okText });
      return true;
    } catch (e) {
      setFb({ error: e.message, ok: "" });
      return false;
    }
  };
  return [fb, run];
}

export function Feedback({ fb, extra }) {
  return (
    <>
      <Notice>{fb.error || extra}</Notice>
      <Notice kind="ok">{fb.ok}</Notice>
    </>
  );
}

/** Liste des employés (réservée aux rôles agent, validateur et admin). */
export function useEmployes() {
  const { data, reload } = useFetch("/employes?limit=500");
  const list = data ?? [];
  const nom = (id) => {
    const e = list.find((x) => x.id === id);
    return e ? `${e.prenom} ${e.nom}` : `Employé n° ${id}`;
  };
  return { list, nom, reload };
}
