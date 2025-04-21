from Modelo.frame_page import Marcos, Pagina
from Modelo.fifo import FIFO
from Modelo.lru import LRU
from Modelo.optimo import Optimo
import random

class GeneradorPaginas:
    def __init__(self, minimo=0, maximo=9):
        self.minimo = minimo
        self.maximo = maximo

    def generar(self, cantidad):
        for _ in range(cantidad):
            yield random.randint(self.minimo, self.maximo)

class Controller:
    def __init__(self):
        self.marcos = None
        self.last_state = None
        self.fifo = None
        self.lru = None
        self.optimo = None
        self.algoritmo = None

    def observer_callback(self, estado):
        self.last_state = estado

    def crear_simulacion(self, cantidad_marcos, modelo, lista_paginas):
        if modelo == 'fifo':
            self.fifo = FIFO(cantidad_marcos)
            self.fifo.cargar_paginas(lista_paginas)
            self.algoritmo = 'fifo'
            return self.fifo.get_estado()
        if modelo == 'lru':
            self.lru = LRU(cantidad_marcos)
            self.lru.cargar_paginas(lista_paginas)
            self.algoritmo = 'lru'
            return self.lru.get_estado()
        if modelo == 'optimo':
            self.optimo = Optimo(cantidad_marcos)
            self.optimo.cargar_paginas(lista_paginas)
            self.algoritmo = 'optimo'
            return self.optimo.get_estado()
        # ...otros algoritmos...
        # fallback legacy:
        self.marcos = Marcos(cantidad=cantidad_marcos, modelo=modelo)
        self.marcos.add_observer(self.observer_callback)
        paginas = [Pagina(num) for num in lista_paginas]
        self.marcos.encolar_paginas(paginas)
        return self.get_estado()

    def avanzar(self):
        if self.algoritmo == 'fifo' and self.fifo:
            return self.fifo.paso()
        if self.algoritmo == 'lru' and self.lru:
            return self.lru.paso()
        if self.algoritmo == 'optimo' and self.optimo:
            return self.optimo.paso()
        # ...otros algoritmos...
        if self.marcos and self.marcos.hay_pagina_por_decidir():
            self.marcos.recibir_pagina(self.marcos.obtener_pagina_actual())
            self.marcos.recibir_pagina()  # Ejecuta transición a 'decidiendo'
            self.marcos.decidir()         # Ejecuta transición a 'actualizando'
            self.marcos.esperar()         # Ejecuta transición a 'en_espera'
        return self.get_estado()

    def retroceder(self):
        if self.algoritmo == 'fifo' and self.fifo:
            return self.fifo.retroceder()
        if self.algoritmo == 'lru' and self.lru:
            return self.lru.retroceder()
        if self.algoritmo == 'optimo' and self.optimo:
            return self.optimo.retroceder()
        if self.marcos and self.marcos.current_step > 0:
            self.marcos.current_step -= 1
        return self.get_estado()

    def reiniciar(self):
        if self.algoritmo == 'fifo' and self.fifo:
            paginas = [p.numero for p in self.fifo.marcos.historial_paginas]
            self.fifo.reiniciar(paginas)
            return self.fifo.get_estado()
        if self.algoritmo == 'lru' and self.lru:
            paginas = [p.numero for p in self.lru.marcos.historial_paginas]
            self.lru.reiniciar(paginas)
            return self.lru.get_estado()
        if self.algoritmo == 'optimo' and self.optimo:
            paginas = [p.numero for p in self.optimo.marcos.historial_paginas]
            self.optimo.reiniciar(paginas)
            return self.optimo.get_estado()
        if self.marcos:
            modelo = self.marcos.modelo
            cantidad = self.marcos.cantidad
            paginas = [p.numero for p in self.marcos.historial_paginas]
            self.crear_simulacion(cantidad, modelo, paginas)
        return self.get_estado()

    def get_estado(self):
        if self.algoritmo == 'fifo' and self.fifo:
            return self.fifo.get_estado()
        if self.algoritmo == 'lru' and self.lru:
            return self.lru.get_estado()
        if self.algoritmo == 'optimo' and self.optimo:
            return self.optimo.get_estado()
        if self.marcos:
            return {
                "marcos": self.marcos.matriz,
                "historial_paginas": [p.numero for p in self.marcos.historial_paginas],
                "page_faults": self.marcos.page_faults,
                "estado_maquina": self.marcos.state,
                "proxima_pagina": self.marcos.obtener_pagina_actual().numero if self.marcos.obtener_pagina_actual() else None,
                "current_step": self.marcos.current_step
            }
        return {"error": "No hay simulación activa."}
