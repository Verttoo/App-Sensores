import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, ScrollView } from 'react-native';
import bluetooth from '../services/bluetoothService';
import { verificarAlertas } from '../utils/alertas';
import { MODO } from '@env';

export default function MonitorScreen() {
  const [dados, setDados] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const dadosRecebidos =
          MODO === 'desenvolvimento_api'
            ? await bluetooth.lerDadosDaApi()
            : await bluetooth.lerDados();

        setDados(dadosRecebidos);
        verificarAlertas(dadosRecebidos);
      } catch (error) {
        console.error('Erro ao buscar dados:', error);
      } finally {
        setLoading(false);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  if (loading || !dados) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#00FFF7" />
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.header}>📊 Monitoramento em Tempo Real</Text>
      <View style={styles.cardColumn}>
        <View style={styles.cardCircle}>
          <Text style={styles.cardLabel}>ENGINE TEMP</Text>
          <Text style={styles.circleValue}>{dados.temperatura} ºC</Text>
        </View>

        <View style={styles.cardCircle}>
          <Text style={styles.cardLabel}>OIL LEVEL</Text>
          <Text style={styles.circleValue}>{dados.nivel_oleo}%</Text>
        </View>

        <View style={styles.cardCircle}>
          <Text style={styles.cardLabel}>BATTERY LEVEL</Text>
          <Text style={styles.circleValue}>{dados.bateria}%</Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: '#0B0C10',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  header: {
    fontSize: 20,
    color: '#66FCF1',
    marginBottom: 20,
    fontWeight: 'bold',
  },
  cardColumn: {
    flexDirection: 'column',
    alignItems: 'center',
    gap: 16,
  },
  cardCircle: {
    width: 200,
    height: 200,
    borderRadius: 100,
    borderWidth: 8,
    borderColor: '#00FFF7',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#1F2833',
    marginVertical: 10,
  },
  circleValue: {
    fontSize: 30,
    fontWeight: 'bold',
    color: '#00FFF7',
  },
  cardLabel: {
    color: '#C5C6C7',
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
});