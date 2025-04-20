from transitions import Machine
from copy import deepcopy

class Pagina:
    """
    Representa una página de memoria adaptable a cualquier algoritmo.
    Atributos:
        numero (int): identificador de la página.
        last_used (int): para LRU, almacena el último tiempo de uso.
        future_uses (list): para Óptimo, almacena las posiciones futuras de uso.
        bit_proteccion (bool): para FIFO Plus Impruve, indica si la página está protegida (solo un marco puede tenerlo a la vez).
        bit_uso (bool): para Reloj y Second Opportunity, indica si la página ha sido usada recientemente.
        bit_modificado (bool): para variantes que requieran bit de modificación.
    """
    def __init__(self, numero):
        self.numero = numero
        self.last_used = None         # LRU
        self.future_uses = []         # Óptimo
        self.bit_proteccion = False   # FIFO Plus Impruve
        self.bit_uso = False          # Reloj, Second Opportunity
        self.bit_modificado = False   # Si alguna variante lo requiere

    def reset(self):
        """Resetea los bits y valores auxiliares (excepto el número de página)."""
        self.last_used = None
        self.future_uses = []
        self.bit_proteccion = False
        self.bit_uso = False
        self.bit_modificado = False

    def __repr__(self):
        return f"Pagina({self.numero})"

class Marcos:
    """
    Refactor: Gestión robusta de marcos para cualquier algoritmo.
    - Los marcos son una lista de objetos Pagina o None, tamaño fijo.
    - Controla el bit de protección (FIFO Plus) para que solo un marco lo tenga.
    - Historial de pasos y page faults.
    - Observers para notificar cambios.
    - Interfaz pública clara: encolar, avanzar, retroceder, reiniciar, obtener estado.
    """
    states = [
        {'name': 'en_espera', 'on_enter': ['on_enter_espera']},
        {'name': 'decidiendo', 'on_enter': ['on_enter_decidiendo']},
        {'name': 'actualizando', 'on_enter': ['on_enter_actualizando']}
    ]

    def __init__(self, cantidad, modelo=None):
        self.cantidad = cantidad
        self.marcos = [None] * cantidad  # Estado actual de los marcos
        self.matriz = []  # Historial de marcos (lista de listas de números de página o None)
        self.page_faults = []
        self.current_step = 0
        self.historial_paginas = []
        self.pagina_actual = None
        self.modelo = modelo
        self.tiempo = 0
        self.cola_paginas = []
        self.proxima_pagina_idx = 0
        self.observers = []
        self.machine = Machine(model=self, states=Marcos.states, initial='en_espera', auto_transitions=False)
        self.machine.add_transition('recibir_pagina', 'en_espera', 'decidiendo')
        self.machine.add_transition('decidir', 'decidiendo', 'actualizando', conditions=['debe_actualizar'])
        self.machine.add_transition('descartar', 'decidiendo', 'en_espera', unless=['debe_actualizar'])
        self.machine.add_transition('esperar', 'actualizando', 'en_espera')

    def add_observer(self, callback):
        self.observers.append(callback)

    def notify_observers(self):
        for callback in self.observers:
            callback(self.get_estado())

    def encolar_paginas(self, paginas):
        self.cola_paginas.extend(paginas)

    def encolar_pagina(self, pagina):
        self.cola_paginas.append(pagina)

    def hay_pagina_por_decidir(self):
        return self.proxima_pagina_idx < len(self.cola_paginas)

    def obtener_pagina_actual(self):
        if self.hay_pagina_por_decidir():
            return self.cola_paginas[self.proxima_pagina_idx]
        return None

    def avanzar_pagina(self):
        if self.hay_pagina_por_decidir():
            self.proxima_pagina_idx += 1

    def reset(self):
        self.marcos = [None] * self.cantidad
        self.matriz = []
        self.page_faults = []
        self.current_step = 0
        self.historial_paginas = []
        self.pagina_actual = None
        self.tiempo = 0
        self.cola_paginas = []
        self.proxima_pagina_idx = 0

    def agregar_iteracion(self, page_fault):
        # Guarda una copia profunda del estado actual de los marcos (solo números o None)
        self.matriz.append([p.numero if p else None for p in self.marcos])
        self.page_faults.append(page_fault)
        self.current_step = len(self.matriz) - 1
        self.notify_observers()

    def get_estado(self):
        return {
            'marcos': self.matriz,
            'historial_paginas': [p.numero for p in self.historial_paginas],
            'page_faults': self.page_faults,
            'estado_maquina': self.state,
            'proxima_pagina': self.obtener_pagina_actual().numero if self.obtener_pagina_actual() else None,
            'current_step': self.current_step
        }

    def proteger_pagina(self, pagina):
        # Solo un marco puede tener bit_proteccion=True
        for p in self.marcos:
            if p and hasattr(p, 'bit_proteccion'):
                p.bit_proteccion = False
        pagina.bit_proteccion = True

    # Métodos de la máquina de estados
    def on_enter_espera(self):
        # Estado de reposo, listo para recibir la siguiente página
        self.pagina_actual = None

    def on_enter_decidiendo(self):
        # Prepara la página actual para decidir
        self.pagina_actual = self.obtener_pagina_actual()
        # Aquí se puede consultar self.pagina_actual y decidir qué información pasar al algoritmo

    def on_enter_actualizando(self):
        # Aquí se debe actualizar el estado de los marcos según el algoritmo
        # y llamar a agregar_iteracion(page_fault) desde el controller/algoritmo
        self.avanzar_pagina()
        # El controller debe llamar a esperar() para volver a 'en_espera' después de actualizar

    def debe_actualizar(self):
        return True  # Placeholder, lógica real depende del algoritmo

    def avanzar(self):
        if self.current_step < len(self.matriz) - 1:
            self.current_step += 1
            self.notify_observers()
            return True
        return False

    def retroceder(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.notify_observers()
            return True
        return False
