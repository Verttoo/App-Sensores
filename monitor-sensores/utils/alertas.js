import { Alert } from 'react-native';

export function verificarAlertas(dados) {
  if (!dados) return;

  if (dados.temperatura > 90) {
    Alert.alert(
      '🚨 Alerta de Temperatura!',
      `A temperatura está em ${dados.temperatura}°C!`,
      [{ text: 'OK' }]
    );
  }

  if (dados.nivel_oleo < 30) {
    Alert.alert(
      '🚨 Alerta de Nível de Óleo',
      `O nível do óleo está em ${dados.nivel_oleo}%`,
      [{ text: 'OK' }]
    );
  }

  if (dados.nivel_agua < 10) {
    Alert.alert(
      '🚨 Alerta de Nível de Água',
      `O nível da água está em ${dados.nivel_agua}%`,
      [{ text: 'OK' }]
    );
  }
}
