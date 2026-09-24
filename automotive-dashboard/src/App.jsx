import { useEffect, useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { api } from "./api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const SENSOR_META = {
  engine_temperature: { label: "Engine Temperature", unit: "°C", color: "#ff6b6b" },
  oil_pressure: { label: "Oil Pressure", unit: "bar", color: "#6ea8fe" },
  engine_vibration: { label: "Engine Vibration", unit: "mm/s", color: "#c084fc" },
  battery_voltage: { label: "Battery Voltage", unit: "V", color: "#4ade80" },
  oil_temperature: { label: "Oil Temperature", unit: "°C", color: "#f59e0b" },
  coolant_temperature: { label: "Coolant Temperature", unit: "°C", color: "#22d3ee" },
  engine_rpm: { label: "Engine RPM", unit: "rpm", color: "#a78bfa" },
  vehicle_speed: { label: "Vehicle Speed", unit: "km/h", color: "#38bdf8" },
  fuel_consumption: { label: "Fuel Consumption", unit: "L/100km", color: "#fb7185" },
  brake_temperature: { label: "Brake Temperature", unit: "°C", color: "#f97316" }
};

function formatValue(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toFixed(2);
}

function normalizeLatest(row) {
  if (!row) return {};
  return {
    engine_temperature: row.engine_temperature ?? row.Engine_Temperature,
    oil_pressure: row.oil_pressure ?? row.Oil_Pressure,
    engine_vibration: row.engine_vibration ?? row.Engine_Vibration,
    battery_voltage: row.battery_voltage ?? row.Battery_Voltage,
    oil_temperature: row.oil_temperature ?? row.Oil_Temperature,
    coolant_temperature: row.coolant_temperature ?? row.Coolant_Temperature,
    engine_rpm: row.engine_rpm ?? row.Engine_RPM,
    vehicle_speed: row.vehicle_speed ?? row.Vehicle_Speed,
    fuel_consumption: row.fuel_consumption ?? row.Fuel_Consumption,
    brake_temperature: row.brake_temperature ?? row.Brake_Temperature
  };
}

function buildActions(prediction, latest) {
  const actions = [];
  if (prediction?.anomaly_status === "ANOMALY") {
    actions.push({
      title: "Investigate anomaly",
      text: "Review the latest telemetry against the vehicle's historical operating pattern."
    });
  }
  if (Number(latest.engine_vibration) > 3) {
    actions.push({
      title: "Inspect vibration sources",
      text: "Check engine mounts and rotating components for wear, looseness, or imbalance."
    });
  }
  if (Number(latest.oil_pressure) < 2.5) {
    actions.push({
      title: "Inspect lubrication system",
      text: "Check oil level, filter, pump, pressure sensor, and lubrication passages."
    });
  }
  if (Number(latest.engine_temperature) > 105) {
    actions.push({
      title: "Inspect cooling system",
      text: "Check coolant level, radiator, thermostat, and related cooling components."
    });
  }
  if (!actions.length) {
    actions.push({
      title: "Continue monitoring",
      text: "No rule-based maintenance action was triggered by the displayed telemetry."
    });
  }
  return actions;
}

function MetricCard({ label, value, unit, tone }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className={`metric-value ${tone || ""}`}>{value}</div>
      {unit && <div className="metric-unit">{unit}</div>}
    </div>
  );
}

function SensorCard({ name, value }) {
  const meta = SENSOR_META[name];
  if (!meta) return null;

  return (
    <div className="sensor-card">
      <div className="sensor-top">
        <span className="sensor-dot" style={{ background: meta.color }} />
        <span>{meta.label}</span>
      </div>
      <div className="sensor-value">{formatValue(value)}</div>
      <div className="sensor-unit">{meta.unit}</div>
    </div>
  );
}

