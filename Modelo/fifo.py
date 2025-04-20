from Modelo.frame_page import Marcos, Pagina
from collections import deque

class FIFO:
    def __init__(self, cantidad_marcos):
        self.marcos = Marcos(cantidad_marcos, modelo='fifo')
        self.cola = deque()  # Para llevar el orden FIFO

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
        return self.marcos.get_estado()

    def terminado(self):
        return not self.marcos.hay_pagina_por_decidir()

    def get_estado(self):
        return self.marcos.get_estado()

    def reiniciar(self, lista_paginas):
        self.marcos.reset()
        self.cola.clear()
        self.cargar_paginas(lista_paginas)
