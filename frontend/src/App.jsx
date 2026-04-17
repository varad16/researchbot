import React, { useState } from "react";

const API = "http://localhost:8000";

export default function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");

  async function submit() {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      const r = await fetch(`${API}/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, session_id: sessionId }),
      });
      if (!r.ok) throw new Error(await r.text());
      const data = await r.json();
      setResult(data);
      setSessionId(data.session_id);
      setHistory((h) => [...h, { query, summary: data.summary }]);
      setQuery("");
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <h1 style={{ margin: 0 }}>ResearchBot</h1>
        <p style={{ margin: 0, color: "#666" }}>
          Multi-source research agent with tool-use and citations
        </p>
      </header>

      <div style={styles.inputRow}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="Ask a research question..."
          style={styles.input}
        />
        <button onClick={submit} disabled={loading} style={styles.button}>
          {loading ? "Researching..." : "Research"}
        </button>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      {result && (
        <div style={styles.card}>
          <h3>Summary</h3>
          <pre style={styles.summary}>{result.summary}</pre>
          <h4>Citations</h4>
          <ol>
            {result.citations.map((c) => (
              <li key={c.id}>
                <a href={c.url} target="_blank" rel="noreferrer">
                  {c.title || c.url}
                </a>{" "}
                <span style={{ color: "#888" }}>({c.source})</span>
              </li>
            ))}
          </ol>
          <div style={{ color: "#666", fontSize: 13 }}>
            Iterations: {result.iterations} · Session: {result.session_id}
          </div>
        </div>
      )}

      {history.length > 1 && (
        <div style={styles.card}>
          <h3>Session history</h3>
          <ul>
            {history.map((h, i) => (
              <li key={i}>
                <strong>Q:</strong> {h.query}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

const styles = {
  app: {
    fontFamily: "system-ui, sans-serif",
    maxWidth: 820,
    margin: "40px auto",
    padding: "0 20px",
  },
  header: { marginBottom: 24 },
  inputRow: { display: "flex", gap: 8, marginBottom: 20 },
  input: {
    flex: 1,
    padding: "10px 14px",
    fontSize: 16,
    border: "1px solid #ccc",
    borderRadius: 6,
  },
  button: {
    padding: "10px 20px",
    fontSize: 16,
    background: "#2563eb",
    color: "white",
    border: "none",
    borderRadius: 6,
    cursor: "pointer",
  },
  card: {
    border: "1px solid #e5e5e5",
    borderRadius: 8,
    padding: 20,
    marginBottom: 20,
    background: "#fafafa",
  },
  summary: {
    whiteSpace: "pre-wrap",
    fontFamily: "inherit",
    fontSize: 15,
    lineHeight: 1.5,
  },
  error: {
    background: "#fee",
    color: "#900",
    padding: 12,
    borderRadius: 6,
    marginBottom: 16,
  },
};