function App() {
  const [vehicles, setVehicles] = useState([]);
  const [vehicleId, setVehicleId] = useState("");
  const [latest, setLatest] = useState(null);
  const [previous, setPrevious] = useState([]);
  const [health, setHealth] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [agent, setAgent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [training, setTraining] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const loadDashboard = async (id) => {
  if (!id) return;

  setLoading(true);
  setError("");

  try {
    const [latestData, previousData, healthData, predictionData] =
      await Promise.all([
        api.getLatest(id),
        api.getPrevious(id),
        api.getHealth(id),
        api.getPrediction(id)
      ]);

    setLatest(normalizeLatest(latestData));
    setPrevious(previousData || []);
    setHealth(healthData);
    setPrediction(predictionData);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};

  const generateAIAssessment = async () => {
        setAiLoading(true);
        setError("");

        try {
          const result = await api.getAgent(vehicleId);
          setAgent(result);
        } catch (err) {
          setError(err.message);
        } finally {
          setAiLoading(false);
        }
      };

  useEffect(() => {
    api.getVehicles()
      .then((data) => {
        const list = data.vehicles || [];
        setVehicles(list);
        if (list.length) setVehicleId(list[0]);
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
  if (vehicleId) {
    setAgent(null);
    loadDashboard(vehicleId);
  }
}, [vehicleId]);

  const chartData = useMemo(() => {
    return [...previous, latest || {}].map((row, index) => ({
      index: index + 1,
      temperature: Number(row.engine_temperature ?? row.Engine_Temperature ?? 0),
      vibration: Number(row.engine_vibration ?? row.Engine_Vibration ?? 0),
      oilPressure: Number(row.oil_pressure ?? row.Oil_Pressure ?? 0)
    }));
  }, [previous, latest]);

  const actions = useMemo(
    () => buildActions(prediction, latest || {}),
    [prediction, latest]
  );

  const runTraining = async () => {
    setTraining(true);
    setError("");
    try {
      await api.trainModels();
      await loadDashboard(vehicleId);
    } catch (err) {
      setError(err.message);
    } finally {
      setTraining(false);
    }
  };

  const uploadCsv = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError("");

    try {
      await api.uploadCsv(file);
      const data = await api.getVehicles();
      const list = data.vehicles || [];
      setVehicles(list);
      if (list.length && !list.includes(vehicleId)) setVehicleId(list[0]);
      else await loadDashboard(vehicleId);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };

  const anomaly = prediction?.anomaly_status === "ANOMALY";
  const healthStatus = health?.health_status || "—";
  const failureProbability = Number(prediction?.failure_probability ?? 0);
  const failurePercent = Math.round(failureProbability * 100);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">AS</div>
          <div>
            <div className="brand-title">Auto Sense</div>
            <div className="brand-subtitle">Predictive Maintenance Intelligence</div>
          </div>
        </div>

        <div className="header-actions">
          <label className="upload-button">
            {uploading ? "Uploading..." : "Upload Telemetry"}
            <input type="file" accept=".csv" onChange={uploadCsv} disabled={uploading} />
          </label>

          <button className="train-button" onClick={runTraining} disabled={training}>
            {training ? "Training..." : "Train Models"}
          </button>

          <div className="status-pill">
            <span className="status-dot" />
            API Online
          </div>
        </div>
      </header>

      <main className="dashboard">
        <section className="hero">
          <div>
            <div className="eyebrow">VEHICLE INTELLIGENCE</div>
            <h1>Predictive Maintenance Dashboard</h1>
            <p>
              Monitor telemetry, detect abnormal behavior, and review AI-assisted
              maintenance guidance .
            </p>
          </div>

          <div className="vehicle-selector">
            <label>Active vehicle</label>
            <select value={vehicleId} onChange={(e) => setVehicleId(e.target.value)}>
              {vehicles.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>
        </section>

        {error && (
          <div className="error-banner">
            <strong>Backend error:</strong> {error}
          </div>
        )}

        {loading ? (
          <div className="loading-panel">
            <div className="spinner" />
            Loading vehicle intelligence...
          </div>
        ) : (
          <>
            <section className="summary-grid">
              <MetricCard
                label="Vehicle"
                value={vehicleId || "—"}
              />
              <MetricCard
                label="Health Status"
                value={healthStatus}
                tone={
                  healthStatus === "CRITICAL"
                    ? "danger"
                    : healthStatus === "DEGRADED"
                    ? "warning"
                    : "success"
                }
              />
              <MetricCard
                label="Risk Points"
                value={health?.risk_points ?? "—"}
              />
              <MetricCard
                label="Failure Probability"
                value={`${failurePercent}%`}
                tone={failurePercent > 50 ? "danger" : "success"}
              />
            </section>

            <section className="main-grid">
              <div className="panel prediction-panel">
                <div className="panel-header">
                  <div>
                    <div className="panel-kicker">MODEL SIGNAL</div>
                    <h2>Vehicle condition</h2>
                  </div>
                  <div className={`anomaly-badge ${anomaly ? "anomaly" : "normal"}`}>
                    <span />
                    {prediction?.anomaly_status || "—"}
                  </div>
                </div>

                <div className="condition-visual">
                  <div className={`radar-ring ${anomaly ? "ring-alert" : ""}`}>
                    <div className="radar-core">
                      <strong>{failurePercent}%</strong>
                      <span>failure risk</span>
                    </div>
                  </div>

                  <div className="condition-copy">
                    <h3>
                      {anomaly
                        ? "Unusual telemetry detected"
                        : "Telemetry within learned pattern"}
                    </h3>
                    <p>
                      The anomaly detector compares the current feature pattern
                      with the behavior learned from your telemetry dataset.
                    </p>
                    <div className="mini-stats">
                      <div>
                        <span>Model status</span>
                        <strong>Active</strong>
                      </div>
                      <div>
                        <span>Vehicle</span>
                        <strong>{vehicleId || "—"}</strong>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="panel latest-panel">
                <div className="panel-header">
                  <div>
                    <div className="panel-kicker">LATEST TELEMETRY</div>
                    <h2>Sensor snapshot</h2>
                  </div>
                  <span className="live-badge">LATEST</span>
                </div>

                <div className="sensor-grid">
                  {[
                    "engine_temperature",
                    "oil_pressure",
                    "engine_vibration",
                    "battery_voltage",
                    "oil_temperature",
                    "coolant_temperature",
                    "engine_rpm",
                    "vehicle_speed",
                    "fuel_consumption",
                    "brake_temperature"
                  ].map((name) => (
                    <SensorCard key={name} name={name} value={latest?.[name]} />
                  ))}
                </div>
              </div>
            </section>

            <section className="panel chart-panel">
              <div className="panel-header">
                <div>
                  <div className="panel-kicker">RECENT BEHAVIOR</div>
                  <h2>Telemetry trend</h2>
                </div>
                <div className="chart-legend">
                  <span><i className="legend-temp" /> Temperature</span>
                  <span><i className="legend-vib" /> Vibration</span>
                  <span><i className="legend-oil" /> Oil pressure</span>
                </div>
              </div>

              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="tempFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#ff6b6b" stopOpacity={0.28} />
                        <stop offset="100%" stopColor="#ff6b6b" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="vibFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#c084fc" stopOpacity={0.2} />
                        <stop offset="100%" stopColor="#c084fc" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#203047" />
                    <XAxis dataKey="index" stroke="#71809a" />
                    <YAxis stroke="#71809a" />
                    <Tooltip
                      contentStyle={{
                        background: "#101b2d",
                        border: "1px solid #273955",
                        borderRadius: 12,
                        color: "#eef4ff"
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="temperature"
                      stroke="#ff6b6b"
                      fill="url(#tempFill)"
                      strokeWidth={2}
                      name="Temperature"
                    />
                    <Area
                      type="monotone"
                      dataKey="vibration"
                      stroke="#c084fc"
                      fill="url(#vibFill)"
                      strokeWidth={2}
                      name="Vibration"
                    />
                    <Area
                      type="monotone"
                      dataKey="oilPressure"
                      stroke="#6ea8fe"
                      fill="none"
                      strokeWidth={2}
                      name="Oil pressure"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </section>

            <section className="bottom-grid">
              <div className="panel actions-panel">
                <div className="panel-header">
                  <div>
                    <div className="panel-kicker">MAINTENANCE GUIDANCE</div>
                    <h2>Recommended actions</h2>
                  </div>
                  <span className="action-count">{actions.length} items</span>
                </div>

                <div className="actions-list">
                  {actions.map((action, index) => (
                    <div className="action-item" key={action.title}>
                      <div className="action-number">{String(index + 1).padStart(2, "0")}</div>
                      <div>
                        <h3>{action.title}</h3>
                        <p>{action.text}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="panel ai-panel">
                <div className="panel-header">
                  <div>
                    <div className="panel-kicker"><h2>Auto Sense AI</h2></div>
                    
                  </div>
                  <div className="ai-orb">✦</div>
                </div>

                <div className="ai-response">
                  {agent?.explanation ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {agent.explanation}
                    </ReactMarkdown>
                  ) : (
                    <>
                      <p>No AI explanation generated yet.</p>

                      <button
                        className="ai-generate-button"
                        onClick={generateAIAssessment}
                        disabled={aiLoading}
                      >
                        {aiLoading ? "Generating..." : "Generate AI Assessment"}
                      </button>
                    </>
                  )}
                </div>
              </div>
            </section>
          </>
        )}
      </main>

      <footer className="footer">
        <span>AutoSense AI</span>
        <span>© Vinod Sagar</span>
      </footer>
    </div>
  );
}

export default App;