// app.js - Esqueleto básico para manejar el formulario

const chkAutoPaginas = document.getElementById('chk-auto-paginas');
const inputSequence = document.getElementById('sequence');

chkAutoPaginas.addEventListener('change', function() {
    if (chkAutoPaginas.checked) {
        inputSequence.required = false;
        inputSequence.disabled = true;
        // Generar páginas aleatorias y ponerlas en el input
        const cantidad = 15; // puedes ajustar la cantidad
        const minimo = 0, maximo = 9;
        fetch(`http://127.0.0.1:5000/generar_paginas?cantidad=${cantidad}&minimo=${minimo}&maximo=${maximo}`)
            .then(resp => resp.json())
            .then(data => {
                inputSequence.value = data.paginas.join(',');
            });
    } else {
        inputSequence.required = true;
        inputSequence.disabled = false;
        inputSequence.value = '';
    }
});

document.getElementById('sim-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const algoritmo = document.getElementById('algorithm').value;
    const frames = document.getElementById('frames').value;
    let secuencia = document.getElementById('sequence').value;
    if (chkAutoPaginas.checked && !secuencia) {
        secuencia = inputSequence.value;
    }
    const resultados = document.getElementById('resultados');
    resultados.innerHTML = '<p>Enviando datos al servidor...</p>';
    try {
        const response = await fetch('http://127.0.0.1:5000/simular', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                algoritmo: algoritmo,
                frames: frames,
                secuencia: secuencia
            })
        });
        const data = await response.json();
        if (response.status === 501) {
            resultados.innerHTML = `<p style='color: orange;'><strong>Servidor:</strong> ${data.message}</p>`;
        } else if (response.ok) {
            resultados.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        } else {
            resultados.innerHTML = `<p style='color: red;'>Error: ${data.message || 'Error desconocido'}</p>`;
        }
    } catch (error) {
        resultados.innerHTML = `<p style='color: red;'>No se pudo conectar con el servidor.</p>`;
    }
    mostrarEstado();
});

async function mostrarEstado() {
    const resultados = document.getElementById('resultados');
    try {
        const response = await fetch('http://127.0.0.1:5000/estado');
        const data = await response.json();
        if (data.error) {
            resultados.innerHTML = `<p style='color: red;'>${data.error}</p>`;
        } else {
            resultados.innerHTML = renderSimulacion(data);
        }
    } catch (error) {
        resultados.innerHTML = `<p style='color: red;'>No se pudo conectar con el servidor.</p>`;
    }
}

async function reiniciarSimulacion() {
    await fetch('http://127.0.0.1:5000/reiniciar', { method: 'POST' });
    mostrarEstado();
}

function renderBadgeEstado(estado, proximaPagina) {
    let clase = '';
    let label = '';
    if (estado === 'en_espera' && proximaPagina === null) {
        clase = 'badge badge-en_espera';
        label = 'FINALIZADO';
    } else if (estado === 'en_espera') {
        clase = 'badge badge-en_espera';
        label = 'EN ESPERA';
    } else if (estado === 'decidiendo') {
        clase = 'badge badge-decidiendo';
        label = 'DECIDIENDO';
    } else if (estado === 'actualizando') {
        clase = 'badge badge-actualizando';
        label = 'ACTUALIZANDO';
    }
    return `<span class="${clase}">${label}</span>`;
}

function renderSimulacion(data) {
    let html = `<h2>Estado de la simulación</h2>`;
    document.getElementById('badge-estado').innerHTML = renderBadgeEstado(data.estado_maquina, data.proxima_pagina);
    html += `<div class='sim-table-wrapper'><table class='sim-table'>`;
    // Historial de páginas (encabezado superior)
    html += `<tr class='historial-row'><td class='historial'>Historial</td>`;
    for (let i = 0; i < data.historial_paginas.length; i++) {
        html += `<td class='historial'>${data.historial_paginas[i]}</td>`;
    }
    html += `</tr>`;
    // Filas de marcos (cada marco es una fila, cada columna es una iteración)
    if (data.marcos.length > 0) {
        for (let marcoIdx = 0; marcoIdx < data.marcos[0].length; marcoIdx++) {
            html += `<tr><td>Marco ${marcoIdx+1}</td>`;
            for (let iter = 0; iter < data.marcos.length; iter++) {
                let cellClass = (iter === data.current_step) ? 'actual' : '';
                html += `<td class='${cellClass}'>${data.marcos[iter][marcoIdx] ?? '-'}</td>`;
            }
            html += `</tr>`;
        }
    }
    // Fila de page faults con emojis (alineados con las iteraciones)
    html += `<tr class='page-fault-row'><td>Page Fault</td>`;
    for (let i = 0; i < data.page_faults.length; i++) {
        let pf = data.page_faults[i];
        let emoji = pf ? '❌' : '✅';
        let pfClass = pf ? 'bad' : 'good';
        html += `<td class='${pfClass}'>${emoji}</td>`;
    }
    html += `</tr>`;
    html += `</table></div>`;
    return html;
}

// Botón avanzar
const btnAvanzar = document.getElementById('btn-avanzar');
if (btnAvanzar) {
    btnAvanzar.addEventListener('click', async function() {
        await fetch('http://127.0.0.1:5000/avanzar', { method: 'POST' });
        mostrarEstado();
    });
}

// Botón retroceder
const btnRetroceder = document.getElementById('btn-retroceder');
if (btnRetroceder) {
    btnRetroceder.addEventListener('click', async function() {
        await fetch('http://127.0.0.1:5000/retroceder', { method: 'POST' });
        mostrarEstado();
    });
}

// Botón reiniciar
const btnReiniciar = document.getElementById('btn-reiniciar');
if (btnReiniciar) {
    btnReiniciar.addEventListener('click', reiniciarSimulacion);
}

// Botón play (avance automático)
let playInterval = null;
const btnPlay = document.getElementById('btn-play');
if (btnPlay) {
    btnPlay.addEventListener('click', function() {
        if (playInterval) {
            clearInterval(playInterval);
            playInterval = null;
            btnPlay.textContent = 'Play';
            btnPlay.classList.remove('pausar');
        } else {
            btnPlay.textContent = 'Pausar';
            btnPlay.classList.add('pausar');
            playInterval = setInterval(async () => {
                const resp = await fetch('http://127.0.0.1:5000/avanzar', { method: 'POST' });
                const data = await resp.json();
                mostrarEstado();
                if (!data.proxima_pagina) {
                    clearInterval(playInterval);
                    playInterval = null;
                    btnPlay.textContent = 'Play';
                    btnPlay.classList.remove('pausar');
                }
            }, 800); // velocidad de avance
        }
    });
}

// Mostrar estado al cargar
mostrarEstado();
