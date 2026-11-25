import React, { useEffect, useState } from "react";
import { apiFetch } from "../api";

export default function CustomerDashboard({ onSelectTicket }) {
  const [orders, setOrders] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [refunds, setRefunds] = useState([]);
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("electronics");
  const [orderId, setOrderId] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadData() {
    setLoading(true);
    const [o, t, r] = await Promise.all([apiFetch("/api/orders"), apiFetch("/api/tickets"), apiFetch("/api/refunds")]);
    setOrders(o);
    setTickets(t);
    setRefunds(r);
    setLoading(false);
  }

  useEffect(() => { loadData(); }, []);

  async function handleCreateTicket(e) {
    e.preventDefault();
    const created = await apiFetch("/api/tickets", {
      method: "POST",
      body: JSON.stringify({ subject, description, category, order_id: orderId || null }),
    });
    setSubject("");
    setDescription("");
    onSelectTicket(created.id);
  }

  if (loading) return <p style={{ padding: 24 }}>Loading dashboard...</p>;

  return (
    <div style={{ maxWidth: 960, margin: "24px auto", padding: "0 16px", display: "grid", gap: 24 }}>
      <section style={{ background: "#fff", padding: 20, borderRadius: 8 }}>
        <h3>Your Orders</h3>
        <table width="100%" border="1" cellPadding="8" style={{ borderCollapse: "collapse", borderColor: "#e2e8f0" }}>
          <thead><tr><th>Order ID</th><th>Item</th><th>Category</th><th>Amount</th><th>Status</th></tr></thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}><td>{o.id}</td><td>{o.item_name}</td><td>{o.category}</td><td>₹{o.total_amount}</td><td>{o.status}</td></tr>
            ))}
          </tbody>
        </table>
      </section>

      <section style={{ background: "#fff", padding: 20, borderRadius: 8 }}>
        <h3>Raise a Support Ticket / Chat with AI Agent</h3>
        <form onSubmit={handleCreateTicket} style={{ display: "grid", gap: 10 }}>
          <input placeholder="Subject" value={subject} onChange={(e) => setSubject(e.target.value)} required style={{ padding: 8 }} />
          <select value={orderId} onChange={(e) => setOrderId(e.target.value)} style={{ padding: 8 }}>
            <option value="">-- Optional: Select Order --</option>
            {orders.map((o) => <option key={o.id} value={o.id}>{o.id} - {o.item_name} (₹{o.total_amount})</option>)}
          </select>
          <select value={category} onChange={(e) => setCategory(e.target.value)} style={{ padding: 8 }}>
            <option value="electronics">Electronics</option>
            <option value="fashion">Fashion</option>
            <option value="home">Home</option>
          </select>
          <textarea placeholder="Describe your issue (e.g., I want a refund for ORD-1001)" value={description} onChange={(e) => setDescription(e.target.value)} required rows={3} style={{ padding: 8 }} />
          <button type="submit" style={{ padding: 10, background: "#2563eb", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
            Submit & Start AI Chat
          </button>
        </form>
      </section>

      <section style={{ background: "#fff", padding: 20, borderRadius: 8 }}>
        <h3>Your Support Tickets & Refunds</h3>
        {tickets.length === 0 ? <p>No tickets yet.</p> : tickets.map((t) => (
          <div key={t.id} style={{ display: "flex", justifyContent: "space-between", padding: "10px 0", borderBottom: "1px solid #eee" }}>
            <div><strong>#{t.id} {t.subject}</strong> ({t.order_id || "No Order"}) — Status: <b>{t.status}</b></div>
            <button onClick={() => onSelectTicket(t.id)}>Open Chat</button>
          </div>
        ))}
        <h4 style={{ marginTop: 16 }}>Refund Status</h4>
        {refunds.length === 0 ? <p>No refund requests.</p> : refunds.map((r) => (
          <div key={r.id}>Refund #{r.id} for {r.order_id} — ₹{r.amount} — Status: <b>{r.status}</b></div>
        ))}
      </section>
    </div>
  );
}