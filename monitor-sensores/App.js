import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, Button, ActivityIndicator } from 'react-native';

export default function App() {
  const [dados, setDados] = useState(null);
  const [loading, setLoading] = useState(false);

  const buscarDados = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://192.168.0.44:5000/dados'); // <- Troque para o seu IP real
      const json = await response.json();
      setDados(json);
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    buscarDados();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>📡 Monitor de Sensores</Text>

      {loading ? (
        <ActivityIndicator size="large" color="#007AFF" />
      ) : dados ? (
        <View style={styles.dadosContainer}>
          <Text style={styles.dado}>🌡️ Temperatura: {dados.temperatura} °C</Text>
          <Text style={styles.dado}>🚶‍♂️ Presença: {dados.presenca ? 'Detectada' : 'Não Detectada'}</Text>
          <Text style={styles.dado}>🛢️ Nível de Óleo: {dados.nivel_oleo} %</Text>
        </View>
      ) : (
        <Text>Nenhum dado disponível</Text>
      )}

      <View style={styles.buttonContainer}>
        <Button title="Atualizar Dados" onPress={buscarDados} color="#28A745" />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F3F3',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    marginBottom: 30,
    fontWeight: 'bold',
  },
  dadosContainer: {
    marginBottom: 30,
  },
  dado: {
    fontSize: 18,
    marginVertical: 5,
  },
  buttonContainer: {
    marginTop: 20,
    width: '80%',
  },
});