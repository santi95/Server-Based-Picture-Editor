import threading
import socket
import random
import json
import pickle
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QProgressBar, \
    QVBoxLayout
from PyQt5.QtGui import QPixmap, QKeyEvent, QTransform
from PyQt5.Qt import QTest, QTimer, QThread, pyqtSignal


class Verificar:
    def __init__(self, verif):
        self.ans = verif


class Client(QThread):
    veriftrigger = pyqtSignal(Verificar)
    fototrigger = pyqtSignal(list)
    usuariotrigger = pyqtSignal(list)
    ocupadotrigger = pyqtSignal(dict)
    blurrytrigger = pyqtSignal(str)
    comentrigger = pyqtSignal(list)
    recortatrigger = pyqtSignal(tuple)

    def __init__(self, front_end):
        super().__init__()
        print("Inicializando cliente...")

        # Inicializamos el socket principal del cliente
        self.host = '192.168.0.34'
        self.port = 5000
        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.connect_to_server()
            self.listen()
            # self.repl()
        except:
            print("Conexión terminada")
            self.socket_cliente.close()
            exit()

    def dashboard(self, dash):
        self.dash = dash

    def connect_to_server(self):
        self.socket_cliente.connect((self.host, self.port))
        print("Cliente conectado exitosamente al servidor...")

    def listen(self):
        thread = threading.Thread(target=self.listen_thread, daemon=True)
        thread.start()

    '''Siempre se mandan tuplas de la forma (info, que_es)'''

    def send(self, msg):
        msg_bytes = pickle.dumps(msg[0])
        # El tipo siempre es de 5 caracteres
        tipo = msg[1].encode()
        msg_length = len(msg_bytes).to_bytes(4, byteorder="big")
        self.socket_cliente.send(msg_length + tipo + msg_bytes)

    def listen_thread(self):
        while True:
            response_bytes_length = self.socket_cliente.recv(4)
            response_length = int.from_bytes(response_bytes_length,
                                             byteorder="big")
            tipo = (self.socket_cliente.recv(5)).decode()
            response = b""
            print(tipo)
            # Recibimos datos hasta que alcancemos la totalidad de los datos
            # indicados en los primeros 4 bytes recibidos.
            while len(response) < response_length:
                response += self.socket_cliente.recv(4096)
            info = pickle.loads(response)

            if tipo == 'hzblu':
                self.blurrytrigger.emit(info)

            # Le envia las fotos al front end
            if tipo == 'fotos':
                self.fototrigger.emit(info)

            # EL evento que manda el servidor cuando entra alguien nuevo
            if tipo == 'ocupp':
                self.ocupadotrigger.emit(info)

            if tipo == 'verif':
                self.veriftrigger.emit(Verificar(info))

            if tipo == 'cnews':
                self.usuariotrigger.emit(info)

            if tipo == 'ocupa':
                self.ocupadotrigger.emit(info)

            if tipo == 'pnerc':
                self.comentrigger.emit(info)

            if tipo == 'creco':
                self.recortatrigger.emit(info)

    def enviar_usuario(self, usuario):
        # Le mandamos una tupla al send
        tupla = (usuario, 'nuser')
        self.send(tupla)

    def pedir_fotos(self):
        tupla = ('nada', 'fotos')
        self.send(tupla)

    def pedir_conectados(self):
        tupla = ('nada', 'ususc')
        self.send(tupla)

    def cambio_fotos(self, nombre_foto, cambio):
        tupla = (nombre_foto, cambio)
        self.send(tupla)

    # Se manda al servidor cada vez que alguien hace un comentario
    def mandar_comentario(self, que, nombre_foto):
        tupla = ((que, nombre_foto), 'comnt')
        self.send(tupla)

    def marcar_ocupada(self, nombre_foto):
        tupla = (nombre_foto, 'ocupi')
        self.send(tupla)

    def marcar_desocupada(self, nombre_foto):
        tupla = (nombre_foto, 'desoc')
        self.send(tupla)

    # Pide que le manden el diccionario con las ocupadas
    def preguntar_cuales_ocupados(self):
        tupla = ('nada', 'dicoc')
        self.send(tupla)

    def add_espectador(self, nombre_usuario, nombre_foto):
        tupla = ((nombre_usuario, nombre_foto), 'espec')
        print('estoy intentando agregarte a la lista de vip')
        self.send(tupla)

    def remove_espectador(self, nombre_usuario, nombre_foto):
        tupla = ((nombre_usuario, nombre_foto), 'esnon')
        self.send(tupla)

    def salir(self):
        tupla = ('nada', 'salir')
        self.send(tupla)
