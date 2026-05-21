const API_URL = 'http://localhost:5000/api';

let ciudades = [];
let rutaActual = null;  // Guardar la ruta encontrada
let preciosRuedas = null;  // Guardar precios para cálculos

// Precios de ruedas (misma estructura que en backend)
const tiposRueda = ['T', 'H', 'V', 'W'];
const nombresTipos = {
    'T': 'Tipo T (Baja)',
    'H': 'Tipo H (Media)',
    'V': 'Tipo V (Alta)',
    'W': 'Tipo W (Alta)'
};
const nombresEmpresas = ['Empresa 1', 'Empresa 2', 'Empresa 3', 'Empresa 4'];

// Precios por tipo y empresa
const precios = {
    'T': [20, 50, 60, 100],
    'H': [30, 50, 55, 80],
    'V': [20, 40, 50, 60],
    'W': [40, 50, 60, 70]
};

async function cargarCiudades() {
    console.log('Cargando ciudades...');
    try {
        const response = await fetch(`${API_URL}/ciudades`);
        const data = await response.json();
        ciudades = data.ciudades ? data.ciudades.sort() : [];
        
        const origenSelect = document.getElementById('origen');
        const destinoSelect = document.getElementById('destino');
        
        if (origenSelect) {
            origenSelect.innerHTML = '<option value="">Seleccione origen...</option>';
            ciudades.forEach(ciudad => {
                const option = document.createElement('option');
                option.value = ciudad;
                option.textContent = ciudad;
                origenSelect.appendChild(option);
            });
        }
        
        if (destinoSelect) {
            destinoSelect.innerHTML = '<option value="">Seleccione destino...</option>';
            ciudades.forEach(ciudad => {
                const option = document.createElement('option');
                option.value = ciudad;
                option.textContent = ciudad;
                destinoSelect.appendChild(option);
            });
        }
        
        console.log(`${ciudades.length} ciudades cargadas`);
        mostrarMensaje(`${ciudades.length} ciudades disponibles`, 'exito');
        
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error al cargar ciudades. ¿Backend corriendo?', 'error');
    }
}

async function buscarRuta(origen, destino) {
    console.log(`Buscando ruta de ${origen} a ${destino}`);
    try {
        const response = await fetch(`${API_URL}/ruta`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ origen, destino })
        });
        
        const data = await response.json();
        console.log('Respuesta ruta:', data);
        
        if (data.exito) {
            rutaActual = {
                ciudades: data.ruta,
                costo: data.coste
            };
            
            // Mostrar resultados de ruta
            const rutaResultados = document.getElementById('rutaResultados');
            const rutaLista = document.getElementById('rutaLista');
            const costoRuta = document.getElementById('costoRuta');
            
            if (rutaLista) {
                rutaLista.innerHTML = '';
                data.ruta.forEach((ciudad, index) => {
                    const span = document.createElement('span');
                    span.textContent = ciudad;
                    rutaLista.appendChild(span);
                    if (index < data.ruta.length - 1) {
                        const flecha = document.createElement('span');
                        flecha.textContent = '→';
                        flecha.style.margin = '0 5px';
                        flecha.style.color = '#9bc4a5';
                        flecha.style.fontWeight = 'bold';
                        rutaLista.appendChild(flecha);
                    }
                });
            }
            
            if (costoRuta) costoRuta.textContent = `${data.coste} km`;
            if (rutaResultados) rutaResultados.style.display = 'block';
            
            // Mostrar panel de selección de ruedas
            crearSelectoresRuedas();
            document.getElementById('ruedasPanel').style.display = 'block';
            
            // Ocultar resultado total anterior
            document.getElementById('resultadoTotal').style.display = 'none';
            
            mostrarMensaje(`Ruta encontrada! Selecciona las ruedas para calcular el costo total.`, 'exito');
        } else {
            mostrarMensaje(data.mensaje || 'Ruta no encontrada', 'error');
            document.getElementById('ruedasPanel').style.display = 'none';
            document.getElementById('rutaResultados').style.display = 'none';
        }
    } catch (error) {
        console.error('Error en buscarRuta:', error);
        mostrarMensaje('Error de conexión con el servidor', 'error');
    }
}

