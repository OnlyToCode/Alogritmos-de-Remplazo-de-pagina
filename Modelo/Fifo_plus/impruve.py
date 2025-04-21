from Modelo.frame_page import Marcos, Pagina
from collections import deque
from copy import deepcopy

class Impruve:
    def __init__(self, cantidad_marcos):
        self.marcos = Marcos(cantidad_marcos, modelo='impruve')
        self.cola = deque()  # Para el orden FIFO
        self.estados_marcos = []
        self.estados_proteccion = []

    def cargar_paginas(self, lista_paginas):
        paginas = [Pagina(num) for num in lista_paginas]
        self.marcos.encolar_paginas(paginas)

    def paso(self):
        pagina = self.marcos.obtener_pagina_actual()
        if pagina is None:
            return self.get_estado()
        en_marcos = False
        for idx, p in enumerate(self.marcos.marcos):
            if p and p.numero == pagina.numero:
                en_marcos = True
                # Quitar protección a todos
                for q in self.marcos.marcos:
                    if q:
                        q.bit_proteccion = False
                # Dar protección solo a esta página
                p.bit_proteccion = True
        if en_marcos:
            page_fault = False
        else:
            page_fault = True
            if None in self.marcos.marcos:
                idx = self.marcos.marcos.index(None)
                self.marcos.marcos[idx] = pagina
                pagina.bit_proteccion = False
                self.cola.append(idx)
            else:
                # FIFO Mejorado: si el más viejo tiene protección, se la quita y reemplaza al segundo más viejo
                idx_viejo = self.cola[0]
                p_viejo = self.marcos.marcos[idx_viejo]
                if p_viejo.bit_proteccion:
                    p_viejo.bit_proteccion = False
                    # Reemplazar al segundo más viejo
                    if len(self.cola) > 1:
                        idx_segundo = self.cola[1]
                        self.marcos.marcos[idx_segundo] = pagina
                        pagina.bit_proteccion = False
                        self.cola.remove(idx_segundo)
                        self.cola.append(idx_segundo)
                    else:
                        # Solo hay un marco, reemplazar el mismo
                        self.marcos.marcos[idx_viejo] = pagina
                        pagina.bit_proteccion = False
                        self.cola.popleft()
                        self.cola.append(idx_viejo)
                else:
                    # Si el más viejo no tiene protección, reemplazarlo
                    self.marcos.marcos[idx_viejo] = pagina
                    pagina.bit_proteccion = False
                    self.cola.popleft()
                    self.cola.append(idx_viejo)
        self.marcos.historial_paginas.append(pagina)
        self.marcos.agregar_iteracion(page_fault)
        self.marcos.avanzar_pagina()
        self.estados_marcos.append(deepcopy(self.marcos.marcos))
        self.estados_proteccion.append([p.bit_proteccion if p else False for p in self.marcos.marcos])
        return self.get_estado()

    def terminado(self):
        return not self.marcos.hay_pagina_por_decidir()

    def get_estado(self):
        estado = self.marcos.get_estado()
        if not self.estados_proteccion:
            estado['bits_proteccion'] = [[False for _ in range(self.marcos.cantidad)]]
        else:
            estado['bits_proteccion'] = self.estados_proteccion.copy()
        return estado

    def reiniciar(self, lista_paginas):
        self.marcos.reset()
        self.cola.clear()
        self.estados_marcos = []
        self.estados_proteccion = []
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
            if self.estados_marcos and self.estados_proteccion:
                self.marcos.marcos = deepcopy(self.estados_marcos[self.marcos.current_step])
                for i, p in enumerate(self.marcos.marcos):
                    if p:
                        p.bit_proteccion = self.estados_proteccion[self.marcos.current_step][i]
                self.estados_marcos = self.estados_marcos[:self.marcos.current_step+1]
                self.estados_proteccion = self.estados_proteccion[:self.marcos.current_step+1]
        return self.get_estado()
