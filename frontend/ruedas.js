const API_URL = 'https://ruedas-astar-api.onrender.com/api';

async function cargarPrecios() {
    console.log('Cargando precios de ruedas...');
    try {
        const response = await fetch(`${API_URL}/ruedas/precios`);
        const data = await response.json();
        
        const tbody = document.getElementById('preciosBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        const tiposMap = {
            'T': 'T (Baja)',
            'H': 'H (Media)',
            'V': 'V (Alta)',
            'W': 'W (Alta)'
        };
        
        for (const [tipo, precios] of Object.entries(data.precios)) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${tiposMap[tipo] || tipo}</strong></td>
                <td>$${precios[0]}</td>
                <td>$${precios[1]}</td>
                <td>$${precios[2]}</td>
                <td>$${precios[3]}</td>
            `;
            tbody.appendChild(row);
        }
        
        console.log('Precios cargados correctamente');
    } catch (error) {
        console.error('Error cargando precios:', error);
        mostrarError('Error al cargar los precios. ¿El backend está corriendo?');
    }
}

async function resolverProblema() {
    const solveBtn = document.getElementById('solveBtn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    solveBtn.disabled = true;
    loading.style.display = 'block';
    results.style.display = 'none';
    
    try {
        const response = await fetch(`${API_URL}/ruedas/solucion`);
        const data = await response.json();
        
        if (data.success) {
            mostrarSolucion(data.solution);
            await cargarValidacionHeuristica();
        } else {
            mostrarError(data.error || 'Error al encontrar solución');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarError('Error de conexión con el servidor');
    } finally {
        solveBtn.disabled = false;
        loading.style.display = 'none';
    }
}

function mostrarSolucion(solution) {
    const finalSolutionDiv = document.getElementById('finalSolution');
    const stepsContainer = document.getElementById('stepsContainer');
    const totalCostSpan = document.getElementById('totalCost');
    const results = document.getElementById('results');
    
    finalSolutionDiv.innerHTML = '';
    solution.detalle.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'asignacion-item';
        itemDiv.innerHTML = `
            <span><strong>Rueda Tipo ${item.tipo}</strong></span>
            <span>${item.empresa}</span>
            <span><strong>$${item.costo}</strong></span>
        `;
        finalSolutionDiv.appendChild(itemDiv);
    });
    
    stepsContainer.innerHTML = '';
    solution.asignaciones.forEach((asignacion, index) => {
        if (index === 0 && Object.keys(asignacion).length === 0) {
            const stepDiv = document.createElement('div');
            stepDiv.className = 'step-item';
            stepDiv.innerHTML = `<strong>Paso ${index}:</strong> Estado inicial (sin asignaciones)`;
            stepsContainer.appendChild(stepDiv);
        } else if (Object.keys(asignacion).length > 0) {
            const stepDiv = document.createElement('div');
            stepDiv.className = 'step-item';
            let asignacionesStr = Object.entries(asignacion)
                .map(([tipo, empresa]) => `${tipo} → ${empresa}`)
                .join(', ');
            stepDiv.innerHTML = `<strong>Paso ${index}:</strong> { ${asignacionesStr} }`;
            stepsContainer.appendChild(stepDiv);
        }
    });
    
    totalCostSpan.textContent = solution.costo_total;
    results.style.display = 'block';
    results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function cargarValidacionHeuristica() {
    try {
        const response = await fetch(`${API_URL}/ruedas/heuristica`);
        const data = await response.json();
        
        const validationText = document.getElementById('validationText');
        if (validationText) {
            validationText.innerHTML = `
                <strong> ${data.titulo}</strong><br><br>
                <strong>Definición:</strong> ${data.descripcion}<br><br>
                <strong>¿Por qué es admisible?</strong> ${data.razon}<br><br>
                <strong>Ejemplo:</strong> ${data.ejemplo}<br><br>
                <span style="color: #28a745;"> Como la heurística siempre toma el mínimo precio posible para los tipos pendientes, NUNCA sobrestima el costo real. Esto garantiza que A* encuentre la solución óptima.</span>
            `;
        }
    } catch (error) {
        console.error('Error cargando validación:', error);
    }
}

function mostrarError(mensaje) {
    const results = document.getElementById('results');
    const loading = document.getElementById('loading');
    
    if (loading) loading.style.display = 'none';
    if (results) results.style.display = 'none';
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'mensaje-card error';
    errorDiv.style.margin = '20px';
    errorDiv.style.padding = '20px';
    errorDiv.innerHTML = `<p> ${mensaje}</p>`;
    
    const container = document.querySelector('.main-content');
    const existingError = document.querySelector('.mensaje-card.error');
    if (existingError) existingError.remove();
    if (container) container.insertBefore(errorDiv, container.firstChild);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('=== INICIANDO APLICACIÓN DE RUEDAS ===');
    
    const solveBtn = document.getElementById('solveBtn');
    if (solveBtn) {
        solveBtn.addEventListener('click', resolverProblema);
    }
    
    cargarPrecios();
});