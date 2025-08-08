import { useEffect, useState } from "react";
import { fetchJSON } from "./lib/api";

const TABS = [
  { key: "intro",     label: "Intro to Finances", path: "/api/intro" },
  { key: "market",    label: "Market Updates",    path: "/api/market" },
  { key: "portfolio", label: "Portfolio",         path: "/api/portfolio" },
  { key: "planning",  label: "Planning",          path: "/api/planning" },
];

export default function App() {
  const [active, setActive] = useState("intro");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const tab = TABS.find(t => t.key === active);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    fetchJSON(tab.path)
      .then(d => alive && setData(d))
      .catch(err => alive && setData({ error: err.message }))
      .finally(() => alive && setLoading(false));
    return () => { alive = false; };
  }, [active]);

  return (
    <div style={{ fontFamily: "system-ui, sans-serif", maxWidth: 900, margin: "32px auto", padding: "0 16px" }}>
      <header style={{ marginBottom: 16 }}>
        <h1 style={{ margin: 0 }}>ProfitPlug</h1>
        <p style={{ color: "#555", margin: "4px 0 0" }}>Your simple finance helper</p>
      </header>

      <nav style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        {TABS.map(t => (
          <button
            key={t.key}
            onClick={() => setActive(t.key)}
            style={{
              padding: "8px 12px",
              borderRadius: 8,
              border: "1px solid #ddd",
              background: active === t.key ? "#f0f0f0" : "white",
              cursor: "pointer"
            }}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main style={{ border: "1px solid #eee", borderRadius: 12, padding: 16, minHeight: 240 }}>
        {loading && <p>Loading…</p>}
        {!loading && data?.error && <p style={{ color: "crimson" }}>Error: {data.error}</p>}
        {!loading && !data?.error && <Content data={data} />}
      </main>
    </div>
  );
}

function Content({ data }) {
  if (!data) return null;

  if (data.sections) {
    return (
      <div>
        <h2>{data.title}</h2>
        {data.sections.map(sec => (
          <section key={sec.id} style={{ margin: "16px 0" }}>
            <h3 style={{ marginBottom: 8 }}>{sec.title}</h3>
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {(sec.items || []).map((it, i) => (
                <li key={i} style={{ marginBottom: 6 }}>
                  <strong>{it.headline || it.term}</strong>
                  {": "}
                  <span>{it.blurb}</span>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    );
  }

  if (data.updates) {
    return (
      <div>
        <h2>{data.title}</h2>
        <ul>
          {data.updates.map((u, i) => <li key={i}>{u}</li>)}
        </ul>
      </div>
    );
  }

  if (data.holdings) {
    const total = data.holdings.reduce((s, h) => s + h.shares * h.price, 0);
    return (
      <div>
        <h2>{data.title}</h2>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={th}>Symbol</th>
              <th style={th}>Shares</th>
              <th style={th}>Price</th>
              <th style={th}>Value</th>
            </tr>
          </thead>
          <tbody>
            {data.holdings.map((h, i) => (
              <tr key={i}>
                <td style={td}>{h.symbol}</td>
                <td style={td}>{h.shares}</td>
                <td style={td}>${h.price?.toFixed?.(2) ?? "—"}</td>
                <td style={td}>${(h.shares * (h.price ?? 0)).toFixed(2)}</td>
              </tr>
            ))}
            <tr>
              <td colSpan={3} style={{ ...td, fontWeight: "bold" }}>Total</td>
              <td style={{ ...td, fontWeight: "bold" }}>${total.toFixed(2)}</td>
            </tr>
          </tbody>
        </table>
      </div>
    );
  }

  if (data.steps) {
    return (
      <div>
        <h2>{data.title}</h2>
        <ol>
          {data.steps.map((s, i) => <li key={i} style={{ marginBottom: 6 }}>{s}</li>)}
        </ol>
      </div>
    );
  }

  return <pre>{JSON.stringify(data, null, 2)}</pre>;
}

const th = { textAlign: "left", borderBottom: "1px solid #eee", padding: "6px 4px" };
const td = { borderBottom: "1px solid #f5f5f5", padding: "6px 4px" };