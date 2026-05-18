
import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  MailWarning,
  Moon,
  Network,
  Search,
  Settings,
  ShieldCheck,
  Sun,
  Target,
  Users,
  BarChart3,
  FileText,
  Bell,
  Maximize2,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { motion } from "framer-motion";

const API = "http://127.0.0.1:8000";

const trendData = [
  { time: "00:00", alerts: 6 },
  { time: "04:00", alerts: 28 },
  { time: "08:00", alerts: 50 },
  { time: "12:00", alerts: 82 },
  { time: "16:00", alerts: 45 },
  { time: "20:00", alerts: 58 },
  { time: "24:00", alerts: 77 },
];

const pieData = [
  { name: "Critical", value: 12 },
  { name: "High", value: 19 },
  { name: "Medium", value: 48 },
  { name: "Low", value: 80 },
];

const COLORS = ["#ff4d67", "#ff9f1c", "#22c55e", "#7565ff"];

function StatCard({ icon: Icon, title, value, subtitle, tone }) {
  return (
    <motion.div
      whileHover={{ y: -6, scale: 1.01 }}
      className={`stat-card ${tone}`}
    >
      <div className="stat-top">
        <div className="icon-bubble">
          <Icon size={24} />
        </div>
        <span>{subtitle}</span>
      </div>
      <h3>{title}</h3>
      <div className="stat-value">{value}</div>
    </motion.div>
  );
}

