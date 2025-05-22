import asyncio
import websockets
import paho.mqtt.client as mqtt
import json
import time

# --- Configurações do Broker MQTT ---
MQTT_BROKER_HOST = "test.mosquitto.org"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC_SUB = "wokwi/carro/sensores"
MQTT_CLIENT_ID = "python-subscriber-carro-websocket-789" # Mantenha ou altere se necessário

# --- Configurações do WebSocket Server ---
WEBSOCKET_HOST = "localhost"
WEBSOCKET_PORT = 8765

# Variável global para armazenar os dados mais recentes
latest_data = {}
# Conjunto para armazenar todos os clientes WebSocket conectados
connected_clients = set()
# Variável global para armazenar o loop de eventos asyncio da thread principal
main_asyncio_loop = None

# Função chamada quando a ligação ao broker MQTT é estabelecida
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Ligado ao Broker MQTT: {MQTT_BROKER_HOST} com sucesso!")
        client.subscribe(MQTT_TOPIC_SUB)
        print(f"Subscrito ao tópico: {MQTT_TOPIC_SUB}")
    else:
        print(f"Falha ao ligar ao MQTT, código de retorno: {rc}")

# Função assíncrona para enviar dados para os clientes WebSocket
async def send_to_websockets(data_to_send):
    if connected_clients:
        message = json.dumps(data_to_send)
        # Cópia do set para evitar problemas de modificação durante iteração
        clients_to_send = list(connected_clients)
        tasks = [asyncio.create_task(client.send(message)) for client in clients_to_send]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for client, result in zip(clients_to_send, results):
            if isinstance(result, Exception):
                print(f"Erro ao enviar para o cliente WebSocket {client.remote_address}: {result}. Removendo.")
                if client in connected_clients: # Verifica se ainda está no set original
                    connected_clients.remove(client)


# Função chamada quando uma mensagem MQTT é recebida
def on_message(client, userdata, msg):
    global latest_data, main_asyncio_loop # Precisamos acessar o loop principal
    print(f"Mensagem MQTT recebida no tópico '{msg.topic}'")
    payload_str = msg.payload.decode('utf-8')
    # print(f"Payload MQTT: {payload_str}") # Descomente para debug detalhado
    try:
        data = json.loads(payload_str)
        latest_data = data
        print(f"Dados MQTT processados: {latest_data}")

        # Exemplo de verificação de alertas
        if latest_data.get("alerta_distancia"):
            print("ALERTA PYTHON: Objeto próximo!")
        # Adicione outros alertas aqui se necessário

        # Envia os dados para os clientes WebSocket conectados
        # Usando o loop de eventos da thread principal que foi armazenado
        if main_asyncio_loop and main_asyncio_loop.is_running():
            asyncio.run_coroutine_threadsafe(send_to_websockets(latest_data), main_asyncio_loop)
        else:
            print("ERRO: Loop de eventos Asyncio principal não está disponível ou não está rodando.")

    except json.JSONDecodeError:
        print("Erro: Não foi possível descodificar o JSON recebido do MQTT.")
    except Exception as e:
        print(f"Erro ao processar mensagem MQTT: {e}") # Isso agora irá capturar o erro que você viu

# Handler para novas conexões WebSocket
async def websocket_handler(websocket, path=None): # Path agora é opcional
    global latest_data
    print(f"Cliente WebSocket conectado: {websocket.remote_address}, Path: {path if path else 'N/A'}") # Mostra o path
    connected_clients.add(websocket)
    try:
        if latest_data: # Envia dados atuais se houver
            await websocket.send(json.dumps(latest_data))
        
        async for message_from_client in websocket:
            print(f"Mensagem recebida do cliente WebSocket {websocket.remote_address}: {message_from_client}")
            if message_from_client == "GET_DATA":
                 if latest_data:
                    await websocket.send(json.dumps(latest_data))
    except websockets.exceptions.ConnectionClosed:
        print(f"Cliente WebSocket {websocket.remote_address} desconectado (normal).")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Cliente WebSocket {websocket.remote_address} desconectado com erro: {e}")
    except Exception as e:
        print(f"Erro no handler WebSocket para {websocket.remote_address}: {e}")
    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        print(f"Cliente WebSocket {websocket.remote_address} removido/finalizado.")


# Função para iniciar o cliente MQTT
def setup_mqtt_client(): # Alterado para não ser async, pois on_message não é async
    try:
        # Para paho-mqtt v2.x, use mqtt.CallbackAPIVersion.VERSION2 ou VERSION1
        # Para paho-mqtt v1.x, omita callback_api_version
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=MQTT_CLIENT_ID)
    except TypeError: # Compatibilidade com versões mais antigas
        client = mqtt.Client(client_id=MQTT_CLIENT_ID)

    client.on_connect = on_connect
    client.on_message = on_message # on_message agora usará main_asyncio_loop

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
    global main_asyncio_loop
    # Obtém o loop de eventos da thread principal onde asyncio.run() foi chamado
    main_asyncio_loop = asyncio.get_running_loop()

    # Inicia o cliente MQTT
    mqtt_client = setup_mqtt_client() # Não precisa ser 'await' pois não é mais async
    if not mqtt_client:
        print("Falha ao iniciar cliente MQTT. Encerrando.")
        return

    # Inicia o servidor WebSocket
    server = await websockets.serve(websocket_handler, WEBSOCKET_HOST, WEBSOCKET_PORT)
    print(f"Servidor WebSocket iniciado em ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    print("Pressione Ctrl+C para sair.")

    try:
        # Mantém o servidor WebSocket a correr (e o loop asyncio principal)
        await server.wait_closed()
    except KeyboardInterrupt:
        print("Script interrompido pelo utilizador.")
    finally:
        print("A desligar...")
        if mqtt_client:
            mqtt_client.loop_stop() # Para a thread do MQTT
            mqtt_client.disconnect()
            print("Cliente MQTT desligado.")
        # O servidor websockets será fechado automaticamente ao sair do await server.wait_closed()
        # ou pode ser fechado explicitamente se necessário antes.
        # server.close()
        # await server.wait_closed()
        print("Servidor WebSocket (deveria estar) desligado.")

if __name__ == '__main__':
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("Programa terminado pelo utilizador.")
    except Exception as e:
        print(f"Erro inesperado no __main__: {e}")