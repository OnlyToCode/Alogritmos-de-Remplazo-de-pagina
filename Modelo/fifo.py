from Modelo.frame_page import Marcos, Pagina
from collections import deque
from copy import deepcopy

class FIFO:
    def __init__(self, cantidad_marcos):
        self.marcos = Marcos(cantidad_marcos, modelo='fifo')
        self.cola = deque()  # Para llevar el orden FIFO
        self.estados_marcos = []  # Guardar copia profunda de marcos en cada paso
        self.estados_cola = []    # Guardar copia profunda de la cola en cada paso

    def cargar_paginas(self, lista_paginas):
        paginas = [Pagina(num) for num in lista_paginas]
        self.marcos.encolar_paginas(paginas)

    def paso(self):
        """Realiza un paso de la simulación FIFO."""
        pagina = self.marcos.obtener_pagina_actual()
        if pagina is None:
            return self.marcos.get_estado()
        # Verificar si la página ya está en los marcos
        numeros_en_marcos = [p.numero if p else None for p in self.marcos.marcos]
        if pagina.numero in numeros_en_marcos:
            page_fault = False
        else:
            page_fault = True
            # Buscar marco vacío
            if None in self.marcos.marcos:
                idx = self.marcos.marcos.index(None)
                self.marcos.marcos[idx] = pagina
                self.cola.append(idx)
            else:
                # Reemplazar el más antiguo (FIFO)
                idx = self.cola.popleft()
                self.marcos.marcos[idx] = pagina
                self.cola.append(idx)
        self.marcos.historial_paginas.append(pagina)
        self.marcos.agregar_iteracion(page_fault)
        self.marcos.avanzar_pagina()
        # Guardar el estado profundo de marcos y cola
        self.estados_marcos.append(deepcopy(self.marcos.marcos))
        self.estados_cola.append(deepcopy(self.cola))
        return self.marcos.get_estado()

    def terminado(self):
        return not self.marcos.hay_pagina_por_decidir()

    def get_estado(self):
        return self.marcos.get_estado()

    def reiniciar(self, lista_paginas):
        self.marcos.reset()
        self.cola.clear()
        self.estados_marcos = []
        self.estados_cola = []
        self.cargar_paginas(lista_paginas)

    def retroceder(self):
        # Solo retrocede si hay al menos una iteración previa
        if self.marcos.current_step > 0:
            self.marcos.current_step -= 1
            # Elimina la última iteración de la matriz, page_faults e historial_paginas si están sincronizados
            if len(self.marcos.matriz) > self.marcos.current_step + 1:
                self.marcos.matriz.pop()
            if len(self.marcos.page_faults) > self.marcos.current_step + 1:
                self.marcos.page_faults.pop()
            if len(self.marcos.historial_paginas) > self.marcos.current_step + 1:
                self.marcos.historial_paginas.pop()
            if self.marcos.proxima_pagina_idx > 0:
                self.marcos.proxima_pagina_idx -= 1
            # Restaurar el estado de los marcos y la cola al current_step
            if self.estados_marcos and self.estados_cola:
                self.marcos.marcos = deepcopy(self.estados_marcos[self.marcos.current_step])
                self.cola = deepcopy(self.estados_cola[self.marcos.current_step])
                # Eliminar los estados futuros
                self.estados_marcos = self.estados_marcos[:self.marcos.current_step+1]
                self.estados_cola = self.estados_cola[:self.marcos.current_step+1]
        return self.get_estado()
