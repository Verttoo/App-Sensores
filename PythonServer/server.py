import asyncio
import websockets
import paho.mqtt.client as mqtt
import json
import time

# --- Configurações do Broker MQTT ---
MQTT_BROKER_HOST = "test.mosquitto.org"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC_SUB = "wokwi/carro/sensores"
MQTT_CLIENT_ID = "python-subscriber-carro-websocket-789"

# --- Configurações do WebSocket Server ---
WEBSOCKET_HOST = "localhost" # Ou o IP da sua máquina na rede local se for acessar de outro dispositivo
WEBSOCKET_PORT = 8765

# Variável global para armazenar os dados mais recentes
latest_data = {}
# Conjunto para armazenar todos os clientes WebSocket conectados
connected_clients = set()

# Função chamada quando a ligação ao broker MQTT é estabelecida
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Ligado ao Broker MQTT: {MQTT_BROKER_HOST} com sucesso!")
        client.subscribe(MQTT_TOPIC_SUB)
        print(f"Subscrito ao tópico: {MQTT_TOPIC_SUB}")
    else:
        print(f"Falha ao ligar ao MQTT, código de retorno: {rc}")

# Função chamada quando uma mensagem MQTT é recebida
async def send_to_websockets(data_to_send):
    if connected_clients:
        message = json.dumps(data_to_send)
        # Cria uma lista de tarefas para enviar para todos os clientes
        tasks = [asyncio.create_task(client.send(message)) for client in connected_clients]
        # Aguarda a conclusão de todas as tarefas de envio (ou lida com exceções)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Remove o cliente se o envio falhar (ele pode ter desconectado)
                # Esta é uma forma simplificada, pode precisar de lógica mais robusta
                client_to_remove = list(connected_clients)[i] # Cuidado com a ordem aqui
                print(f"Erro ao enviar para o cliente WebSocket {client_to_remove.remote_address}: {result}. Removendo.")
                if client_to_remove in connected_clients:
                    connected_clients.remove(client_to_remove)


def on_message(client, userdata, msg):
    global latest_data
    print(f"Mensagem MQTT recebida no tópico '{msg.topic}'")
    payload_str = msg.payload.decode('utf-8')
    print(f"Payload MQTT: {payload_str}")
    try:
        data = json.loads(payload_str)
        latest_data = data
        print(f"Dados MQTT processados: {latest_data}")

        # Exemplo de verificação de alertas
        if latest_data.get("alerta_distancia"):
            print("ALERTA PYTHON: Objeto próximo!")
        if latest_data.get("alerta_combustivel"):
            print("ALERTA PYTHON: Combustível baixo!")
        if latest_data.get("alerta_fluido_freio"):
            print("ALERTA PYTHON: Fluido de freio baixo!")

        # Envia os dados para os clientes WebSocket conectados
        # Precisamos agendar isso no loop de eventos do asyncio
        asyncio.run_coroutine_threadsafe(send_to_websockets(latest_data), asyncio.get_event_loop())

    except json.JSONDecodeError:
        print("Erro: Não foi possível descodificar o JSON recebido do MQTT.")
    except Exception as e:
        print(f"Erro ao processar mensagem MQTT: {e}")

# Handler para novas conexões WebSocket
async def websocket_handler(websocket, path):
    global latest_data
    print(f"Cliente WebSocket conectado: {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        # Envia os dados mais recentes assim que o cliente se conecta
        if latest_data:
            await websocket.send(json.dumps(latest_data))

        # Mantém a conexão aberta para enviar atualizações
        # e para detectar desconexões
        async for message_from_client in websocket:
            # Opcional: Lidar com mensagens recebidas do cliente React, se necessário
            print(f"Mensagem recebida do cliente WebSocket {websocket.remote_address}: {message_from_client}")
            # Exemplo: se o cliente enviar "GET_DATA", reenviar latest_data
            if message_from_client == "GET_DATA":
                 if latest_data:
                    await websocket.send(json.dumps(latest_data))

    except websockets.exceptions.ConnectionClosedOK:
        print(f"Cliente WebSocket {websocket.remote_address} desconectado (normal).")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Cliente WebSocket {websocket.remote_address} desconectado com erro: {e}")
    except Exception as e:
        print(f"Erro no handler WebSocket para {websocket.remote_address}: {e}")
    finally:
        print(f"Removendo cliente WebSocket: {websocket.remote_address}")
        connected_clients.remove(websocket)

async def start_mqtt_client():
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=MQTT_CLIENT_ID)
    except TypeError:
        client = mqtt.Client(client_id=MQTT_CLIENT_ID)

    client.on_connect = on_connect
    # Passamos o loop do asyncio para a função on_message para poder agendar tarefas
    client.on_message = on_message

    try:
        print(f"A tentar ligar ao broker MQTT {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        client.loop_start() # Inicia uma thread para o loop de rede MQTT
        print("Loop MQTT iniciado.")
    except Exception as e:
        print(f"Erro ao ligar ao broker MQTT: {e}")
        return None
    return client

async def main_async():
    # Inicia o cliente MQTT
    mqtt_client = await start_mqtt_client()
    if not mqtt_client:
        return

    # Inicia o servidor WebSocket
    server = await websockets.serve(websocket_handler, WEBSOCKET_HOST, WEBSOCKET_PORT)
    print(f"Servidor WebSocket iniciado em ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    print("Pressione Ctrl+C para sair.")

    try:
        # Mantém o servidor WebSocket e o loop MQTT a correr
        await server.wait_closed() # Mantém o servidor a correr indefinidamente
    except KeyboardInterrupt:
        print("Script interrompido pelo utilizador.")
    finally:
        print("A desligar...")
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            print("Cliente MQTT desligado.")
        if server:
            server.close()
            await server.wait_closed() # Garante que o servidor fechou corretamente
            print("Servidor WebSocket desligado.")

if __name__ == '__main__':
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("Programa terminado.")