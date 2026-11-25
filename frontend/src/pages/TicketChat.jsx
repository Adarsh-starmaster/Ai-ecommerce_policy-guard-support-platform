import React, { useEffect, useState } from "react";
import { apiFetch } from "../api";

export default function TicketChat({ ticketId, onBack }) {
  const [detail, setDetail] = useState(null);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  async function load() {
    const data = await apiFetch(`/api/tickets/${ticketId}`);
    setDetail(data);
  }

  useEffect(() => { load(); }, [ticketId]);

  async function sendMessage(e) {
    e.preventDefault();
    if (!input.trim()) return;
    setSending(true);
    await apiFetch(`/api/tickets/${ticketId}/messages`, { method: "POST", body: JSON.stringify({ content: input }) });
    setInput("");
    await load();
    setSending(false);
  }

  if (!detail) return <p style={{ padding: 24 }}>Loading conversation...</p>;

  return (
    <div style={{ maxWidth: 800, margin: "24px auto", background: "#fff", padding: 20, borderRadius: 8 }}>
      <button onClick={onBack}>← Back to Dashboard</button>
      <h3>Ticket #{detail.ticket.id}: {detail.ticket.subject}</h3>
      <p>Status: <b>{detail.ticket.status}</b> | Priority: <b>{detail.ticket.priority}</b> | Order: <b>{detail.ticket.order_id || "None"}</b></p>

      <div style={{ border: "1px solid #e2e8f0", borderRadius: 6, padding: 12, minHeight: 260, maxHeight: 400, overflowY: "auto", display: "flex", flexDirection: "column", gap: 10 }}>
        {detail.messages.map((m) => (
          <div key={m.id} style={{
            alignSelf: m.sender_type === "customer" ? "flex-end" : "flex-start",
            background: m.sender_type === "customer" ? "#dbeafe" : "#f1f5f9",
            padding: 10, borderRadius: 6, maxWidth: "75%"
          }}>
            <small style={{ fontWeight: "bold" }}>{m.sender_type.toUpperCase()}</small>
            <div>{m.content}</div>
          </div>
        ))}
      </div>

      <form onSubmit={sendMessage} style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type your message..." style={{ flex: 1, padding: 8 }} />
        <button type="submit" disabled={sending} style={{ padding: "8px 16px", background: "#2563eb", color: "#fff", border: "none", borderRadius: 4 }}>
          {sending ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
}