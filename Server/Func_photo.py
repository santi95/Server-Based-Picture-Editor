from zlib import crc32, compress, decompress
import itertools
import array
import copy


class Foto:
    primero = False

    def get_rgb(self, foto):
        # foto es el nombre
        with open("image/{}".format(foto), 'rb') as file:
            b = file.read()

        self.standard = b[:8]
        b = b[8:]
        end = False
        self.dicti = {}
        # Lee todas las zonas de la imagen hasta que se acaba
        while not end:
            largo_chunki = b[:4]  # 0,0,0,13
            largo_chunk = int.from_bytes(largo_chunki, 'big')
            tipoi = b[4:8]
            tipo = tipoi.decode()
            info = b[8: 8 + largo_chunk]
            if tipo == 'IHDR':
                self.dicti['IHDR'] = (info, largo_chunki)
                self.ancho = int.from_bytes(info[:4], 'big')
                self.alto = int.from_bytes(info[4:8], 'big')
            elif tipo == 'IDAT':
                self.dicti['IDAT'] = (info, largo_chunki)
            elif tipo == 'IEND':
                self.iend = largo_chunki + tipoi + info
                end = True
            self.crc = b[8 + largo_chunk: 12 + largo_chunk]
            b = b[12 + largo_chunk:]

        # Prepara todo para la escritura de la matriz final
        self.matriz_rgb = decompress(self.dicti['IDAT'][0])
        self.rgbs = []
        self.matriz_final = []

        for i in range(self.alto):
            # Separamos en filas
            self.matriz_rgb = self.matriz_rgb[1:]
            fila = self.matriz_rgb[:self.ancho * 3]
            self.rgbs.append(fila)
            self.matriz_rgb = self.matriz_rgb[self.ancho * 3:]
            fila_separada = []
            for j in range(0, len(fila), 3):
                pixel = [fila[j], fila[j + 1], fila[j + 2]]
                fila_separada.append(pixel)
            self.matriz_final.append(fila_separada)
        # retorna la matriz final
        return self.matriz_final

    def blurry_be(self, rgbs):
        rgb_blurry = copy.deepcopy(rgbs)
        for i in range(len(rgbs)):
            for j in range(len(rgbs[i])):
                try:
                    suma_r = 2 * rgbs[i + 1][j][0] + 2 * rgbs[i - 1][j][
                        0] + 2 * rgbs[i][j + 1][0] + 2 * rgbs[i][j - 1][0]
                    suma_g = 2 * rgbs[i + 1][j][1] + 2 * rgbs[i - 1][j][
                        1] + 2 * rgbs[i][j + 1][1] + 2 * rgbs[i][j - 1][1]
                    suma_b = 2 * rgbs[i + 1][j][2] + 2 * rgbs[i - 1][j][
                        2] + 2 * rgbs[i][j + 1][2] + 2 * rgbs[i][j - 1][2]
                    suma_r += rgbs[i + 1][j + 1][0] + rgbs[i - 1][j + 1][0] + \
                              rgbs[i + 1][j - 1][0] + rgbs[i - 1][j - 1][0]
                    suma_g += rgbs[i + 1][j + 1][1] + rgbs[i - 1][j + 1][1] + \
                              rgbs[i + 1][j - 1][1] + rgbs[i - 1][j - 1][1]
                    suma_b += rgbs[i + 1][j + 1][2] + rgbs[i - 1][j + 1][2] + \
                              rgbs[i + 1][j - 1][2] + rgbs[i - 1][j - 1][2]
                    suma_r += rgbs[i][j][0] * 4
                    suma_g += rgbs[i][j][1] * 4
                    suma_b += rgbs[i][j][2] * 4
                    rgb_blurry[i][j] = [round(suma_r / 16), round(suma_g / 16),
                                        round(suma_b / 16)]
                except:
                    pass

        vacio = bytearray()
        for i in range(len(rgb_blurry)):
            fila = [0]
            for j in range(len(rgb_blurry[i])):
                fila.extend(rgb_blurry[i][j])
            filas = bytearray(fila)
            vacio.extend(filas)
        # imagen1 es el idat comprimido
        imagen1 = compress(vacio, 9)
        print('terminé')
        return (imagen1, rgb_blurry)

    def rearmar_foto(self, idat):
        standard = self.standard
        bytes_ihdr = self.dicti['IHDR'][0]
        largo_ihdr = self.dicti['IHDR'][1]
        ihdr = 'IHDR'.encode('ascii')
        crc1 = (crc32(ihdr + bytes_ihdr)).to_bytes(4, byteorder='big')
        bytes_idat = idat
        largo_idat = len(bytes_idat).to_bytes(4, byteorder='big')
        idat1 = 'IDAT'.encode('ascii')
        crc2 = (crc32(idat1 + bytes_idat)).to_bytes(4, byteorder='big')
        iend = self.iend
        foto = standard + largo_ihdr + ihdr + bytes_ihdr + crc1 + largo_idat + idat1 + bytes_idat + crc2 + iend
        return foto

    def hacer_blurry(self, nombre_foto):
        matriz = self.get_rgb(nombre_foto)
        tupla = self.blurry_be(matriz)
        bytes_final = self.rearmar_foto(tupla[0])
        with open("image/{}".format(nombre_foto), 'wb') as file:
            file.write(bytes_final)
        return ('termine')

    def recortar(self, datos):
        # (self.nombre, self.primer_click, self.soltar_click, self.foto.frameGeometry())
        matriz = self.get_rgb(datos[0])
        alto_label1 = datos[3].height()
        ancho_label1 = datos[3].width()
        alto_imagen = len(matriz)
        ancho_imagen = len(matriz[0])

        ratio = alto_imagen / alto_label1

        desde_x = min([datos[1].x(), datos[2].x()])
        hasta_x = max([datos[1].x(), datos[2].x()])
        desde_y = min([datos[1].y(), datos[2].y()])
        hasta_y = max([datos[1].y(), datos[2].y()])

        # Coordenadas escaladas a la matriz
        desde_x = round(desde_x * ratio)
        desde_y = round(desde_y * ratio)
        hasta_x = round(hasta_x * ratio)
        hasta_y = round(hasta_y * ratio)

        for i in range(desde_y, hasta_y):
            for j in range(desde_x, hasta_x):
                matriz[i][j] = [255, 255, 255]

        vacio = bytearray()
        for i in range(len(matriz)):
            fila = [0]
            for j in range(len(matriz[i])):
                fila.extend(matriz[i][j])
            filas = bytearray(fila)
            vacio.extend(filas)

        imagen1 = compress(vacio, 9)
        bytes_finales = self.rearmar_foto(imagen1)
        with open("image/" + datos[0], 'wb') as file:
            file.write(bytes_finales)
