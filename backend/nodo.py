class Nodo:
    def __init__(self, datos, padre=None):
        self.datos = datos
        self.padre = padre
        self.coste = 0
        self.heuristica = 0  # Para almacenar h(n)
        self.hijos = []
    
    def set_coste(self, coste):
        self.coste = coste
    
    def get_coste(self):
        return self.coste
    
    def set_heuristica(self, heuristica):
        self.heuristica = heuristica
    
    def get_heuristica(self):
        return self.heuristica
    
    def set_padre(self, padre):
        self.padre = padre
    
    def get_padre(self):
        return self.padre
    
    def get_datos(self):
        return self.datos
    
    def set_hijos(self, hijos):
        self.hijos = hijos
    
    def get_hijos(self):
        return self.hijos
    
    def igual(self, nodo):
        return self.datos == nodo.get_datos()
    
    def en_lista(self, lista_nodos):
        for n in lista_nodos:
            if self.igual(n):
                return True
        return False