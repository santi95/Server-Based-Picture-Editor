from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressBar
from PyQt5.QtGui import QIcon, QPixmap, QTransform
from PyQt5.Qt import QTimer, QTest, QFrame, QDrag, QApplication, QLabel, QPushButton
from PyQt5.QtCore import Qt, QMimeData, QSize
import sys
import socket
from Client2 import Client
import functools
import os
from BackEnd import Foto
from zlib import decompress, compress, crc32
from threading import Thread
import time

login = uic.loadUiType('Login.ui')
dash = uic.loadUiType('Dashboard.ui')
edit = uic.loadUiType('Editor.ui')
pop = uic.loadUiType('PopUpLogin.ui')


class Login(login[0], login[1]):
    def __init__(self):
        super().__init__()
        self.a = Client(self)
        self.setupUi(self)
        self.setObjectName('main')
        self.setStyleSheet(
            "#main {background-image: url(fondo.jpg); background-attachment: fixed;}")
        self.showMaximized()
        self.apreto.clicked.connect(self.get_login)
        self.a.veriftrigger.connect(self.verifica)

    def verifica(self, event):
        verificacion = event.ans
        if verificacion == True:
            self.hide()
            self.d = Dashboard(self.a, self.usuario, self)
            self.d.showMaximized()
        else:
            self.popup = PopUp()
            self.popup.show()

    def get_login(self):

        self.usuario = self.lineEdit.text()
        '''Nos conectamos al Cliente,
            para que le hable al Servidor y nos entregue una lista
            con las 6 fotos del Dashboard'''
        if len(self.usuario) > 2 and self.usuario.isalnum():
            # Le estamos preguntando si hay otro usuario llamado igual
            self.a.enviar_usuario(self.usuario)
        else:
            self.popup = PopUp()
            self.popup.show()

    def closeEvent(self, event):
        self.hide()


