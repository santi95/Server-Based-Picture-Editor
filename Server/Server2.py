import threading
import socket
import random
import pickle
from Func_photo import Foto
import copy


class Server:
    conecciones = []
    usuarios_conectados = []

    def __init__(self, port, host):
        print("Inicializando servidor...")

        # Inicializar socket principal del servidor.
        self.host = host
        self.port = port
        self.socket_servidor = socket.socket(socket.AF_INET,
                                             socket.SOCK_STREAM)
        self.bind_and_listen()
        self.accept_connections()

        # Es la entidad del editor Func_photo,
        # que nos hará los cambios en las imagenes del servidor
        self.editor = Foto()
        # Comentarios, este diccionario tendrá una lista con todos los comentarios de la foto
        self.dicti = {}
        # Diccionario con True o False de cuales son las fotos ocupadas
        self.ocupadas = {}
        self.dicti_espectadores = {}

        # llena el diccionario al iniciarse el servidor
        for i in range(1, 10):
            nombre_imagen = "imagen_{}.png".format(i)
            self.ocupadas[nombre_imagen] = False
            self.dicti_espectadores[nombre_imagen] = []
            self.dicti[nombre_imagen] = []

    # El método bind_and_listen() enlazará el socket creado con el host y puerto
    # indicado. Primero se enlaza el socket y luego que esperando por conexiones
    # entrantes, con un máximo de 5 clientes en espera.
    def bind_and_listen(self):
        self.socket_servidor.bind((self.host, self.port))
        self.socket_servidor.listen(5)
        print("Servidor escuchando en {}:{}...".format(self.host, self.port))

    # El método accept_connections() inicia el thread que aceptará clientes.
    # Aunque podríamos aceptar clientes en el thread principal de la instancia,
    # resulta útil hacerlo en un thread aparte que nos permitirá realizar la
    # lógica en la parte del servidor sin dejar de aceptar clientes. Por ejemplo,
    # seguir procesando archivos.
    def accept_connections(self):
        thread = threading.Thread(target=self.accept_connections_thread)
        thread.start()

    # El método accept_connections_thread() será arrancado como thread para
    # aceptar clientes. Cada vez que aceptamos un nuevo cliente, iniciamos un
    # thread nuevo encargado de manejar el socket para ese cliente.
    def accept_connections_thread(self):
        print("Servidor aceptando conexiones...")

        while True:
            client_socket, _ = self.socket_servidor.accept()
            listening_client_thread = threading.Thread(
                target=self.listen_client_thread,
                args=(client_socket,),
                daemon=True
            )
            listening_client_thread.start()

    # Usaremos el método send() para enviar mensajes hacia algún socket cliente.
    # Debemos implementar en este método el protocolo de comunicación donde los
    # primeros 4 bytes indicarán el largo del mensaje.
    '''Siempre se mandan tuplas de la siguiente forma (información, tipo_mensaje)'''

    @staticmethod
    def send(value, socket):
        try:
            msg_bytes = pickle.dumps(value[0])
            tipo = value[1].encode()
            msg_bytes = msg_bytes
            msg_length = len(msg_bytes).to_bytes(4, byteorder="big")
            # tipo siempre va a tener largo 5
            socket.send(msg_length + tipo + msg_bytes)
        except:
            pass

    # El método listen_client_thread() sera ejecutado como thread que escuchará a un
    # cliente en particular. Implementa las funcionalidades del protocolo de comunicación
    # que permiten recuperar la informacion enviada.
    def listen_client_thread(self, client_socket):
        Server.conecciones.append(client_socket)

        while True:
            try:  # Maneja el error de cuando se cierra el socket a la mala, sorry por eso
                response_bytes_length = client_socket.recv(4)
                response_length = int.from_bytes(response_bytes_length,
                                                 byteorder="big")
                tipo = (client_socket.recv(5)).decode()
                response = b""

                while len(response) < response_length:
                    response += client_socket.recv(4096)

                received = pickle.loads(response)
                if received != "":
                    response = self.handle_command(tipo, received,
                                                   client_socket)
                    self.send(response, client_socket)

                    if response[1] == 'verif' and response[0] == True:
                        lista_usuarios = [i[0] for i in
                                          Server.usuarios_conectados]
                        sockets = [i[1] for i in Server.usuarios_conectados]
                        for i in sockets:
                            # Mandamos señal a todos de que entró alguien nuevo
                            tupla = (lista_usuarios, 'cnews')
                            self.send(tupla, i)
            except:
                pass

    def handle_command(self, tipo, msge, socket):
        # Estamos respondiendo si esq existe otro cliente con el mismo usuario
        print(tipo)
        if tipo == 'nuser':
            usuarios = [i[0] for i in Server.usuarios_conectados]
            if msge not in usuarios:
                Server.usuarios_conectados.append((msge, socket))
                return (True, 'verif')
            else:
                return (False, 'verif')

        if tipo == 'ususc':
            lista_usuarios = [i[0] for i in Server.usuarios_conectados]
            sockets = [i[1] for i in Server.usuarios_conectados]
            for i in sockets:
                # Mandamos señal a todos de que entró alguien nuevo
                tupla = (lista_usuarios, 'cnews')
                self.send(tupla, i)

        if tipo == 'fotos':
            lista = []
            self.fotos = random.sample(range(1, 10), 6)
            for i in self.fotos:
                nombre = "imagen_{}.png".format(i)
                with open("image/{}".format(nombre), 'rb') as file:
                    img = file.read()
                    lista.append((nombre, img))
            return (lista, 'fotos')

        if tipo == 'blurr':
            self.editor = Foto()
            nombre_foto = msge
            self.editor.hacer_blurry(nombre_foto)
            # Mandarle a todos los que estan en modo
            # espectador los cambios hechos
            lista_sockets_espectadores = self.dicti_espectadores[msge]
            print(len(lista_sockets_espectadores))
            for i in lista_sockets_espectadores:
                tupla = ('nada', 'hzblu')
                self.send(tupla, i[0])

        if tipo == 'recor':
            print('yaya ok lo corto')
            # (self.nombre, self.primer_click, self.soltar_click, self.foto.frameGeometry())
            self.editor.recortar(msge)
            # Mandarle a todos los que estan en modo
            # espectador los cambios hechos
            lista_sockets_espectadores = self.dicti_espectadores[msge[0]]
            print(len(lista_sockets_espectadores))
            for i in lista_sockets_espectadores:
                tupla = (msge, 'creco')
                self.send(tupla, i[0])

        if tipo == 'salir':
            sockets = [i[1] for i in Server.usuarios_conectados]
            pos = sockets.index(socket)
            Server.usuarios_conectados.pop(pos)
            Server.conecciones.pop(pos)

            lista_usuarios = [i[0] for i in Server.usuarios_conectados]
            sockets = [i[1] for i in Server.usuarios_conectados]
            for i in sockets:
                # Mandamos señal a todos de que entró alguien nuevo
                tupla = (lista_usuarios, 'cnews')
                self.send(tupla, i)

        # Le llega el comentario recien hecho
        if tipo == 'comnt':
            print(msge, 'este es el que te fijas')
            self.dicti[msge[1]].append(msge[0])
            print(self.dicti)
            # Mandarselo a todos
            lista_sockets_espectadores = self.dicti_espectadores[msge[1]]
            # pnrc poner comentario
            print(lista_sockets_espectadores)
            if socket not in lista_sockets_espectadores:
                lista_sockets_espectadores.append([socket])
            print(socket)
            print(lista_sockets_espectadores)
            for i in lista_sockets_espectadores:
                tupla = (self.dicti[msge[1]], 'pnerc')
                self.send(tupla, i[0])
                print('enviado con éxito')

        if tipo == 'ocupi':
            self.ocupadas[msge] = True
            # Avisarle a todos
            sockets = [i[1] for i in Server.usuarios_conectados]
            for i in sockets:
                # Mandamos señal a todos de que entró alguien nuevo
                tupla = (self.ocupadas, 'ocupa')
                self.send(tupla, i)

        if tipo == 'desoc':
            self.ocupadas[msge] = False
            # Avisarle a todos
            sockets = [i[1] for i in Server.usuarios_conectados]
            for i in sockets:
                # Mandamos señal a todos de que entró alguien nuevo
                tupla = (self.ocupadas, 'ocupa')
                self.send(tupla, i)

        if tipo == 'dicoc':
            tupla = (self.ocupadas, 'ocupp')
            return tupla

        if tipo == 'espec':
            print('llegó un espectador a mirar lo que haces')
            print(msge, 'mensaje')
            print(Server.usuarios_conectados, 'usuarios conectados')
            socket = [i[1] for i in Server.usuarios_conectados if
                      i[0] == msge[0]]
            print(socket, 'este es el socket del frontend')
            self.dicti_espectadores[msge[1]].append(socket)

        # Sacamos de la lista de espectadores
        if tipo == 'esnon':
            print('se fue un espectador, eres fome')
            socket = [i[1] for i in Server.usuarios_conectados if
                      i[0] == msge[0]]
            pos = self.dicti_espectadores[msge[1]].index(socket)
            self.dicti_espectadores[msge[1]].pop(pos)

        tipo = None


if __name__ == "__main__":
    port = 5000
    host = 'localhost'

    server = Server(port, host)
