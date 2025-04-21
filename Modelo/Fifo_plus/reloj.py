from Modelo.frame_page import Marcos, Pagina
from copy import deepcopy

class Reloj:
    def __init__(self, cantidad_marcos):
        self.marcos = Marcos(cantidad_marcos, modelo='reloj')
        self.puntero = 0
        self.estados_marcos = []
        self.estados_bits = []
        self.estados_puntero = []

    def cargar_paginas(self, lista_paginas):
        paginas = [Pagina(num) for num in lista_paginas]
        self.marcos.encolar_paginas(paginas)

    def paso(self):
        pagina = self.marcos.obtener_pagina_actual()
        if pagina is None:
            return self.get_estado()
        # Verificar si la página ya está en los marcos
        en_marcos = False
        for p in self.marcos.marcos:
            if p and p.numero == pagina.numero:
                en_marcos = True
                p.bit_uso = True
        if en_marcos:
            page_fault = False
        else:
            page_fault = True
            while True:
                actual = self.marcos.marcos[self.puntero]
                if actual is None:
                    self.marcos.marcos[self.puntero] = pagina
                    pagina.bit_uso = True
                    self.puntero = (self.puntero + 1) % self.marcos.cantidad
                    break
                elif actual.bit_uso:
                    actual.bit_uso = False
                    self.puntero = (self.puntero + 1) % self.marcos.cantidad
                else:
                    self.marcos.marcos[self.puntero] = pagina
                    pagina.bit_uso = True
                    self.puntero = (self.puntero + 1) % self.marcos.cantidad
                    break
        self.marcos.historial_paginas.append(pagina)
        self.marcos.agregar_iteracion(page_fault)
        self.marcos.avanzar_pagina()
        # Guardar el estado profundo de marcos, bits y puntero
        self.estados_marcos.append(deepcopy(self.marcos.marcos))
        self.estados_bits.append([p.bit_uso if p else False for p in self.marcos.marcos])
        self.estados_puntero.append(self.puntero)
        return self.get_estado()

    def terminado(self):
        return not self.marcos.hay_pagina_por_decidir()

    def get_estado(self):
        estado = self.marcos.get_estado()
        # Si no hay historial, inicializa bits_uso y punteros con valores por defecto para mostrar placeholder
        if not self.estados_bits:
            estado['bits_uso'] = [[False for _ in range(self.marcos.cantidad)]]
        else:
            estado['bits_uso'] = self.estados_bits.copy()
        if hasattr(self, 'estados_puntero'):
            if not self.estados_puntero:
                estado['punteros'] = [0]
            else:
                estado['punteros'] = self.estados_puntero.copy()
        return estado

    def reiniciar(self, lista_paginas):
        self.marcos.reset()
        self.puntero = 0
        self.estados_marcos = []
        self.estados_bits = []
        self.estados_puntero = []
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
            # Restaurar el estado de los marcos, bits y puntero al current_step
            if self.estados_marcos and self.estados_bits and self.estados_puntero:
                self.marcos.marcos = deepcopy(self.estados_marcos[self.marcos.current_step])
                for i, p in enumerate(self.marcos.marcos):
                    if p:
                        p.bit_uso = self.estados_bits[self.marcos.current_step][i]
                self.puntero = self.estados_puntero[self.marcos.current_step]
                self.estados_marcos = self.estados_marcos[:self.marcos.current_step+1]
                self.estados_bits = self.estados_bits[:self.marcos.current_step+1]
                self.estados_puntero = self.estados_puntero[:self.marcos.current_step+1]
        return self.get_estado()
