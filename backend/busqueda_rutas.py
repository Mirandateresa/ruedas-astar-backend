import json
import os
from nodo import Nodo  # Cambiado de "arbol" a "nodo"
from math import sin, cos, acos, radians
from functools import cmp_to_key

class BuscadorRutas:
    ARCHIVO_DATOS = 'datos_ciudades.json'
    
    def __init__(self):
        self.cargar_datos()
    
    def cargar_datos(self):
        """Carga los datos desde el archivo JSON"""
        if os.path.exists(self.ARCHIVO_DATOS):
            with open(self.ARCHIVO_DATOS, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                self.coord = datos.get('coordenadas', {})
                self.conexiones = datos.get('conexiones', {})
        else:
            # Datos por defecto si no existe el archivo
            self.coord = {
                'JILOYORK': [195708.7, 993159.3],
                'MORELOS': [18.92256998916627, -99.23495478216566],
                'CDMX': [19.43280876164703, -99.13334105118217],
                'HGO': [20.606315001876514, -99.24204926476969],
                'QRO': [20.593447100205406, -100.39005130695465],
                'SLP': [22.156055538736886, -100.96973806153706],
                'AGS': [21.886985868996973, -102.26257186191842],
                'SONORA': [19.43274978622343, -99.13337579180093],
                'MEXICALI': [32.62387398602895, -115.44288546017057],
                'MTY': [25.679620689238646, -100.32659620815436],
            }
            
            self.conexiones = {
                'JILOYORK': {'CDMX': 125, 'QRO': 513},
                'MORELOS': {'QRO': 425},
                'CDMX': {'JILOYORK': 125, 'QRO': 423, 'HGO': 491},
                'HGO': {'CDMX': 491, 'QRO': 351, 'MEXICALI': 309, 'MTY': 346},
                'QRO': {'SLP': 203, 'MORELOS': 514, 'JILOYORK': 513, 'CDMX': 423, 
                        'MTY': 603, 'SONORA': 437, 'HGO': 356, 'MEXICALI': 313, 'AGS': 599},
                'SLP': {'AGS': 390, 'QRO': 203},
                'AGS': {'SLP': 390, 'QRO': 599},
                'SONORA': {'QRO': 437, 'MEXICALI': 394},
                'MEXICALI': {'MTY': 296, 'HGO': 309, 'QRO': 313},
                'MTY': {'MEXICALI': 296, 'QRO': 603, 'HGO': 436}
            }
    
    def guardar_datos(self):
        """Guarda los datos en el archivo JSON"""
        datos = {
            'coordenadas': self.coord,
            'conexiones': self.conexiones
        }
        with open(self.ARCHIVO_DATOS, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
    
    def geodist(self, lat1, lon1, lat2, lon2):
        grad_rad = 0.01745329
        rad_grad = 57.29577951
        longitud = lon1 - lon2
        val = (sin(lat1 * grad_rad) * sin(lat2 * grad_rad)) \
            + (cos(lat1 * grad_rad) * cos(lat2 * grad_rad) * cos(longitud * grad_rad))
        return (acos(val) * rad_grad) * 111.32
    
    def compara(self, x, y, solucion):
        lat1 = self.coord[x.get_datos()][0]
        lon1 = self.coord[x.get_datos()][1]
        lat2 = self.coord[solucion][0]
        lon2 = self.coord[solucion][1]
        d = int(self.geodist(lat1, lon1, lat2, lon2))
        c1 = x.get_coste() + d
        
        lat1 = self.coord[y.get_datos()][0]
        lon1 = self.coord[y.get_datos()][1]
        lat2 = self.coord[solucion][0]
        lon2 = self.coord[solucion][1]
        d = int(self.geodist(lat1, lon1, lat2, lon2))
        c2 = y.get_coste() + d
        return c1 - c2
    
    def buscar_solucion(self, estado_inicial, solucion_buscar):
        solucionado = False
        nodos_visitados = []
        nodos_frontera = []
        nodo_inicial = Nodo(estado_inicial)
        nodo_inicial.set_coste(0)
        nodos_frontera.append(nodo_inicial)
        
        while not solucionado and len(nodos_frontera) != 0:
            nodos_frontera = sorted(nodos_frontera, 
                                  key=cmp_to_key(lambda x, y: self.compara(x, y, solucion_buscar)))
            nodo = nodos_frontera[0]
            nodos_visitados.append(nodos_frontera.pop(0))
            
            if nodo.get_datos() == solucion_buscar:
                solucionado = True
                return nodo
            else:
                dato_nodo = nodo.get_datos()
                if dato_nodo not in self.conexiones:
                    continue
                    
                lista_hijos = []
                for un_hijo in self.conexiones[dato_nodo]:
                    hijo = Nodo(un_hijo)
                    coste = self.conexiones[dato_nodo][un_hijo]
                    hijo.set_coste(nodo.get_coste() + coste)
                    hijo.set_padre(nodo)
                    lista_hijos.append(hijo)
                    
                    if not hijo.en_lista(nodos_visitados):
                        if hijo.en_lista(nodos_frontera):
                            for n in nodos_frontera:
                                if n.igual(hijo) and n.get_coste() > hijo.get_coste():
                                    nodos_frontera.remove(n)
                                    nodos_frontera.append(hijo)
                        else:
                            nodos_frontera.append(hijo)
                nodo.set_hijos(lista_hijos)
        
        return None
    
    def obtener_ruta(self, estado_inicial, estado_final):
        if estado_inicial not in self.coord:
            return {
                'exito': False,
                'mensaje': f'La ciudad "{estado_inicial}" no existe en el sistema'
            }
        if estado_final not in self.coord:
            return {
                'exito': False,
                'mensaje': f'La ciudad "{estado_final}" no existe en el sistema'
            }
            
        nodo_solucion = self.buscar_solucion(estado_inicial, estado_final)
        if nodo_solucion:
            resultado = []
            nodo = nodo_solucion
            while nodo.get_padre() is not None:
                resultado.append(nodo.get_datos())
                nodo = nodo.get_padre()
            resultado.append(estado_inicial)
            resultado.reverse()
            return {
                'ruta': resultado,
                'coste': nodo_solucion.get_coste(),
                'exito': True
            }
        return {
            'exito': False,
            'mensaje': 'No se encontró una ruta entre estas ciudades'
        }
    
    def obtener_ciudades(self):
        return list(self.coord.keys())
    
    def agregar_ciudad(self, nombre, latitud, longitud):
        if nombre in self.coord:
            return {'exito': False, 'mensaje': 'La ciudad ya existe'}
        
        self.coord[nombre] = [float(latitud), float(longitud)]
        self.conexiones[nombre] = {}
        self.guardar_datos()
        return {'exito': True, 'mensaje': 'Ciudad agregada correctamente'}
    
    def agregar_conexion(self, ciudad1, ciudad2, distancia):
        if ciudad1 not in self.coord or ciudad2 not in self.coord:
            return {'exito': False, 'mensaje': 'Una o ambas ciudades no existen'}
        
        distancia = float(distancia)
        self.conexiones[ciudad1][ciudad2] = distancia
        self.conexiones[ciudad2][ciudad1] = distancia
        self.guardar_datos()
        return {'exito': True, 'mensaje': 'Conexión agregada correctamente'}