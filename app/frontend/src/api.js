import { useCallback, useEffect, useState } from "react";

export const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

let unauthorizedHandler = () => {};
export const onUnauthorized = (fn) => { unauthorizedHandler = fn; };
export const getToken = () => localStorage.getItem("jirama_token");
export const setToken = (t) =>
  t ? localStorage.setItem("jirama_token", t) : localStorage.removeItem("jirama_token");

function messageFrom(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail.map((d) => `${(d.loc || []).slice(1).join(".")} : ${d.msg}`).join(" ; ");
  return "Une erreur est survenue.";
}

/** Appel à l’API. `form` = envoi x-www-form-urlencoded (login), `body` = JSON. */
export async function api(path, { method = "GET", body, form } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  let payload;
  if (form) payload = new URLSearchParams(form);
  else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }
  let res;
  try {
    res = await fetch(BASE + path, { method, headers, body: payload });
  } catch {
    throw new Error("Impossible de joindre le serveur. Vérifiez que l’API est lancée.");
  }
  if (res.status === 401 && token) unauthorizedHandler();
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(messageFrom(data.detail));
  }
  return res.status === 204 ? null : res.json();
}

/** GET avec état de chargement. Se recharge quand `path` change. */
export function useFetch(path) {
  const [state, setState] = useState({ data: null, error: "", loading: true });
  const load = useCallback(() => {
    setState((s) => ({ ...s, loading: true }));
    api(path)
      .then((data) => setState({ data, error: "", loading: false }))
      .catch((e) => setState({ data: null, error: e.message, loading: false }));
  }, [path]);
  useEffect(load, [load]);
  return { ...state, reload: load };
}