function crearSelectoresRuedas() {
    const container = document.getElementById('ruedasSelectores');
    if (!container) return;
    
    container.innerHTML = '';
    
    tiposRueda.forEach(tipo => {
        const div = document.createElement('div');
        div.className = 'rueda-item';
        div.innerHTML = `
            <label>${nombresTipos[tipo]}</label>
            <select id="select_${tipo}" data-tipo="${tipo}" class="rueda-select">
                <option value="">Seleccione empresa...</option>
                <option value="0">${nombresEmpresas[0]} - $${precios[tipo][0]}</option>
                <option value="1">${nombresEmpresas[1]} - $${precios[tipo][1]}</option>
                <option value="2">${nombresEmpresas[2]} - $${precios[tipo][2]}</option>
                <option value="3">${nombresEmpresas[3]} - $${precios[tipo][3]}</option>
            </select>
        `;
        container.appendChild(div);
    });
    
    // Agregar event listeners para actualizar preview
    document.querySelectorAll('.rueda-select').forEach(select => {
        select.addEventListener('change', actualizarPreviewRuedas);
    });
    
    actualizarPreviewRuedas();
}

function actualizarPreviewRuedas() {
    const asignaciones = obtenerAsignacionesActuales();
    const previewDiv = document.getElementById('costoRuedasPreview');
    const detalleDiv = document.getElementById('detalleRuedas');
    
    if (!previewDiv || !detalleDiv) return;
    
    // Validar que no haya empresas repetidas
    const empresasUsadas = new Set();
    let hayDuplicados = false;
    let costoTotal = 0;
    let detalle = [];
    
    for (const [tipo, empresa] of Object.entries(asignaciones)) {
        if (empresa !== null && empresa !== '') {
            const empresaNum = parseInt(empresa);
            if (empresasUsadas.has(empresaNum)) {
                hayDuplicados = true;
            }
            empresasUsadas.add(empresaNum);
            const costo = precios[tipo][empresaNum];
            costoTotal += costo;
            detalle.push({
                tipo: nombresTipos[tipo],
                empresa: nombresEmpresas[empresaNum],
                costo: costo
            });
        }
    }
    
    if (Object.keys(asignaciones).length === 4 && !hayDuplicados && Object.values(asignaciones).every(v => v !== null && v !== '')) {
        previewDiv.style.display = 'block';
        detalleDiv.innerHTML = `
            <table style="width: 100%; margin-top: 10px;">
                ${detalle.map(d => `
                    <tr>
                        <td>${d.tipo}</td>
                        <td>${d.empresa}</td>
                        <td><strong>$${d.costo}</strong></td>
                    </tr>
                `).join('')}
                <tr style="border-top: 2px solid #d4c4b5;">
                    <td><strong>Total Ruedas</strong></td>
                    <td></td>
                    <td><strong>$${costoTotal}</strong></td>
                </tr>
            </table>
        `;
    } else {
        if (hayDuplicados) {
            detalleDiv.innerHTML = '<p style="color: #d4a5a5;">⚠️ No puedes seleccionar la misma empresa para diferentes tipos de rueda</p>';
        } else {
            const faltantes = 4 - Object.values(asignaciones).filter(v => v !== null && v !== '').length;
            detalleDiv.innerHTML = `<p>Selecciona los ${faltantes} tipos de rueda restantes</p>`;
        }
        previewDiv.style.display = 'block';
    }
}

function obtenerAsignacionesActuales() {
    const asignaciones = {};
    tiposRueda.forEach(tipo => {
        const select = document.getElementById(`select_${tipo}`);
        if (select && select.value) {
            asignaciones[tipo] = select.value;
        } else {
            asignaciones[tipo] = null;
        }
    });
    return asignaciones;
}

