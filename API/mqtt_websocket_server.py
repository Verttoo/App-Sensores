# mqtt_websocket_server.py
import asyncio
import websockets
import paho.mqtt.client as mqtt
import json
import time

# --- Configurações do Broker MQTT ---
MQTT_BROKER_HOST = "broker.hivemq.com" # Ou broker.hivemq.com se test.mosquitto.org estiver com problemas
MQTT_BROKER_PORT = 1883
MQTT_TOPIC_SUB = "wokwi/carro/sensores" # Tópico que o ESP32 publica
MQTT_CLIENT_ID = "python-subscriber-carro-websocket-unique" # ID de cliente único

# --- Configurações do WebSocket Server ---
WEBSOCKET_HOST = "localhost"
WEBSOCKET_PORT = 8765

latest_data = {}
connected_clients = set()
main_asyncio_loop = None

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Ligado ao Broker MQTT: {MQTT_BROKER_HOST} com sucesso!")
        client.subscribe(MQTT_TOPIC_SUB)
        print(f"Subscrito ao tópico: {MQTT_TOPIC_SUB}")
    else:
        print(f"Falha ao ligar ao MQTT, código de retorno: {rc}")

async def send_to_websockets(data_to_send):
    if connected_clients:
        message = json.dumps(data_to_send)
        clients_to_send = list(connected_clients)
        tasks = [asyncio.create_task(client.send(message)) for client in clients_to_send]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for client, result in zip(clients_to_send, results):
            if isinstance(result, Exception):
                print(f"Erro ao enviar para o cliente WebSocket {client.remote_address}: {result}. Removendo.")
                if client in connected_clients:
                    connected_clients.remove(client)

def on_message(client, userdata, msg):
    global latest_data, main_asyncio_loop
    # print(f"Mensagem MQTT recebida no tópico '{msg.topic}'") # Descomente para debug
    payload_str = msg.payload.decode('utf-8')
    try:
        data = json.loads(payload_str)
        latest_data = data
        print(f"Dados MQTT processados (Python): {latest_data}") # Verifique este output!

        # Alertas impressos no console do Python (não afetam o React)
        if latest_data.get("alerta_distancia"): print("ALERTA PYTHON (CONSOLE): Objeto próximo!")
        if latest_data.get("alerta_combustivel"): print("ALERTA PYTHON (CONSOLE): Combustível baixo!")
        if latest_data.get("alerta_fluido_freio"): print("ALERTA PYTHON (CONSOLE): Fluido de freio baixo!")
        if latest_data.get("alerta_oleo_motor"): print("ALERTA PYTHON (CONSOLE): Óleo do motor baixo!")
        if latest_data.get("alerta_velocidade"): print("ALERTA PYTHON (CONSOLE): Velocidade alta (sistema)!")


        if main_asyncio_loop and main_asyncio_loop.is_running():
            asyncio.run_coroutine_threadsafe(send_to_websockets(latest_data), main_asyncio_loop)
        else:
            print("ERRO PYTHON: Loop de eventos Asyncio principal não está disponível.")
    except json.JSONDecodeError:
        print("Erro PYTHON: Não foi possível descodificar o JSON recebido do MQTT.")
    except Exception as e:
        print(f"Erro PYTHON ao processar mensagem MQTT: {e}")

async def websocket_handler(websocket, path=None): # path=None para compatibilidade
    global latest_data
    print(f"Cliente WebSocket conectado: {websocket.remote_address}, Path: {path if path else 'N/A'}")
    connected_clients.add(websocket)
    try:
        if latest_data:
            await websocket.send(json.dumps(latest_data))
        async for message_from_client in websocket:
            print(f"Mensagem recebida do WebSocket {websocket.remote_address}: {message_from_client}")
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

def setup_mqtt_client():
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=MQTT_CLIENT_ID)
    except TypeError:
        client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        print(f"A tentar ligar ao broker MQTT {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        client.loop_start()
        print("Loop MQTT iniciado.")
    except Exception as e:
        print(f"Erro ao ligar ao broker MQTT: {e}")
        return None
    return client

async def main_async():
    global main_asyncio_loop
    main_asyncio_loop = asyncio.get_running_loop()
    mqtt_client = setup_mqtt_client()
    if not mqtt_client:
        print("Falha ao iniciar cliente MQTT. Encerrando.")
        return
    server = await websockets.serve(websocket_handler, WEBSOCKET_HOST, WEBSOCKET_PORT)
    print(f"Servidor WebSocket iniciado em ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    print("Pressione Ctrl+C para sair.")
    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        print("Script interrompido pelo utilizador.")
    finally:
        print("A desligar...")
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            print("Cliente MQTT desligado.")
        print("Servidor WebSocket (deveria estar) desligado.")

if __name__ == '__main__':
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("Programa terminado pelo utilizador.")
    except Exception as e:
        print(f"Erro inesperado no __main__: {e}")