class PopUp(pop[0], pop[1]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.exit_pop.clicked.connect(self.salir)

    def salir(self):
        self.hide()


class Dashboard(dash[0], dash[1]):
    def __init__(self, cliente, nombre_usuario, inicio):
        super().__init__()
        self.llego_dicti = False
        self.cliente = cliente
        self.cliente.dashboard(self)
        self.cliente.fototrigger.connect(self.recibir_fotos)
        self.cliente.usuariotrigger.connect(self.mostrar_conectados)
        self.cliente.ocupadotrigger.connect(self.recibir_dicti_ocupados)

        # conectado al fototrigger
        self.cliente.pedir_fotos()

        self.recibidas = False
        self.nombre_usuario = nombre_usuario
        self.inicio = inicio

        self.setupUi(self)
        self.centralwidget.setObjectName('dash')
        self.centralwidget.setStyleSheet(
            "#dash {background-image: url(Fondo_Dash.jpg); background-attachment: fixed;}    ")
        self.cerrar.clicked.connect(self.cerrar_sesion)

        # Espera a que lleguen las fotos
        a = True
        while a:
            QTest.qWait(700)
            if self.recibidas:
                a = False
        print('sali de uno')
        self.cliente.preguntar_cuales_ocupados()
        # Conectado al ocupadotrigger

        icon0 = QIcon()
        self.pix0 = QPixmap()
        self.pix0.loadFromData(self.lista_fotos[0][1])
        icon0.addPixmap(self.pix0)

        icon1 = QIcon()
        self.pix1 = QPixmap()
        self.pix1.loadFromData(self.lista_fotos[1][1])
        icon1.addPixmap(self.pix1)

        icon2 = QIcon()
        self.pix2 = QPixmap()
        self.pix2.loadFromData(self.lista_fotos[2][1])
        icon2.addPixmap(self.pix2)

        icon3 = QIcon()
        self.pix3 = QPixmap()
        self.pix3.loadFromData(self.lista_fotos[3][1])
        icon3.addPixmap(self.pix3)

        icon4 = QIcon()
        self.pix4 = QPixmap()
        self.pix4.loadFromData(self.lista_fotos[4][1])
        icon4.addPixmap(self.pix4)

        icon5 = QIcon()
        self.pix5 = QPixmap()
        self.pix5.loadFromData(self.lista_fotos[5][1])
        icon5.addPixmap(self.pix5)

        # Parte ineficiente que tengo que cambiar para que se vea kul :D
        self.img1.clicked.connect(self.editor1)
        self.img1.setIcon(icon0)
        self.img2.clicked.connect(self.editor2)
        self.img2.setIcon(icon1)
        self.img3.clicked.connect(self.editor3)
        self.img3.setIcon(icon2)
        self.img4.clicked.connect(self.editor4)
        self.img4.setIcon(icon3)
        self.img5.clicked.connect(self.editor5)
        self.img5.setIcon(icon4)
        self.img6.clicked.connect(self.editor6)
        self.img6.setIcon(icon5)
        self.cliente.pedir_conectados()

        # Espera la info de las fotos ocupadas
        a = True
        while a:
            QTest.qWait(700)
            if self.llego_dicti:
                a = False
            else:
                pass
        print('salir de 2')
        # seteamos los tags iniciales de Ocupados o no
        if self.diccio_ocupados[self.lista_fotos[0][0]]:
            self.dis1.setText('Ocupado')
        else:
            self.dis1.setText('Disponible')

        if self.diccio_ocupados[self.lista_fotos[1][0]]:
            self.dis2.setText('Ocupado')
        else:
            self.dis2.setText('Disponible')

        if self.diccio_ocupados[self.lista_fotos[2][0]]:
            self.dis3.setText('Ocupado')
        else:
            self.dis3.setText('Disponible')

        if self.diccio_ocupados[self.lista_fotos[3][0]]:
            self.dis4.setText('Ocupado')
        else:
            self.dis4.setText('Disponible')
        if self.diccio_ocupados[self.lista_fotos[4][0]]:
            self.dis5.setText('Ocupado')
        else:
            self.dis5.setText('Disponible')
        if self.diccio_ocupados[self.lista_fotos[5][0]]:
            self.dis6.setText('Ocupado')
        else:
            self.dis6.setText('Disponible')
        self.showMaximized()

    def cerrar_sesion(self):
        self.hide()
        self.inicio.showMaximized()

    def recibir_fotos(self, list):
        print('recibí las fotoooos!!!')
        self.lista_fotos = list
        self.recibidas = True

    def recibir_dicti_ocupados(self, dict):
        print('llegó dicti')
        self.diccio_ocupados = dict
        self.llego_dicti = True
        try:
            # Actualizamos todos los tags cada vez que alguien se mete o sale de alguno
            if self.diccio_ocupados[self.lista_fotos[0][0]]:
                self.dis1.setText('Ocupado')
            else:
                self.dis1.setText('Disponible')

            if self.diccio_ocupados[self.lista_fotos[1][0]]:
                self.dis2.setText('Ocupado')
            else:
                self.dis2.setText('Disponible')

            if self.diccio_ocupados[self.lista_fotos[2][0]]:
                self.dis3.setText('Ocupado')
            else:
                self.dis3.setText('Disponible')

            if self.diccio_ocupados[self.lista_fotos[3][0]]:
                self.dis4.setText('Ocupado')
            else:
                self.dis4.setText('Disponible')
            if self.diccio_ocupados[self.lista_fotos[4][0]]:
                self.dis5.setText('Ocupado')
            else:
                self.dis5.setText('Disponible')
            if self.diccio_ocupados[self.lista_fotos[5][0]]:
                self.dis6.setText('Ocupado')
            else:
                self.dis6.setText('Disponible')
        except:
            pass
            # A veces le llegan las fotos depués y tira error

    def editor1(self):
        if "Disponible" in self.dis1.text():
            self.hide()
            # Editor recibe (bytes_foto, el_cliente, nombre_foto, dashboard, nombre_usuario_entrando)
            self.editar = Editor(self.lista_fotos[0][1], self.cliente,
                                 self.lista_fotos[0][0], self,
                                 self.nombre_usuario, False)
            self.editar.showMaximized()
            # Le dice al cliente que la foto está ocupada
            self.cliente.marcar_ocupada(self.lista_fotos[0][0])
            self.dis1.setText('Ocupado')
        else:
            self.hide()
            self.editar = Editor(self.lista_fotos[0][1], self.cliente,
                                 self.lista_fotos[0][0], self,
                                 self.nombre_usuario, True)
            self.editar.showMaximized()
            # Le dice al cliente que la foto está ocupada
            self.cliente.marcar_ocupada(self.lista_fotos[0][0])

    def editor2(self):
        if "Disponible" in self.dis2.text():
            self.hide()
            self.editar = Editor(self.lista_fotos[1][1], self.cliente,
                                 self.lista_fotos[1][0], self,
                                 self.nombre_usuario, False)
            self.editar.showMaximized()
            # Le dice al cliente que la foto está ocupada
            self.cliente.marcar_ocupada(self.lista_fotos[1][0])
            self.dis2.setText('Ocupado')
        else:
            self.hide()
            self.editar = Editor(self.lista_fotos[1][1], self.cliente,
                                 self.lista_fotos[1][0], self,
                                 self.nombre_usuario, True)
            self.editar.showMaximized()
            # Le dice al cliente que la foto está ocupada
            self.cliente.marcar_ocupada(self.lista_fotos[1][0])

    def editor3(self):
        if "Disponible" in self.dis3.text():
            self.hide()
            self.editar = Editor(self.lista_fotos[2][1], self.cliente,
                                 self.lista_fotos[2][0], self,
                                 self.nombre_usuario, False)
            self.editar.showMaximized()
            # Le dice al cliente que la foto está ocupada
            self.cliente.marcar_ocupada(self.lista_fotos[2][0])
            self.dis3.setText('Ocupado')
        else:
            self.hide()
            self.editar = Editor(self.lista_fotos[2][1], self.cliente,
                                 self.lista_fotos[2][0], self,
                                 self.nombre_usuario, True)
            self.editar.showMaximized()
            # Le dice al cliente que la foto está ocupada
            self.cliente.marcar_ocupada(self.lista_fotos[2][0])

    def editor4(self):
        if "Disponible" in self.dis4.text():
            self.hide()
            self.editar = Editor(self.lista_fotos[3][1], self.cliente,
                                 self.lista_fotos[3][0], self,
                                 self.nombre_usuario, False)
            self.editar.showMaximized()
            # Le dice al cliente que la foto está ocupada
            self.cliente.marcar_ocupada(self.lista_fotos[3][0])
            self.dis4.setText('Ocupado')
        else:
            self.hide()
            self.editar = Editor(self.lista_fotos[3][1], self.cliente,
                                 self.lista_fotos[3][0], self,
                                 self.nombre_usuario, True)
            self.editar.showMaximized()
            # Le dice al cliente que la foto está ocupada
            self.cliente.marcar_ocupada(self.lista_fotos[3][0])

    def editor5(self):
        if "Disponible" in self.dis5.text():
            self.hide()
            self.editar = Editor(self.lista_fotos[4][1], self.cliente,
                                 self.lista_fotos[4][0], self,
                                 self.nombre_usuario, False)
            self.editar.showMaximized()
            # Le dice al cliente que la foto está ocupada
            self.cliente.marcar_ocupada(self.lista_fotos[4][0])
            self.dis5.setText('Ocupado')
        else:
            self.hide()
            self.editar = Editor(self.lista_fotos[4][1], self.cliente,
                                 self.lista_fotos[4][0], self,
                                 self.nombre_usuario, True)
            self.editar.showMaximized()
            # Le dice al cliente que la foto está ocupada
            self.cliente.marcar_ocupada(self.lista_fotos[4][0])

    def editor6(self):
        if "Disponible" in self.dis6.text():
            self.hide()
            self.editar = Editor(self.lista_fotos[5][1], self.cliente,
                                 self.lista_fotos[5][0], self,
                                 self.nombre_usuario, False)
            self.editar.showMaximized()
            # Le dice al cliente que la foto está ocupada
            self.cliente.marcar_ocupada(self.lista_fotos[5][0])
            self.dis6.setText('Ocupado')
        else:
            self.hide()
            self.editar = Editor(self.lista_fotos[5][1], self.cliente,
                                 self.lista_fotos[5][0], self,
                                 self.nombre_usuario, True)
            self.editar.showMaximized()
            # Le dice al cliente que la foto está ocupada
            self.cliente.marcar_ocupada(self.lista_fotos[5][0])

    def closeEvent(self, event):
        print('hice un close event')
        self.hide()

    def mostrar_conectados(self, event):
        print('me llegaron hasta los conectados y no me llega el dicti')
        conectados = event
        for i in reversed(range(self.UsuConect.count())):
            self.UsuConect.itemAt(i).widget().deleteLater()
        for i in conectados:
            self.label = QLabel(i)
            self.label.setStyleSheet("font-size:12pt; font-weight:600;")
            self.UsuConect.addWidget(self.label)
        self.UsuConect.setAlignment(Qt.AlignTop)


class Editor(edit[0], edit[1]):
    def __init__(self, imagen, cliente, nombre, dashbo, nombre_usuario,
                 espectador):
        super().__init__()
        # para volver a mostrar el dashboard
        self.dashbo = dashbo
        self.dashbo.hide()
        # imagen está en bytes
        self.imagen = imagen
        # el cliente
        self.cliente = cliente
        self.cliente.blurrytrigger.connect(self.blurry_remoto)
        self.cliente.comentrigger.connect(self.poner_comentarios_nuevos)
        self.cliente.recortatrigger.connect(self.recorte_remoto)
        # el nombre del archivo
        self.nombre = nombre
        # el nombre del usuario que está editando
        self.nombre_usuario = nombre_usuario
        # Nos dice con un True o False si esq es Espectador
        self.espectador = espectador

        self.setupUi(self)
        self.centralwidget.setObjectName('edit')
        self.centralwidget.setStyleSheet(
            "#edit {background-color: white; }")
        self.exit_button.clicked.connect(self.salir)

        self.foto.mousePressEvent = functools.partial(self.click,
                                                      source_object=self.foto)
        self.foto.mouseReleaseEvent = functools.partial(self.release,
                                                        source_object=self.foto)
        self.bytes_foto_ahora = imagen
        pix = QPixmap()
        pix.loadFromData(imagen)
        self.foto.setPixmap(pix.scaled(
            QSize(600, 600),
            aspectRatioMode=Qt.KeepAspectRatio))

        # Informarle al cliente que hay que hay alguien editando una foto
        if self.espectador == True:
            # Decirle al servidor que hay al menos 1 espectador, para los cambios en vivo
            self.cliente.add_espectador(self.nombre_usuario, self.nombre)

        self.atrevete.clicked.connect(self.agregar_comentario)
        self.download.clicked.connect(self.descargar_imagen)
        self.dash_boton.clicked.connect(self.volver)
        self.editando = Foto()
        self.matriz_rgb = self.editando.get_rgb(imagen)

        if self.espectador == False:
            self.Espectador.hide()
            # llama al modulo BackEnd para que le devuelva la matriz rgb
            self.blurry.clicked.connect(self.blurry_fe)
            self.recortar.clicked.connect(self.recortando)

        self.cliente.mandar_comentario("", self.nombre)

    def blurry_remoto(self):
        # Llama a una función en el BackEnd
        idat_blurry = self.editando.blurry_be(self.matriz_rgb)
        self.matriz_rgb = idat_blurry[1]
        idat_blurry = idat_blurry[0]
        self.bytes_foto_ahora = self.armar_foto(idat_blurry)
        # la volvemos a imprimir en el cliente
        pix = QPixmap()
        pix.loadFromData(self.bytes_foto_ahora)
        self.foto.setPixmap(pix.scaled(
            QSize(600, 600),
            aspectRatioMode=Qt.KeepAspectRatio))
        # Le avisamos al servidor que hicimos

    def recorte_remoto(self, tupla):
        self.bytes_foto_ahora = self.editando.recortar_be(
            self.bytes_foto_ahora, tupla[1], tupla[2], tupla[3])
        pix = QPixmap()
        pix.loadFromData(self.bytes_foto_ahora)
        self.foto.setPixmap(pix.scaled(
            QSize(600, 600),
            aspectRatioMode=Qt.KeepAspectRatio))

    def poner_comentarios_nuevos(self, list):
        print('te llegó la wea o no dog?')
        self.CajaComentarios.setHtml("\n".join(list))

    '''Esta función mostrará la imagen luego de aplicarle el efecto blurry 
    y además le dirá al cliente que le mande al servidor los cambios hechos,
     para que todos los que accedan a la applicación puedan ver los cambios'''

    def blurry_fe(self):
        # Llama a una función en el BackEnd
        idat_blurry = self.editando.blurry_be(self.matriz_rgb)
        self.matriz_rgb = idat_blurry[1]
        idat_blurry = idat_blurry[0]
        self.bytes_foto_ahora = self.armar_foto(idat_blurry)
        # la volvemos a imprimir en el cliente
        pix = QPixmap()
        pix.loadFromData(self.bytes_foto_ahora)
        self.foto.setPixmap(pix.scaled(
            QSize(600, 600),
            aspectRatioMode=Qt.KeepAspectRatio))
        # Le avisamos al servidor que hicimos
        if self.espectador == False:
            self.cliente.cambio_fotos(self.nombre, 'blurr')

    def descargar_imagen(self):
        with open(self.nombre, 'wb') as file:
            file.write(self.bytes_foto_ahora)

    def agregar_comentario(self):
        comentario = self.hace_comentarios.text()
        comentario = comentario.replace(':poop:',
                                        '<img src = Emojis/poop.png width="20" height="20">')
        comentario = comentario.replace('O:)',
                                        '<img src = Emojis/angel.png width="20" height="20">')
        comentario = comentario.replace(':D',
                                        '<img src = Emojis/happy.png width="20" height="20">')
        comentario = comentario.replace(';)',
                                        '<img src = Emojis/wink.png width="20" height="20">')
        comentario = comentario.replace('8)',
                                        '<img src = Emojis/cool.png width="20" height="20">')
        comentario = comentario.replace('U.U',
                                        '<img src = Emojis/cry.png width="20" height="20">')
        comentario = comentario.replace(':(',
                                        '<img src = Emojis/sad.png width="20" height="20">')
        comentario = comentario.replace('3:)',
                                        '<img src = Emojis/devil.png width="20" height="20">')
        comentario = comentario.replace('o.o',
                                        '<img src = Emojis/flushed.png width="20" height="20">')
        comentario = comentario.replace(':v',
                                        '<img src = Emojis/pacman.png width="20" height="20">')
        que = ('<html><h4 style="color:blue;">{a}</h4></html>'.format(
            a=self.nombre_usuario + ": \n"))
        que += '<html><h4>{a}</h4></html>'.format(a=comentario)

        self.CajaComentarios.append(que)
        # Hacer que el client le diga al servidor que todos lo vean!!!
        self.cliente.mandar_comentario(que, self.nombre)

    def volver(self):
        self.cliente.marcar_desocupada(self.nombre)
        self.dashbo.show()
        self.hide()
        if self.espectador:
            self.cliente.remove_espectador(self.nombre_usuario, self.nombre)

    def armar_foto(self, idat):
        bity = self.editando.rearmar_foto(idat)
        return bity

    def recortando(self):
        self.recortando = True

    def click(self, event, source_object=None):
        if self.recortando:
            self.primer_click = event.pos()
        print('click')
        print(event.pos())
        # Nombre del label
        print(source_object.objectName())

    def release(self, event, source_object=None):
        if self.recortando:
            self.soltar_click = event.pos()
            self.recortando = False
            self.bytes_foto_ahora = self.editando.recortar_be(
                self.bytes_foto_ahora, self.primer_click, self.soltar_click,
                self.foto.frameGeometry())
            pix = QPixmap()
            pix.loadFromData(self.bytes_foto_ahora)
            self.foto.setPixmap(pix.scaled(
                QSize(600, 600),
                aspectRatioMode=Qt.KeepAspectRatio))
            # Mandarle los cambios al servidor y que se los replique a todos los espectadores
            if self.espectador == False:
                self.cliente.cambio_fotos((self.nombre, self.primer_click,
                                           self.soltar_click,
                                           self.foto.frameGeometry()), 'recor')

        print('click')
        print(event.pos())
        # Nombre del label
        print(source_object.objectName())

    def salir(self):
        self.cliente.salir()
        self.hide()

    def closeEvent(self, event):
        self.cliente.salir()
        self.hide()


if __name__ == '__main__':
    app = QApplication([])
    form = Login()
    form.show()
    sys.exit(app.exec_())
