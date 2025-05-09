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
      <Text style={styles.header}>SENSOR CONTROL</Text>
      <Text style={styles.description}>Monitoramento inteligente de sensores veiculares</Text>
      <Text style={styles.modo}>Modo atual: {MODO}</Text>

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
    backgroundColor: '#0B0C10',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  logo: {
    width: 150,
    height: 150,
    marginBottom: 30,
  },
  header: {
    fontSize: 26,
    color: '#66FCF1',
    fontWeight: 'bold',
    marginBottom: 16,
  },
  description: {
    fontSize: 16,
    color: '#C5C6C7',
    textAlign: 'center',
    marginBottom: 10,
  },
  modo: {
    fontSize: 14,
    color: '#888',
    marginBottom: 30,
  },
  button: {
    backgroundColor: '#1F2833',
    paddingVertical: 14,
    paddingHorizontal: 40,
    borderRadius: 30,
    borderWidth: 2,
    borderColor: '#00FFF7',
  },
  buttonText: {
    color: '#00FFF7',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