async function calcularCostoTotal() {
    const origen = document.getElementById('origen')?.value;
    const destino = document.getElementById('destino')?.value;
    const asignaciones = obtenerAsignacionesActuales();
    
    if (!origen || !destino) {
        mostrarMensaje('Primero busca una ruta', 'error');
        return;
    }
    
    // Validar que todos los tipos estén seleccionados
    const todasSeleccionadas = Object.values(asignaciones).every(v => v !== null && v !== '');
    if (!todasSeleccionadas) {
        mostrarMensaje('Selecciona todas las ruedas (T, H, V, W)', 'error');
        return;
    }
    
    // Validar empresas únicas
    const empresasUsadas = new Set(Object.values(asignaciones).map(v => parseInt(v)));
    if (empresasUsadas.size !== 4) {
        mostrarMensaje('Cada empresa solo puede suministrar un tipo de rueda. ¡No repitas empresas!', 'error');
        return;
    }
    
    mostrarMensaje('Calculando costo total...', 'exito');
    
    try {
        const response = await fetch(`${API_URL}/calcular_costo_total`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ origen, destino, asignaciones })
        });
        
        const data = await response.json();
        console.log('Respuesta costo total:', data);
        
        if (data.exito) {
            mostrarResultadoTotal(data);
        } else {
            mostrarMensaje(data.mensaje || 'Error al calcular costo total', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje('Error de conexión con el servidor', 'error');
    }
}

function mostrarResultadoTotal(data) {
    const resultadoDiv = document.getElementById('resultadoTotal');
    const resRuta = document.getElementById('resRuta');
    const resDistancia = document.getElementById('resDistancia');
    const resRuedas = document.getElementById('resRuedas');
    const resCostoTotal = document.getElementById('resCostoTotal');
    const resMensaje = document.getElementById('resMensaje');
    
    if (resRuta) resRuta.textContent = data.ruta.ciudades.join(' → ');
    if (resDistancia) resDistancia.textContent = `${data.ruta.costo_km} km`;
    
    if (resRuedas) {
        resRuedas.innerHTML = data.ruedas.asignaciones.map(a => 
            `<div>${a.tipo} → ${a.empresa}: $${a.costo}</div>`
        ).join('');
        resRuedas.innerHTML += `<div style="margin-top: 10px;"><strong>Total ruedas: $${data.ruedas.costo_total_ruedas}</strong></div>`;
    }
    
    if (resCostoTotal) resCostoTotal.textContent = data.costo_total;
    if (resMensaje) resMensaje.textContent = data.mensaje;
    
    if (resultadoDiv) resultadoDiv.style.display = 'block';
    
    // Scroll al resultado
    resultadoDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function mostrarMensaje(mensaje, tipo) {
    console.log(`Mensaje (${tipo}): ${mensaje}`);
    const mensajeDiv = document.getElementById('mensaje');
    const mensajeTexto = document.getElementById('mensajeTexto');
    
    if (mensajeTexto) mensajeTexto.textContent = mensaje;
    if (mensajeDiv) {
        mensajeDiv.className = `mensaje-card ${tipo}`;
        mensajeDiv.style.display = 'block';
    }
    
    setTimeout(() => {
        if (mensajeDiv) mensajeDiv.style.display = 'none';
    }, 4000);
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    console.log('=== INICIANDO APLICACIÓN ===');
    
    const buscarBtn = document.getElementById('buscarRutaBtn');
    const calcularBtn = document.getElementById('calcularTotalBtn');
    
    if (buscarBtn) {
        buscarBtn.addEventListener('click', () => {
            const origen = document.getElementById('origen')?.value;
            const destino = document.getElementById('destino')?.value;
            if (!origen || !destino) {
                mostrarMensaje('Seleccione origen y destino', 'error');
                return;
            }
            if (origen === destino) {
                mostrarMensaje('Origen y destino no pueden ser iguales', 'error');
                return;
            }
            buscarRuta(origen, destino);
        });
    }
    
    if (calcularBtn) {
        calcularBtn.addEventListener('click', calcularCostoTotal);
    }
    
    cargarCiudades();
});