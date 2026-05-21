from nodo import Nodo

class ProblemaRuedas:
    def __init__(self):
        # Matriz de precios: empresas(1-4) vs tipos(T,H,V,W)
        self.precios = {
            'T': [20, 50, 60, 100],  # precios por empresa para tipo T
            'H': [30, 50, 55, 80],   # precios por empresa para tipo H
            'V': [20, 40, 50, 60],   # precios por empresa para tipo V
            'W': [40, 50, 60, 70]    # precios por empresa para tipo W
        }
        self.tipos_rueda = ['T', 'H', 'V', 'W']
        self.empresas = [0, 1, 2, 3]  # 0=Empresa1, 1=Empresa2, 2=Empresa3, 3=Empresa4
        self.nombres_empresas = ['Empresa 1', 'Empresa 2', 'Empresa 3', 'Empresa 4']
    
    def es_objetivo(self, estado):
        """Verifica si todos los tipos de rueda han sido asignados"""
        return len(estado) == 4
    
    def heuristica_admisible(self, estado):
        """
        Calcula h(n): suma de los precios mínimos para los tipos no asignados,
        considerando solo empresas no utilizadas.
        Esta heurística es ADMISIBLE porque nunca sobrestima el costo real.
        """
        tipos_asignados = set(estado.keys())
        empresas_usadas = set(estado.values())
        
        # Tipos de rueda aún no asignados
        tipos_pendientes = [t for t in self.tipos_rueda if t not in tipos_asignados]
        empresas_disponibles = [e for e in self.empresas if e not in empresas_usadas]
        
        if not tipos_pendientes:
            return 0
        
        # Para cada tipo pendiente, tomar el precio mínimo entre empresas disponibles
        heuristica_total = 0
        for tipo in tipos_pendientes:
            precios_tipo = self.precios[tipo]
            if empresas_disponibles:
                min_precio = min([precios_tipo[e] for e in empresas_disponibles])
                heuristica_total += min_precio
        
        return heuristica_total
    
    def costo_real(self, tipo, empresa):
        """Devuelve el costo real de asignar un tipo a una empresa"""
        return self.precios[tipo][empresa]
    
    def generar_hijos(self, estado_actual):
        """Genera todos los estados hijos posibles"""
        hijos = []
        tipos_asignados = set(estado_actual.keys())
        empresas_usadas = set(estado_actual.values())
        
        # Tipos de rueda aún no asignados
        tipos_pendientes = [t for t in self.tipos_rueda if t not in tipos_asignados]
        
        if not tipos_pendientes:
            return hijos
        
        # Para el siguiente tipo a asignar (orden fijo para consistencia)
        siguiente_tipo = tipos_pendientes[0]
        
        # Probar asignar a cada empresa disponible
        for empresa in self.empresas:
            if empresa not in empresas_usadas:
                nuevo_estado = estado_actual.copy()
                nuevo_estado[siguiente_tipo] = empresa
                hijos.append(nuevo_estado)
        
        return hijos
    
    def buscar_a_estrella(self):
        """Implementación del algoritmo A* para el problema de ruedas"""
        estado_inicial = {}
        nodo_inicial = Nodo(estado_inicial)
        nodo_inicial.set_coste(0)
        nodo_inicial.set_heuristica(self.heuristica_admisible(estado_inicial))
        
        nodos_frontera = [nodo_inicial]
        nodos_visitados = []
        solucionado = False
        nodo_solucion = None
        
        while not solucionado and len(nodos_frontera) > 0:
            # Ordenar frontera por f(n) = g(n) + h(n)
            nodos_frontera.sort(key=lambda x: x.get_coste() + x.get_heuristica())
            nodo_actual = nodos_frontera.pop(0)
            
            if self.es_objetivo(nodo_actual.get_datos()):
                solucionado = True
                nodo_solucion = nodo_actual
                break
            
            nodos_visitados.append(nodo_actual)
            hijos_estados = self.generar_hijos(nodo_actual.get_datos())
            
            for hijo_estado in hijos_estados:
                # Encontrar el nuevo tipo asignado
                nuevo_tipo = list(set(hijo_estado.keys()) - set(nodo_actual.get_datos().keys()))[0]
                nueva_empresa = hijo_estado[nuevo_tipo]
                costo_asignacion = self.costo_real(nuevo_tipo, nueva_empresa)
                g_hijo = nodo_actual.get_coste() + costo_asignacion
                h_hijo = self.heuristica_admisible(hijo_estado)
                
                hijo_nodo = Nodo(hijo_estado)
                hijo_nodo.set_coste(g_hijo)
                hijo_nodo.set_heuristica(h_hijo)
                hijo_nodo.set_padre(nodo_actual)
                
                # Verificar si ya está en visitados
                if hijo_nodo.en_lista(nodos_visitados):
                    continue
                
                # Si está en frontera con mayor costo, reemplazar
                encontrado = False
                for i, n in enumerate(nodos_frontera):
                    if n.igual(hijo_nodo):
                        encontrado = True
                        if n.get_coste() + n.get_heuristica() > hijo_nodo.get_coste() + hijo_nodo.get_heuristica():
                            nodos_frontera[i] = hijo_nodo
                        break
                
                if not encontrado:
                    nodos_frontera.append(hijo_nodo)
        
        return nodo_solucion
    
    def obtener_solucion(self):
        """Ejecuta A* y devuelve la solución formateada"""
        nodo_solucion = self.buscar_a_estrella()
        
        if nodo_solucion is None:
            return None
        
        # Reconstruir el camino
        camino = []
        nodo = nodo_solucion
        while nodo is not None:
            camino.insert(0, nodo.get_datos())
            nodo = nodo.get_padre()
        
        # Convertir a formato legible
        asignaciones = []
        for estado in camino:
            asignacion_legible = {}
            for tipo, empresa in estado.items():
                asignacion_legible[tipo] = self.nombres_empresas[empresa]
            asignaciones.append(asignacion_legible)
        
        # Calcular costo total final
        costo_total = nodo_solucion.get_coste()
        
        return {
            'asignaciones': asignaciones,
            'costo_total': costo_total,
            'detalle': self._obtener_detalle(nodo_solucion.get_datos()),
            'heuristica_explicacion': self._explicar_heuristica()
        }
    
    def _obtener_detalle(self, estado):
        """Obtiene el detalle de cada asignación"""
        detalle = []
        for tipo, empresa in estado.items():
            costo = self.costo_real(tipo, empresa)
            detalle.append({
                'tipo': tipo,
                'empresa': self.nombres_empresas[empresa],
                'costo': costo
            })
        return detalle
    
    def _explicar_heuristica(self):
        """Explica por qué la heurística es admisible"""
        return {
            'titulo': 'Heurística Admisible',
            'descripcion': 'h(n) = suma de precios mínimos de tipos pendientes considerando solo empresas disponibles',
            'razon': 'Esta heurística NUNCA sobrestima el costo real porque toma el mínimo precio posible para cada tipo pendiente, lo cual es siempre menor o igual al costo real que se obtendrá.',
            'ejemplo': 'Si solo queda asignar tipo V y W con empresas 3 y 4, h(n) = min(precio V empresas 3,4) + min(precio W empresas 3,4)'
        }