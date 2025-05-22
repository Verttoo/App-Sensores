// src/App.js
import React, { useState, useEffect } from 'react';
import './App.css'; // Vamos criar este arquivo para estilização

// Componentes de UI (exemplos, podem ser divididos em arquivos separados)
const SensorDisplay = ({ label, value, unit, alert }) => (
  <div className={`sensor ${alert ? 'alert' : ''}`}>
    <span className="sensor-label">{label}:</span>
    <span className="sensor-value">{value !== undefined && value !== null ? value.toFixed(1) : 'N/A'} {unit}</span>
  </div>
);

const AlertDisplay = ({ message, active }) => (
  active ? <div className="alert-message active">{message}</div> : null
);

function App() {
  const [carData, setCarData] = useState({});
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // O endereço do seu servidor WebSocket Python
    const wsUrl = 'ws://localhost:8765'; // Certifique-se que é o mesmo host/porta do script Python
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Conectado ao servidor WebSocket');
      setIsConnected(true);
      setError(null);
      // Opcional: Enviar uma mensagem para o servidor se necessário
      // ws.send('Olá do cliente React!');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Dados recebidos do WebSocket:', data);
        setCarData(data);
      } catch (e) {
        console.error('Erro ao processar mensagem do WebSocket:', e);
        setError('Erro ao processar dados recebidos.');
      }
    };

    ws.onerror = (err) => {
      console.error('Erro no WebSocket:', err);
      setIsConnected(false);
      setError('Falha na conexão WebSocket. O servidor Python está rodando?');
    };

    ws.onclose = () => {
      console.log('Desconectado do servidor WebSocket');
      setIsConnected(false);
      // Opcional: Tentar reconectar
    };

    // Limpeza ao desmontar o componente
    return () => {
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
    };
  }, []); // Array de dependências vazio significa que este efeito roda uma vez ao montar

  return (
    <div className="car-multimedia-app">
      <header>
        <h1>Central Multimídia  Simulated</h1>
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? 'Conectado' : 'Desconectado'}
        </div>
        {error && <div className="error-message">{error}</div>}
      </header>

      <main className="dashboard">
        <section className="primary-info">
          <SensorDisplay label="Velocidade" value={carData.velocidade} unit="km/h" />
          <SensorDisplay label="Distância Frontal" value={carData.distancia_cm} unit="cm" alert={carData.alerta_distancia} />
        </section>

        <section className="engine-status">
          <h2>Motor & Fluidos</h2>
          <SensorDisplay label="Nível Combustível" value={carData.combustivel_percent} unit="%" alert={carData.alerta_combustivel} />
          <SensorDisplay label="Temp. Motor" value={carData.temperatura_c} unit="°C" />
          <SensorDisplay label="Nível Óleo" value={carData.nivel_oleo} unit="%" />
          <SensorDisplay label="Fluido Freio" value={carData.fluido_freio_percent} unit="%" alert={carData.alerta_fluido_freio} />
        </section>

        <section className="tire-status">
          <h2>Pneus</h2>
          <SensorDisplay label="Pressão Pneus" value={carData.pressao_pneus} unit="PSI" />
          {/* Adicionar mais sensores de pneus se houver */}
        </section>

        <section className="alerts-panel">
          <h2>Alertas</h2>
          <AlertDisplay message="⚠️ ALERTA: Objeto próximo!" active={carData.alerta_distancia} />
          <AlertDisplay message="⛽ ALERTA: Combustível baixo!" active={carData.alerta_combustivel} />
          <AlertDisplay message="🛑 ALERTA: Fluido de freio baixo!" active={carData.alerta_fluido_freio} />
          {/* Adicione mais alertas conforme necessário */}
        </section>

        
        <section className="raw-data">
          <h2>Dados Crus (Debug)</h2>
          <pre>{JSON.stringify(carData, null, 2)}</pre>
        </section> 
      </main>

      <footer>
        <p>Simulação Wokwi & React</p>
      </footer>
    </div>
  );
}

export default App;