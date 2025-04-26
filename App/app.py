# app_kivy.py
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock  # Importa o Clock
import requests
import threading
import time

kivy.require('2.1.0')  # Verifique a versão do Kivy

class MonitorApp(App):

    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        # Definir a tela com o título
        self.title_label = Label(text="Monitor de Sensores", font_size=30, size_hint=(1, 0.1))
        self.layout.add_widget(self.title_label)

        # Definir a área para mostrar os dados
        self.data_layout = GridLayout(cols=2, size_hint_y=None)
        self.data_layout.bind(minimum_height=self.data_layout.setter('height'))

        # Scroll para os dados
        self.scroll = ScrollView(size_hint=(1, None), height=400)
        self.scroll.add_widget(self.data_layout)
        self.layout.add_widget(self.scroll)

        # Atualiza os dados a cada 2 segundos
        self.update_data()

        return self.layout

    def update_data(self):
        # Função para atualizar os dados na UI
        def fetch_data():
            while True:
                try:
                    response = requests.get('http://192.168.0.44:5000/dados')  # Troque pelo seu IP
                    dados = response.json()

                    # Atualiza a UI na thread principal
                    Clock.schedule_once(lambda dt: self.update_ui(dados))

                except Exception as e:
                    print(f"Erro ao buscar dados: {e}")

                time.sleep(2)  # Atualiza a cada 2 segundos

        # Inicia a thread de atualização
        thread = threading.Thread(target=fetch_data, daemon=True)
        thread.start()

    def update_ui(self, dados):
        # Limpa o layout
        self.data_layout.clear_widgets()

        # Adiciona os dados na interface
        self.data_layout.add_widget(Label(text="Temperatura:"))
        self.data_layout.add_widget(Label(text=f"{dados['temperatura']} °C"))
        self.data_layout.add_widget(Label(text="Presença:"))
        self.data_layout.add_widget(Label(text="Detectado" if dados['presenca'] else "Ausente"))
        self.data_layout.add_widget(Label(text="Nível de Óleo:"))
        self.data_layout.add_widget(Label(text=f"{dados['nivel_oleo']} %"))

if __name__ == '__main__':
    MonitorApp().run()
