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
      <Text style={styles.header}>
  🔧 Status dos Sensores
      </Text>

      <View style={styles.cardRow}>
        <View style={[styles.kpiBox, { backgroundColor: '#1f2833' }]}>
          <Text style={styles.kpiLabel}>ENGINE TEMP 🌡️</Text>
          <Text style={styles.kpiValue}>{dados.temperatura} ºC</Text>
        </View>

        <View style={[styles.kpiBox, { backgroundColor: '#0b0c10' }]}>
          <Text style={styles.kpiLabel}>OIL LEVEL 🧴</Text>
          <Text style={styles.kpiValue}>{dados.nivel_oleo}%</Text>
        </View>

        <View style={[styles.kpiBox, { backgroundColor: '#1f2833' }]}>
          <Text style={styles.kpiLabel}>BATTERY LEVEL 🔋</Text>
          <Text style={styles.kpiValue}>{dados.bateria}%</Text>
        </View>

        <View style={[styles.kpiBox, { backgroundColor: '#1f2833' }]}>
          <Text style={styles.kpiLabel}>WATER LEVEL 💧</Text>
          <Text style={styles.kpiValue}>{dados.nivel_agua}%</Text>
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
    justifyContent: 'flex-start',
    padding: 20,
  },
  header: {
    fontSize: 26,
    color: '#66FCF1',
    fontWeight: 'bold',
    marginBottom: 30,
    textAlign: 'center',
    backgroundColor: '#1F2833',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 12,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
    elevation: 2,
  },
  cardRow: {
    width: '100%',
    gap: 16,
  },
  kpiBox: {
    width: '100%',
    height: 100,
    borderRadius: 20,
    padding: 20,
    justifyContent: 'center',
    backgroundColor: '#1F2833',
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
    elevation: 3,
  },
  kpiLabel: {
    color: '#C5C6C7',
    fontSize: 14,
    fontWeight: 'bold',
  },
  kpiValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#00FFF7',
    marginTop: 4,
  },
});