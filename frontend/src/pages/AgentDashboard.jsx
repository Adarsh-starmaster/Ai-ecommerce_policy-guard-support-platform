import React, { useEffect, useState } from "react";
import { apiFetch } from "../api";

export default function AgentDashboard({ onSelectTicket }) {
  const [tickets, setTickets] = useState([]);
  const [refunds, setRefunds] = useState([]);
  const [filter, setFilter] = useState("");
  const [note, setNote] = useState("");

  async function load() {
    const query = filter ? `?status=${filter}` : "";
    const [t, r] = await Promise.all([apiFetch(`/api/tickets${query}`), apiFetch("/api/refunds")]);
    setTickets(t);
    setRefunds(r);
  }

  useEffect(() => { load(); }, [filter]);

  async function handleRefundDecision(refundId, decision) {
    await apiFetch(`/api/refunds/${refundId}/review`, {
      method: "POST",
      body: JSON.stringify({ decision, internal_note: note }),
    });
    setNote("");
    load();
  }

  return (
    <div style={{ maxWidth: 1000, margin: "24px auto", padding: "0 16px", display: "grid", gap: 24 }}>
      <section style={{ background: "#fff", padding: 20, borderRadius: 8 }}>
        <h3>Escalated & Pending Refund Reviews (&gt; ₹5,000)</h3>
        <input placeholder="Internal review note..." value={note} onChange={(e) => setNote(e.target.value)} style={{ width: "100%", padding: 8, marginBottom: 12 }} />
        {refunds.filter((r) => r.status === "pending").map((r) => (
          <div key={r.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: 10, border: "1px solid #e2e8f0", marginBottom: 8 }}>
            <div><strong>Refund #{r.id}</strong> — Order {r.order_id} — Amount: <b>₹{r.amount}</b> (Ticket #{r.ticket_id})</div>
            <div style={{ display: "flex", gap: 8 }}>
              <button onClick={() => handleRefundDecision(r.id, "approved")} style={{ background: "#16a34a", color: "#fff", border: "none", padding: "6px 12px", borderRadius: 4 }}>Approve</button>
              <button onClick={() => handleRefundDecision(r.id, "rejected")} style={{ background: "#dc2626", color: "#fff", border: "none", padding: "6px 12px", borderRadius: 4 }}>Reject</button>
            </div>
          </div>
        ))}
      </section>

      <section style={{ background: "#fff", padding: 20, borderRadius: 8 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3>All Support Tickets</h3>
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="escalated">Escalated</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
        {tickets.map((t) => (
          <div key={t.id} style={{ display: "flex", justifyContent: "space-between", padding: "10px 0", borderBottom: "1px solid #eee" }}>
            <div><strong>#{t.id} {t.subject}</strong> | Order: {t.order_id || "N/A"} | Priority: <b>{t.priority}</b> | Status: <b>{t.status}</b></div>
            <button onClick={() => onSelectTicket(t.id)}>Inspect Conversation</button>
          </div>
        ))}
      </section>
    </div>
  );
}