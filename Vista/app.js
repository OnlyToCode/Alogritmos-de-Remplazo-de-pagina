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
    // Guardar el tamaño de la secuencia
    totalPaginas = secuencia.split(',').filter(x => x.trim() !== '').length;
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
    // Guardar posición de scroll antes de actualizar
    const simTableWrapper = resultados.querySelector('.sim-table-wrapper');
    let prevScrollLeft = simTableWrapper ? simTableWrapper.scrollLeft : null;
    let userScrolling = false;
    if (simTableWrapper) {
        simTableWrapper.addEventListener('scroll', () => {
            userScrolling = true;
        }, { once: true });
    }
    try {
        const response = await fetch('http://127.0.0.1:5000/estado');
        const data = await response.json();
        if (data.error) {
            resultados.innerHTML = `<p style='color: red;'>${data.error}</p>`;
        } else {
            resultados.innerHTML = renderSimulacion(data);
            // Scroll automático solo si el usuario no está desplazando manualmente
            const newSimTableWrapper = resultados.querySelector('.sim-table-wrapper');
            if (newSimTableWrapper) {
                if (userScrolling && prevScrollLeft !== null) {
                    newSimTableWrapper.scrollLeft = prevScrollLeft;
                } else {
                    newSimTableWrapper.scrollLeft = newSimTableWrapper.scrollWidth;
                }
            }
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
    let html = `<h2 style='display: flex; justify-content: space-between; align-items: center;'>
        <span>Estado de la simulación</span>
        <span style='display: flex; gap: 1.5em;'>
            <span><strong>Próxima página:</strong></span>
            <span style='min-width: 2.5em; display: inline-block; text-align: center; background: #eaf6ff; border-radius: 0.5em; padding: 0.2em 0.8em; font-weight: bold;'>
                ${data.proxima_pagina ?? '-'}
            </span>
        </span>
    </h2>`;
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
                let valor = data.marcos[iter][marcoIdx] ?? '-';
                // FIFO Mejorado: pinta azul si bit_proteccion activo
                if (data.bits_proteccion && data.bits_proteccion[iter]) {
                    let bit = data.bits_proteccion[iter][marcoIdx];
                    let style = '';
                    if (bit) style += 'background: #a3c9f7;'; // azul
                    html += `<td class='${cellClass}' style='${style}'>${valor}</td>`;
                // Segunda Oportunidad: pinta azul claro si bit_uso activo
                } else if (data.bits_uso && !data.punteros && data.bits_uso[iter]) {
                    let bit = data.bits_uso[iter][marcoIdx];
                    let style = '';
                    if (bit) style += 'background: #cce4ff;'; // azul claro
                    html += `<td class='${cellClass}' style='${style}'>${valor}</td>`;
                // Reloj: pinta verde y muestra reloj si puntero
                } else if (data.bits_uso && data.punteros && data.bits_uso[iter] && typeof data.punteros[iter] !== 'undefined') {
                    let bit = data.bits_uso[iter][marcoIdx];
                    let isPointer = (data.punteros[iter] % data.bits_uso[0].length) === marcoIdx;
                    let style = '';
                    if (bit) style += 'background: #d4f7c5;';
                    let pointerMark = isPointer ? `<span style='color:#e67e22;font-weight:bold; margin-left:0.3em;'>⏰</span>` : '';
                    html += `<td class='${cellClass}' style='${style}'>${valor}${pointerMark}</td>`;
                } else {
                    html += `<td class='${cellClass}'>${valor}</td>`;
                }
            }
            html += `</tr>`;
        }
    }
    // Elimina completamente la visualización de filas de bits de protección, incluso del placeholder
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

    // Mostrar errores de página comparados con el óptimo al final de la simulación
    if (data.comparacion_errores) {
        html += `<div class='comparacion-errores'><h3>Errores de página por algoritmo</h3><ul>`;
        for (const alg of data.comparacion_errores) {
            html += `<li><strong>${alg.nombre}:</strong> ${alg.fallos} errores`;
            if (alg.diferencia > 0) {
                html += ` <span style='color: #c0392b;'>(+${alg.diferencia} respecto al óptimo)</span>`;
            } else if (alg.diferencia === 0) {
                html += ` <span style='color: #27ae60;'>(Óptimo)</span>`;
            }
            html += `</li>`;
        }
        html += `</ul></div>`;
    }
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
        const resp = await fetch('http://127.0.0.1:5000/retroceder', { method: 'POST' });
        const data = await resp.json();
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
let playForce = false;
let totalPaginas = 0; // Guardar el tamaño de la secuencia
const btnPlay = document.getElementById('btn-play');

if (btnPlay) {
    btnPlay.addEventListener('click', function() {
        if (playInterval) {
            clearInterval(playInterval);
            playInterval = null;
            playForce = false;
            btnPlay.textContent = 'Play';
            btnPlay.classList.remove('pausar');
        } else {
            btnPlay.textContent = 'Pausar';
            btnPlay.classList.add('pausar');
            playForce = true;
            playInterval = setInterval(async () => {
                if (!playForce) {
                    clearInterval(playInterval);
                    playInterval = null;
                    btnPlay.textContent = 'Play';
                    btnPlay.classList.remove('pausar');
                    return;
                }
                // Solo detener si ya se avanzó toda la secuencia según el front
                const currentCols = document.querySelectorAll('.sim-table tr.historial-row td').length - 1;
                if (currentCols >= totalPaginas) {
                    clearInterval(playInterval);
                    playInterval = null;
                    playForce = false;
                    btnPlay.textContent = 'Play';
                    btnPlay.classList.remove('pausar');
                    return;
                }
                await fetch('http://127.0.0.1:5000/avanzar', { method: 'POST' });
                await mostrarEstado();
            }, 800);
        }
    });
}

// Mostrar estado al cargar
mostrarEstado();
