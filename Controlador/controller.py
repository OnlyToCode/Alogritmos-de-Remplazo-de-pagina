from Modelo.frame_page import Marcos, Pagina
from Modelo.fifo import FIFO
from Modelo.lru import LRU
from Modelo.optimo import Optimo
from Modelo.Fifo_plus.second_opportunity import SecondOpportunity
from Modelo.Fifo_plus.reloj import Reloj
from Modelo.Fifo_plus.impruve import Impruve
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
        self.second_opportunity = None
        self.reloj = None
        self.impruve = None
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
        if modelo == 'second_opportunity':
            self.second_opportunity = SecondOpportunity(cantidad_marcos)
            self.second_opportunity.cargar_paginas(lista_paginas)
            self.algoritmo = 'second_opportunity'
            return self.second_opportunity.get_estado()
        if modelo == 'reloj':
            self.reloj = Reloj(cantidad_marcos)
            self.reloj.cargar_paginas(lista_paginas)
            self.algoritmo = 'reloj'
            return self.reloj.get_estado()
        if modelo == 'fifo_plus':
            self.impruve = Impruve(cantidad_marcos)
            self.impruve.cargar_paginas(lista_paginas)
            self.algoritmo = 'fifo_plus'
            return self.impruve.get_estado()
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
        if self.algoritmo == 'second_opportunity' and self.second_opportunity:
            return self.second_opportunity.paso()
        if self.algoritmo == 'reloj' and self.reloj:
            return self.reloj.paso()
        if self.algoritmo == 'fifo_plus' and self.impruve:
            return self.impruve.paso()
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
        if self.algoritmo == 'second_opportunity' and self.second_opportunity:
            return self.second_opportunity.retroceder()
        if self.algoritmo == 'reloj' and self.reloj:
            return self.reloj.retroceder()
        if self.algoritmo == 'fifo_plus' and self.impruve:
            return self.impruve.retroceder()
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
        if self.algoritmo == 'second_opportunity' and self.second_opportunity:
            paginas = [p.numero for p in self.second_opportunity.marcos.historial_paginas]
            self.second_opportunity.reiniciar(paginas)
            return self.second_opportunity.get_estado()
        if self.algoritmo == 'reloj' and self.reloj:
            paginas = [p.numero for p in self.reloj.marcos.historial_paginas]
            self.reloj.reiniciar(paginas)
            return self.reloj.get_estado()
        if self.algoritmo == 'fifo_plus' and self.impruve:
            paginas = [p.numero for p in self.impruve.marcos.historial_paginas]
            self.impruve.reiniciar(paginas)
            return self.impruve.get_estado()
        if self.marcos:
            modelo = self.marcos.modelo
            cantidad = self.marcos.cantidad
            paginas = [p.numero for p in self.marcos.historial_paginas]
            self.crear_simulacion(cantidad, modelo, paginas)
        return self.get_estado()

    def comparar_algoritmos(self, cantidad_marcos, lista_paginas):
        # Ejecuta todos los algoritmos y retorna una lista ordenada por errores (óptimo primero)
        resultados = []
        # Óptimo
        opt = Optimo(cantidad_marcos)
        opt.cargar_paginas(lista_paginas)
        while not opt.terminado():
            opt.paso()
        fallos_opt = sum(opt.marcos.page_faults)
        resultados.append({'nombre': 'Óptimo', 'fallos': fallos_opt, 'diferencia': 0})
        # FIFO
        fifo = FIFO(cantidad_marcos)
        fifo.cargar_paginas(lista_paginas)
        while not fifo.terminado():
            fifo.paso()
        fallos_fifo = sum(fifo.marcos.page_faults)
        resultados.append({'nombre': 'FIFO', 'fallos': fallos_fifo, 'diferencia': fallos_fifo - fallos_opt})
        # LRU
        lru = LRU(cantidad_marcos)
        lru.cargar_paginas(lista_paginas)
        while not lru.terminado():
            lru.paso()
        fallos_lru = sum(lru.marcos.page_faults)
        resultados.append({'nombre': 'LRU', 'fallos': fallos_lru, 'diferencia': fallos_lru - fallos_opt})
        # FIFO Mejorado
        impruve = Impruve(cantidad_marcos)
        impruve.cargar_paginas(lista_paginas)
        while not impruve.terminado():
            impruve.paso()
        fallos_impruve = sum(impruve.marcos.page_faults)
        resultados.append({'nombre': 'FIFO Mejorado', 'fallos': fallos_impruve, 'diferencia': fallos_impruve - fallos_opt})
        # Segunda Oportunidad
        so = SecondOpportunity(cantidad_marcos)
        so.cargar_paginas(lista_paginas)
        while not so.terminado():
            so.paso()
        fallos_so = sum(so.marcos.page_faults)
        resultados.append({'nombre': 'Segunda Oportunidad', 'fallos': fallos_so, 'diferencia': fallos_so - fallos_opt})
        # Reloj
        reloj = Reloj(cantidad_marcos)
        reloj.cargar_paginas(lista_paginas)
        while not reloj.terminado():
            reloj.paso()
        fallos_reloj = sum(reloj.marcos.page_faults)
        resultados.append({'nombre': 'Reloj', 'fallos': fallos_reloj, 'diferencia': fallos_reloj - fallos_opt})
        # Ordenar: óptimo primero, luego por fallos ascendente
        resultados = sorted(resultados, key=lambda x: (x['diferencia'], x['nombre'] != 'Óptimo'))
        return resultados

    def get_estado(self):
        estado = None
        if self.algoritmo == 'fifo' and self.fifo:
            estado = self.fifo.get_estado()
        elif self.algoritmo == 'lru' and self.lru:
            estado = self.lru.get_estado()
        elif self.algoritmo == 'optimo' and self.optimo:
            estado = self.optimo.get_estado()
        elif self.algoritmo == 'second_opportunity' and self.second_opportunity:
            estado = self.second_opportunity.get_estado()
        elif self.algoritmo == 'reloj' and self.reloj:
            estado = self.reloj.get_estado()
        elif self.algoritmo == 'fifo_plus' and self.impruve:
            estado = self.impruve.get_estado()
        elif self.marcos:
            estado = {
                "marcos": self.marcos.matriz,
                "historial_paginas": [p.numero for p in self.marcos.historial_paginas],
                "page_faults": self.marcos.page_faults,
                "estado_maquina": self.marcos.state,
                "proxima_pagina": self.marcos.obtener_pagina_actual().numero if self.marcos.obtener_pagina_actual() else None,
                "current_step": self.marcos.current_step
            }
        else:
            return {"error": "No hay simulación activa."}
        # Si la simulación terminó, agrega la comparación de errores
        if estado and estado.get('proxima_pagina') is None:
            if self.algoritmo in ['fifo', 'lru', 'optimo', 'second_opportunity', 'reloj', 'fifo_plus']:
                if self.fifo:
                    paginas = [p.numero for p in self.fifo.marcos.historial_paginas]
                    frames = self.fifo.marcos.cantidad
                elif self.lru:
                    paginas = [p.numero for p in self.lru.marcos.historial_paginas]
                    frames = self.lru.marcos.cantidad
                elif self.optimo:
                    paginas = [p.numero for p in self.optimo.marcos.historial_paginas]
                    frames = self.optimo.marcos.cantidad
                elif self.second_opportunity:
                    paginas = [p.numero for p in self.second_opportunity.marcos.historial_paginas]
                    frames = self.second_opportunity.marcos.cantidad
                elif self.reloj:
                    paginas = [p.numero for p in self.reloj.marcos.historial_paginas]
                    frames = self.reloj.marcos.cantidad
                elif self.impruve:
                    paginas = [p.numero for p in self.impruve.marcos.historial_paginas]
                    frames = self.impruve.marcos.cantidad
                else:
                    paginas = []
                    frames = 0
                estado['comparacion_errores'] = self.comparar_algoritmos(frames, paginas)
        return estado
