import React, { useState } from "react";
import Login from "./pages/Login";
import CustomerDashboard from "./pages/CustomerDashboard";
import AgentDashboard from "./pages/AgentDashboard";
import TicketChat from "./pages/TicketChat";

export default function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  });
  const [selectedTicketId, setSelectedTicketId] = useState(null);

  function logout() {
    localStorage.clear();
    setUser(null);
    setSelectedTicketId(null);
  }

  if (!user) return <Login onAuth={setUser} />;

  return (
    <div>
      <header style={{ background: "#1e293b", color: "#fff", padding: "12px 24px", display: "flex", justifyContent: "space-between" }}>
        <strong>E-Commerce AI Support ({user.role.toUpperCase()})</strong>
        <div>
          <span style={{ marginRight: 16 }}>{user.name}</span>
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      {selectedTicketId ? (
        <TicketChat ticketId={selectedTicketId} onBack={() => setSelectedTicketId(null)} />
      ) : user.role === "agent" ? (
        <AgentDashboard onSelectTicket={setSelectedTicketId} />
      ) : (
        <CustomerDashboard onSelectTicket={setSelectedTicketId} />
      )}
    </div>
  );
}