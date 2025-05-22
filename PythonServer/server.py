import paho.mqtt.client as mqtt
import json
import time

# --- Configurações do Broker MQTT ---
# Deve ser o mesmo broker que o ESP32 está a usar
MQTT_BROKER_HOST = "test.mosquitto.org"
# MQTT_BROKER_HOST = "broker.hivemq.com"
MQTT_BROKER_PORT = 1883  # Porta padrão MQTT
MQTT_TOPIC_SUB = "wokwi/carro/sensores"  # Tópico para subscrever (o mesmo que o ESP32 publica)
MQTT_CLIENT_ID = "python-subscriber-carro-456" # ID de cliente único

# Variável global para armazenar os dados mais recentes (opcional, depende de como quer usar os dados)
latest_data = {}

# Função chamada quando a ligação ao broker é estabelecida
def on_connect(client, userdata, flags, rc, properties=None): # Adicionado properties para compatibilidade com paho-mqtt v2.x
    if rc == 0:
        print(f"Ligado ao Broker MQTT: {MQTT_BROKER_HOST} com sucesso!")
        # Subscreve o tópico após a ligação
        client.subscribe(MQTT_TOPIC_SUB)
        print(f"Subscrito ao tópico: {MQTT_TOPIC_SUB}")
    else:
        print(f"Falha ao ligar, código de retorno: {rc}")

# Função chamada quando uma mensagem é recebida do broker
def on_message(client, userdata, msg):
    global latest_data
    print(f"Mensagem recebida no tópico '{msg.topic}'")
    payload_str = msg.payload.decode('utf-8')
    print(f"Payload: {payload_str}")
    try:
        data = json.loads(payload_str)
        latest_data = data # Atualiza os dados mais recentes
        # Aqui pode processar os dados como precisar:
        # - Guardar numa base de dados
        # - Acionar alertas
        # - Atualizar uma interface de utilizador, etc.
        print(f"Dados processados: {latest_data}")

        # Exemplo de verificação de alertas (baseado nos dados recebidos)
        if latest_data.get("alerta_distancia"):
            print("ALERTA PYTHON: Objeto próximo!")
        if latest_data.get("alerta_combustivel"):
            print("ALERTA PYTHON: Combustível baixo!")
        if latest_data.get("alerta_fluido_freio"):
            print("ALERTA PYTHON: Fluido de freio baixo!")

    except json.JSONDecodeError:
        print("Erro: Não foi possível descodificar o JSON recebido.")
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

def main():
    # Cria um novo cliente MQTT (para paho-mqtt v2.x, use mqtt.CallbackAPIVersion.VERSION1)
    # Se estiver a usar paho-mqtt v1.x, pode omitir o argumento callback_api_version
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=MQTT_CLIENT_ID)
    except TypeError: # Para compatibilidade com versões mais antigas de paho-mqtt
        client = mqtt.Client(client_id=MQTT_CLIENT_ID)


    # Define as funções de callback
    client.on_connect = on_connect
    client.on_message = on_message

    # Tenta ligar ao broker
    try:
        print(f"A tentar ligar ao broker {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60) # 60 é o keepalive
    except Exception as e:
        print(f"Erro ao ligar ao broker MQTT: {e}")
        return

    # Inicia o loop de rede em segundo plano para processar tráfego de rede,
    # callbacks e reconexões.
    # loop_forever() é bloqueante. Use loop_start() para não bloqueante.
    try:
        # client.loop_forever() # Bloqueia a execução aqui, bom para scripts simples
        client.loop_start() # Inicia uma thread para o loop de rede
        print("Loop MQTT iniciado. A aguardar mensagens...")
        print("Pressione Ctrl+C para sair.")
        while True:
            # Mantém o script principal a correr
            # Pode adicionar outra lógica aqui se necessário,
            # ou simplesmente esperar que as mensagens cheguem.
            time.sleep(1)
            # print(f"Dados mais recentes no loop principal: {latest_data}") # Debug opcional

    except KeyboardInterrupt:
        print("Script interrompido pelo utilizador.")
    finally:
        print("A desligar o cliente MQTT...")
        client.loop_stop() # Para a thread do loop de rede
        client.disconnect()
        print("Cliente MQTT desligado.")

if __name__ == '__main__':
    main()