function Sidebar({ active, setActive }) {
  const items = [
    ["Overview", Activity],
    ["Alerts", ShieldCheck],
    ["Users", Users],
    ["Graph Intelligence", Network],
    ["Phishing AI", MailWarning],
    ["Reports", FileText],
    ["Settings", Settings],
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-logo">
          <BrainCircuit size={34} />
        </div>
        <div>
          <h2>NeuroTrace AI</h2>
          <p>AI Investigation Platform</p>
        </div>
      </div>

      <nav>
        {items.map(([label, Icon]) => (
          <button
            key={label}
            className={active === label ? "nav-item active" : "nav-item"}
            onClick={() => setActive(label)}
          >
            <Icon size={19} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="admin-card">
        <div className="avatar">A</div>
        <div>
          <h4>Admin</h4>
          <p>Administrator</p>
        </div>
      </div>
    </aside>
  );
}

function Topbar({ theme, setTheme }) {
  return (
    <div className="topbar">
      <div className="search-box">
        <Search size={18} />
        <input placeholder="Search anything..." />
        <kbd>Ctrl + K</kbd>
      </div>

      <button className="icon-btn" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
        {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        <span>{theme === "dark" ? "Light Mode" : "Dark Mode"}</span>
      </button>

      <button className="circle-btn">
        <Bell size={18} />
        <small>12</small>
      </button>

      <button className="circle-btn">
        <Maximize2 size={18} />
      </button>
    </div>
  );
}

function RecentAlerts({ alerts }) {
  const fallback = [
    { user: "user_005", risk_level: "CRITICAL", investigation_explanation: "Brute force attack detected" },
    { user: "LAP0338", risk_level: "HIGH", investigation_explanation: "Unusual night communication detected" },
    { user: "MOH0273", risk_level: "MEDIUM", investigation_explanation: "Phishing-like email activity" },
    { user: "PC-5758", risk_level: "LOW", investigation_explanation: "Multiple weak signals detected" },
  ];

  const rows = alerts?.length ? alerts.slice(0, 5) : fallback;

  return (
    <div className="panel recent">
      <div className="panel-head">
        <h3>Recent Alerts</h3>
        <button>View All</button>
      </div>

      {rows.map((a, idx) => (
        <div className="alert-row" key={idx}>
          <div className={`alert-icon ${String(a.risk_level || "low").toLowerCase()}`}>
            <AlertTriangle size={18} />
          </div>
          <div className="alert-info">
            <strong>{a.investigation_explanation || "Suspicious behavior detected"}</strong>
            <span>{a.user || "unknown"} • {idx + 2} min ago</span>
          </div>
          <span className={`badge ${String(a.risk_level || "low").toLowerCase()}`}>
            {a.risk_level || "LOW"}
          </span>
        </div>
      ))}
    </div>
  );
}

function Overview({ kpis, alerts }) {
  return (
    <>
      <section className="hero">
        <div>
          <span className="eyebrow">✣ Autonomous Behavioral Intelligence</span>
          <h1>NeuroTrace AI Command Center</h1>
          <p>
            Analyse comportementale, détection phishing, graph intelligence et investigation automatique des menaces.
          </p>
        </div>
        <div className="api-pill">
          <ShieldCheck size={20} />
          API Connected
        </div>
      </section>

      <div className="stat-grid">
        <StatCard icon={Users} title="Total Users" value={kpis.total_users ?? 0} subtitle="Enterprise scope" tone="blue" />
        <StatCard icon={AlertTriangle} title="Critical Alerts" value={kpis.critical_users ?? 0} subtitle="Immediate review" tone="red" />
        <StatCard icon={ShieldCheck} title="High Risk" value={kpis.high_risk_users ?? 0} subtitle="SOC priority" tone="orange" />
        <StatCard icon={Target} title="Total Alerts" value={kpis.total_alerts ?? 0} subtitle="Investigation queue" tone="green" />
      </div>

      <div className="grid-two">
        <div className="panel">
          <div className="panel-head">
            <h3>Alerts Over Time</h3>
            <button>Last 24 Hours</button>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={trendData}>
              <defs>
                <linearGradient id="alertGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#7c3aed" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="chart-grid" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="alerts" stroke="#8b5cf6" fill="url(#alertGradient)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <RecentAlerts alerts={alerts} />
      </div>

      <div className="grid-two bottom">
        <div className="panel">
          <h3>Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={pieData} dataKey="value" innerRadius={55} outerRadius={85}>
                {pieData.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="panel">
          <h3>Top Attack Types</h3>
          <div className="attack-row"><span>Brute Force</span><div><i style={{ width: "78%" }} /></div><b>42</b></div>
          <div className="attack-row"><span>Phishing</span><div><i style={{ width: "62%" }} /></div><b>28</b></div>
          <div className="attack-row"><span>Insider Threat</span><div><i style={{ width: "45%" }} /></div><b>19</b></div>
          <div className="attack-row"><span>Data Exfiltration</span><div><i style={{ width: "34%" }} /></div><b>12</b></div>
        </div>
      </div>
    </>
  );
}

function UsersPage({ users }) {
  return (
    <div className="panel page-panel">
      <h2>Suspicious Users</h2>
      <table>
        <thead>
          <tr>
            <th>User</th>
            <th>Risk Level</th>
            <th>Score</th>
            <th>Anomaly</th>
            <th>Explanation</th>
          </tr>
        </thead>
        <tbody>
          {users.slice(0, 15).map((u, i) => (
            <tr key={i}>
              <td>{u.user}</td>
              <td><span className={`badge ${String(u.risk_level || "low").toLowerCase()}`}>{u.risk_level}</span></td>
              <td>{Number(u.final_intelligence_score || 0).toFixed(2)}</td>
              <td>{u.anomaly_status}</td>
              <td>{u.investigation_explanation}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PhishingPage() {
  const [text, setText] = useState("Urgent! Verify your password now by clicking this link.");
  const [result, setResult] = useState(null);

  async function predict() {
    try {
      const res = await axios.post(`${API}/predict-phishing`, { text });
      setResult(res.data);
    } catch {
      setResult({ prediction: "API ERROR", text });
    }
  }

  return (
    <div className="panel page-panel">
      <h2>Phishing AI Detector</h2>
      <p className="muted">Analyse un message et détecte s'il est suspect ou safe.</p>
      <textarea value={text} onChange={(e) => setText(e.target.value)} />
      <button className="primary-btn" onClick={predict}>Analyse Message</button>
      {result && (
        <div className={`result-box ${result.prediction === "PHISHING" ? "danger" : "safe"}`}>
          <h3>{result.prediction}</h3>
          <p>{result.text}</p>
        </div>
      )}
    </div>
  );
}

function Placeholder({ title }) {
  return (
    <div className="panel page-panel">
      <h2>{title}</h2>
      <p className="muted">Module prêt pour extension frontend.</p>
    </div>
  );
}

export default function App() {
  const [theme, setTheme] = useState("dark");
  const [active, setActive] = useState("Overview");
  const [kpis, setKpis] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [users, setUsers] = useState([]);
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    async function loadData() {
      try {
        const [k, a, u] = await Promise.all([
          axios.get(`${API}/kpis`),
          axios.get(`${API}/alerts?limit=20`),
          axios.get(`${API}/users?limit=30`),
        ]);

        setKpis(k.data || {});
        setAlerts(Array.isArray(a.data) ? a.data : []);
        setUsers(Array.isArray(u.data) ? u.data : []);
        setApiStatus("connected");
      } catch (e) {
        setApiStatus("offline");
      }
    }

    loadData();
  }, []);

  const content = useMemo(() => {
    if (active === "Overview") return <Overview kpis={kpis} alerts={alerts} />;
    if (active === "Alerts") return <RecentAlerts alerts={alerts} />;
    if (active === "Users") return <UsersPage users={users} />;
    if (active === "Graph Intelligence") return <Placeholder title="Graph Intelligence" />;
    if (active === "Phishing AI") return <PhishingPage />;
    return <Placeholder title={active} />;
  }, [active, kpis, alerts, users]);

  return (
    <div className="app-shell">
      <Sidebar active={active} setActive={setActive} />
      <main className="main">
        <Topbar theme={theme} setTheme={setTheme} />
        {apiStatus === "offline" && (
          <div className="api-warning">
            Backend API not reachable. Start FastAPI with: uvicorn main:app --reload
          </div>
        )}
        {content}
      </main>
    </div>
  );
}
