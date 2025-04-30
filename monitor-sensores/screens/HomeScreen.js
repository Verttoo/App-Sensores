import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, Alert } from 'react-native';
import bluetooth from '../services/bluetoothService';
import { MODO } from '@env'; // pega a variável do .env

export default function HomeScreen({ navigation }) {
  const handleConectar = async () => {
    if (MODO === 'desenvolvimento_api') {
      console.log('[DEBUG] MODO=desenvolvimento_api → pulando conexão Bluetooth');
      navigation.navigate('Monitor');
      return;
    }

    try {
      const conectado = await bluetooth.conectar();
      if (conectado) {
        navigation.navigate('Monitor');
      } else {
        Alert.alert('Erro', 'Não foi possível conectar ao dispositivo Bluetooth.');
      }
    } catch (error) {
      Alert.alert('Erro de Conexão', error.message);
    }
  };

  return (
    <View style={styles.container}>
      <Image source={require('../assets/logo.png')} style={styles.logo} resizeMode="contain" />
      <Text style={styles.title}>SENSOR CONTROL</Text>
      <Text style={styles.description}>Monitoramento inteligente de sensores veiculares</Text>

      {/* Mostrar o modo atual (opcional, útil para debug ou TCC) */}
      <Text style={styles.modo}>Modo: {MODO}</Text>

      <TouchableOpacity style={styles.button} onPress={handleConectar}>
        <Text style={styles.buttonText}>
          {MODO === 'desenvolvimento_api' ? 'ENTRAR' : 'CONNECT BT'}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 20,
  },
  logo: {
    width: 150,
    height: 150,
    marginBottom: 30,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  description: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 10,
  },
  modo: {
    fontSize: 14,
    color: '#999',
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#1ABC9C',
    paddingVertical: 12,
    paddingHorizontal: 40,
    borderRadius: 25,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});