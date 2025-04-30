import { API_URL } from '@env';

let RNBluetoothClassic = null;

class BluetoothManager {
  constructor() {
    this.device = null;
    this.connection = null;

    // Importa o módulo Bluetooth só se não estiver no Expo
    try {
      RNBluetoothClassic = require('react-native-bluetooth-classic').default;
    } catch (e) {
      console.log('Bluetooth nativo não carregado (ambiente Expo ou sem dependência)');
    }
  }

  async conectar() {
    if (!RNBluetoothClassic) {
      throw new Error('Bluetooth indisponível neste ambiente');
    }

    try {
      const devices = await RNBluetoothClassic.list();
      const arduino = devices.find(
        d => d.name && (d.name.includes('HC-05') || d.name.includes('Arduino'))
      );
      if (!arduino) throw new Error('Dispositivo Arduino não encontrado');

      const conectado = await arduino.connect();
      if (conectado) {
        this.device = arduino;
        this.connection = true;
        return true;
      }
      return false;
    } catch (error) {
      console.error('Erro na conexão Bluetooth:', error);
      throw error;
    }
  }

  async lerDados() {
    if (!this.device || !this.connection) {
      throw new Error('Dispositivo não conectado');
    }
    if (!RNBluetoothClassic) {
      throw new Error('Bluetooth indisponível neste ambiente');
    }

    try {
      const data = await this.device.read();
      return JSON.parse(data);
    } catch (error) {
      console.error('Erro ao ler dados Bluetooth:', error);
      throw error;
    }
  }

  desconectar() {
    this.device = null;
    this.connection = null;
  }

  estaConectado() {
    return this.connection != null;
  }

  async lerDadosDaApi() {
    try {
      const response = await fetch(`${API_URL}/dados`);;
      if (!response.ok) {
        throw new Error('Erro ao acessar a API: ' + response.status);
      }
      const json = await response.json();
      return json;
    } catch (error) {
      console.error('Erro ao buscar dados da API:', error);
      throw error;
    }
  }
}

const bluetooth = new BluetoothManager();
export default bluetooth;
