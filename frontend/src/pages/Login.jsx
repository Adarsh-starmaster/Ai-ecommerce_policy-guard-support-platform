import React, { useState } from "react";
import { apiFetch } from "../api";

export default function Login({ onAuth }) {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("alice@example.com");
  const [password, setPassword] = useState("Password123!");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      const endpoint = isRegister ? "/api/auth/register" : "/api/auth/login";
      const body = isRegister ? { name, email, password, role: "customer" } : { email, password };
      const data = await apiFetch(endpoint, { method: "POST", body: JSON.stringify(body) });
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      onAuth(data.user);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: "80px auto", background: "#fff", padding: 24, borderRadius: 8, boxShadow: "0 2px 8px rgba(0,0,0,0.08)" }}>
      <h2>{isRegister ? "Create Account" : "Support Portal Sign In"}</h2>
      {error && <p style={{ color: "#dc2626" }}>{error}</p>}
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {isRegister && <input placeholder="Full Name" value={name} onChange={(e) => setName(e.target.value)} required style={{ padding: 8 }} />}
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required style={{ padding: 8 }} />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required style={{ padding: 8 }} />
        <button type="submit" style={{ padding: 10, background: "#2563eb", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
          {isRegister ? "Register" : "Sign In"}
        </button>
      </form>
      <p style={{ fontSize: 13, marginTop: 12 }}>
        Demo Customer: <code>alice@example.com</code> / <code>Password123!</code><br />
        Demo Agent: <code>agent@example.com</code> / <code>Agent123!</code>
      </p>
      <button onClick={() => setIsRegister(!isRegister)} style={{ background: "none", border: "none", color: "#2563eb", cursor: "pointer", padding: 0 }}>
        {isRegister ? "Already have an account? Sign in" : "Need an account? Register"}
      </button>
    </div>
  );
}