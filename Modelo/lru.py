from Modelo.frame_page import Marcos, Pagina
from copy import deepcopy

class LRU:
    def __init__(self, cantidad_marcos):
        self.marcos = Marcos(cantidad_marcos, modelo='lru')
        self.tiempo = 0
        self.estados_marcos = []
        self.estados_uso = []

    def cargar_paginas(self, lista_paginas):
        paginas = [Pagina(num) for num in lista_paginas]
        self.marcos.encolar_paginas(paginas)

    def paso(self):
        pagina = self.marcos.obtener_pagina_actual()
        if pagina is None:
            return self.marcos.get_estado()
        # Verificar si la página ya está en los marcos
        en_marcos = False
        for p in self.marcos.marcos:
            if p and p.numero == pagina.numero:
                en_marcos = True
                p.last_used = self.tiempo
        if en_marcos:
            page_fault = False
        else:
            page_fault = True
            # Buscar marco vacío
            if None in self.marcos.marcos:
                idx = self.marcos.marcos.index(None)
                self.marcos.marcos[idx] = pagina
                pagina.last_used = self.tiempo
            else:
                # Reemplazar el menos recientemente usado
                idx_lru = self._indice_lru()
                self.marcos.marcos[idx_lru] = pagina
                pagina.last_used = self.tiempo
        self.marcos.historial_paginas.append(pagina)
        self.marcos.agregar_iteracion(page_fault)
        self.marcos.avanzar_pagina()
        self.tiempo += 1
        # Guardar el estado profundo de marcos y uso
        self.estados_marcos.append(deepcopy(self.marcos.marcos))
        self.estados_uso.append(self.tiempo)
        return self.marcos.get_estado()

    def _indice_lru(self):
        # Devuelve el índice del marco menos recientemente usado
        usos = [p.last_used if p else -1 for p in self.marcos.marcos]
        return usos.index(min(usos))

    def terminado(self):
        return not self.marcos.hay_pagina_por_decidir()

    def get_estado(self):
        return self.marcos.get_estado()

    def reiniciar(self, lista_paginas):
        self.marcos.reset()
        self.tiempo = 0
        self.estados_marcos = []
        self.estados_uso = []
        self.cargar_paginas(lista_paginas)

    def retroceder(self):
        if self.marcos.current_step > 0:
            self.marcos.current_step -= 1
            if len(self.marcos.matriz) > self.marcos.current_step + 1:
                self.marcos.matriz.pop()
            if len(self.marcos.page_faults) > self.marcos.current_step + 1:
                self.marcos.page_faults.pop()
            if len(self.marcos.historial_paginas) > self.marcos.current_step + 1:
                self.marcos.historial_paginas.pop()
            if self.marcos.proxima_pagina_idx > 0:
                self.marcos.proxima_pagina_idx -= 1
            # Restaurar el estado de los marcos y el tiempo al current_step
            if self.estados_marcos and self.estados_uso:
                self.marcos.marcos = deepcopy(self.estados_marcos[self.marcos.current_step])
                self.tiempo = self.estados_uso[self.marcos.current_step]
                self.estados_marcos = self.estados_marcos[:self.marcos.current_step+1]
                self.estados_uso = self.estados_uso[:self.marcos.current_step+1]
        return self.get_estado()
