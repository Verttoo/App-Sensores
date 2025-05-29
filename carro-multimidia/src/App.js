
import React, { useState, useEffect } from 'react';
import './App.css';
import Speedometer from './Speedometer';

const SensorDisplay = ({ label, value, unit, alert }) => (
  <div className={`sensor ${alert ? 'alert' : ''}`}>
    <span className="sensor-label">{label}:</span>
    <span className="sensor-value">{value !== undefined && value !== null && !isNaN(value) ? Number(value).toFixed(1) : 'N/A'} {unit}</span>
  </div>
);

const AlertDisplay = ({ message, active }) => (
  active ? <div className="alert-message active">{message}</div> : null
);

function App() {
  const [carData, setCarData] = useState({});
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);

  const [speedLimitInput, setSpeedLimitInput] = useState('');
  const [customSpeedLimit, setCustomSpeedLimit] = useState(null);
  const [showCustomSpeedAlert, setShowCustomSpeedAlert] = useState(false); 

  useEffect(() => {
    const wsUrl = 'ws://localhost:8765';
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => { setIsConnected(true); setError(null); console.log('Conectado ao WebSocket'); };
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setCarData(data);
      } catch (e) { setError('Erro ao processar dados.'); console.error('Erro:', e); }
    };
    ws.onerror = (err) => { setIsConnected(false); setError('Falha na conexão WebSocket.'); console.error('Erro WebSocket:', err); };
    ws.onclose = () => { setIsConnected(false); console.log('Desconectado do WebSocket'); };
    return () => { if (ws.readyState === 1) ws.close(); };
  }, []);

  const handleSpeedLimitInputChange = (event) => setSpeedLimitInput(event.target.value);
  const handleSetCustomSpeedLimit = () => {
    const newLimit = parseFloat(speedLimitInput);
    if (!isNaN(newLimit) && newLimit > 0) {
      setCustomSpeedLimit(newLimit);
      setSpeedLimitInput('');
    } else {
      alert("Insira um limite válido.");
      setCustomSpeedLimit(null);
    }
  };

  useEffect(() => {
    const currentSpeed = parseFloat(carData.velocidade_kmh); 

    if (customSpeedLimit !== null && !isNaN(currentSpeed)) {
      setShowCustomSpeedAlert(currentSpeed > customSpeedLimit);
    } else {
      setShowCustomSpeedAlert(false);
    }
  }, [carData.velocidade_kmh, customSpeedLimit]); 


  return (
    <div className="car-multimedia-app">
      <header>
        <h1>Central Multimídia</h1>
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? 'Conectado' : 'Desconectado'}
        </div>
        {error && <div className="error-message">{error}</div>}
      </header>

      <main className="dashboard">
        <section className="speed-limit-control">
          <h2>Definir Limite de Velocidade</h2>
          <div className="input-group">
            <input type="number" value={speedLimitInput} onChange={handleSpeedLimitInputChange} placeholder="Ex: 80" min="0"/>
            <button onClick={handleSetCustomSpeedLimit}>Definir</button>
          </div>
          {customSpeedLimit !== null && (<p className="current-limit-text">Limite personalizado: {customSpeedLimit} km/h</p>)}
        </section>

        <section className="primary-info">
          <Speedometer speed={carData.velocidade_kmh} />
          <SensorDisplay label="Distância Traseira" value={carData.distancia_cm} unit="cm" alert={carData.alerta_distancia} />
        </section>

        <section className="engine-status">
          <h2>Motor & Fluidos</h2>
          <SensorDisplay label="Nível Combustível" value={carData.combustivel_percent} unit="%" alert={carData.alerta_combustivel} />
          <SensorDisplay label="Nível Óleo Motor" value={carData.oleo_motor_percent} unit="%" alert={carData.alerta_oleo_motor} />
          <SensorDisplay label="Fluido Freio" value={carData.fluido_freio_PSI} unit="PSI" alert={carData.alerta_fluido_freio} />
        </section>

        <section className="alerts-panel">
          <h2>Alertas</h2>
          <AlertDisplay 
            message={`⚠️ ALERTA (PERSONALIZADO): Velocidade (${Number(carData.velocidade_kmh || 0).toFixed(0)} km/h) acima do limite de ${customSpeedLimit} km/h!`} 
            active={showCustomSpeedAlert} 
          />

          <AlertDisplay message="⚠️ ALERTA: Objeto próximo!" active={carData.alerta_distancia} />
          <AlertDisplay message="⛽ ALERTA: Combustível baixo!" active={carData.alerta_combustivel} />
          <AlertDisplay message="🛑 ALERTA: Pressão do fluido de freio baixo!" active={carData.alerta_fluido_freio} />
          <AlertDisplay message="💧 ALERTA: Nível do óleo do motor baixo!" active={carData.alerta_oleo_motor} />
        </section>

        {/*<section className="raw-data">
          <h2>Dados Crus (Debug)</h2>
          <pre>{JSON.stringify(carData, null, 2)}</pre>
        </section>*/}
      </main>

      <footer>
        <p>Simulação Wokwi & React</p>
      </footer>
    </div>
  );
}

export default App;