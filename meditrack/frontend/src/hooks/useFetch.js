import { useState, useEffect, useCallback } from "react";
import api, { err } from "../services/api";
export default function useFetch(url) {
  const [data, setData] = useState(null), [loading, setL] = useState(true), [error, setE] = useState("");
  const load = useCallback(() => { setL(true); api.get(url).then(r => { setData(r.data); setE(""); }).catch(e => setE(err(e))).finally(() => setL(false)); }, [url]);
  useEffect(() => { load(); }, [load]);
  return { data, loading, error, reload: load };
}
