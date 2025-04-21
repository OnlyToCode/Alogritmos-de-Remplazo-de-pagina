from Modelo.frame_page import Marcos, Pagina
from collections import deque
from copy import deepcopy

class SecondOpportunity:
    def __init__(self, cantidad_marcos):
        self.marcos = Marcos(cantidad_marcos, modelo='second_opportunity')
        self.cola = deque()  # Para el orden de los marcos
        self.estados_marcos = []
        self.estados_bits = []

    def cargar_paginas(self, lista_paginas):
        paginas = [Pagina(num) for num in lista_paginas]
        self.marcos.encolar_paginas(paginas)

    def paso(self):
        pagina = self.marcos.obtener_pagina_actual()
        if pagina is None:
            return self.marcos.get_estado()
        # Verificar si la página ya está en los marcos
        en_marcos = False
        for idx, p in enumerate(self.marcos.marcos):
            if p and p.numero == pagina.numero:
                en_marcos = True
                p.bit_uso = True  # Da segunda oportunidad
        if en_marcos:
            page_fault = False
        else:
            page_fault = True
            # Buscar marco vacío
            if None in self.marcos.marcos:
                idx = self.marcos.marcos.index(None)
                self.marcos.marcos[idx] = pagina
                pagina.bit_uso = True
                self.cola.append(idx)
            else:
                while True:
                    idx = self.cola[0]
                    p = self.marcos.marcos[idx]
                    if p.bit_uso:
                        p.bit_uso = False  # Segunda oportunidad: limpia el bit y mueve al final
                        self.cola.rotate(-1)
                    else:
                        self.marcos.marcos[idx] = pagina
                        pagina.bit_uso = True
                        self.cola.popleft()
                        self.cola.append(idx)
                        break
        self.marcos.historial_paginas.append(pagina)
        self.marcos.agregar_iteracion(page_fault)
        self.marcos.avanzar_pagina()
        # Guardar el estado profundo de marcos y bits
        self.estados_marcos.append(deepcopy(self.marcos.marcos))
        self.estados_bits.append([p.bit_uso if p else False for p in self.marcos.marcos])
        return self.marcos.get_estado()

    def terminado(self):
        return not self.marcos.hay_pagina_por_decidir()

    def get_estado(self):
        estado = self.marcos.get_estado()
        # Si no hay historial, inicializa bits_uso con valores por defecto para mostrar placeholder
        if not self.estados_bits:
            estado['bits_uso'] = [[False for _ in range(self.marcos.cantidad)]]
        else:
            estado['bits_uso'] = self.estados_bits.copy()
        return estado

    def reiniciar(self, lista_paginas):
        self.marcos.reset()
        self.cola.clear()
        self.estados_marcos = []
        self.estados_bits = []
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
            # Restaurar el estado de los marcos y los bits al current_step
            if self.estados_marcos and self.estados_bits:
                self.marcos.marcos = deepcopy(self.estados_marcos[self.marcos.current_step])
                for i, p in enumerate(self.marcos.marcos):
                    if p:
                        p.bit_uso = self.estados_bits[self.marcos.current_step][i]
                self.estados_marcos = self.estados_marcos[:self.marcos.current_step+1]
                self.estados_bits = self.estados_bits[:self.marcos.current_step+1]
        return self.get_estado()
