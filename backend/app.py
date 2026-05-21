from flask import Flask, request, jsonify
from flask_cors import CORS
from busqueda_rutas import BuscadorRutas
from problema_ruedas import ProblemaRuedas

app = Flask(__name__)
CORS(app)

buscador = BuscadorRutas()
problema_ruedas = ProblemaRuedas()

# ============ ENDPOINTS EXISTENTES (BÚSQUEDA DE RUTAS) ============
@app.route('/api/ciudades', methods=['GET'])
def obtener_ciudades():
    ciudades = buscador.obtener_ciudades()
    return jsonify({'ciudades': ciudades})

@app.route('/api/ruta', methods=['POST'])
def buscar_ruta():
    data = request.json
    origen = data.get('origen')
    destino = data.get('destino')
    
    if not origen or not destino:
        return jsonify({'error': 'Faltan parámetros'}), 400
    
    resultado = buscador.obtener_ruta(origen, destino)
    return jsonify(resultado)

@app.route('/api/agregar_ciudad', methods=['POST'])
def agregar_ciudad():
    data = request.json
    nombre = data.get('nombre', '').strip().upper()
    latitud = data.get('latitud')
    longitud = data.get('longitud')
    
    if not nombre or latitud is None or longitud is None:
        return jsonify({'error': 'Faltan parámetros'}), 400
    
    try:
        resultado = buscador.agregar_ciudad(nombre, latitud, longitud)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)}), 500

@app.route('/api/agregar_conexion', methods=['POST'])
def agregar_conexion():
    data = request.json
    ciudad1 = data.get('ciudad1', '').strip().upper()
    ciudad2 = data.get('ciudad2', '').strip().upper()
    distancia = data.get('distancia')
    
    if not ciudad1 or not ciudad2 or distancia is None:
        return jsonify({'error': 'Faltan parámetros'}), 400
    
    try:
        resultado = buscador.agregar_conexion(ciudad1, ciudad2, distancia)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': str(e)}), 500

# ============ NUEVO ENDPOINT: CALCULAR COSTO TOTAL (RUTA + RUEDAS) ============
@app.route('/api/calcular_costo_total', methods=['POST'])
def calcular_costo_total():
    """
    Calcula el costo total combinado:
    - Costo de la ruta (distancia en km)
    - Costo de las ruedas seleccionadas por el usuario
    """
    data = request.json
    origen = data.get('origen')
    destino = data.get('destino')
    asignaciones = data.get('asignaciones', {})  # {tipo_rueda: empresa_id}
    
    if not origen or not destino:
        return jsonify({'error': 'Faltan origen o destino'}), 400
    
    # 1. Obtener la ruta óptima
    resultado_ruta = buscador.obtener_ruta(origen, destino)
    
    if not resultado_ruta.get('exito'):
        return jsonify({
            'exito': False,
            'mensaje': resultado_ruta.get('mensaje', 'No se encontró ruta')
        }), 404
    
    costo_ruta = resultado_ruta['coste']
    ruta_completa = resultado_ruta['ruta']
    
    # 2. Calcular costo de ruedas
    costo_ruedas = 0
    detalle_ruedas = []
    
    for tipo, empresa_id in asignaciones.items():
        # empresa_id puede venir como string o int
        empresa = int(empresa_id) if isinstance(empresa_id, str) else empresa_id
        costo = problema_ruedas.costo_real(tipo, empresa)
        costo_ruedas += costo
        detalle_ruedas.append({
            'tipo': tipo,
            'empresa': problema_ruedas.nombres_empresas[empresa],
            'costo': costo
        })
    
    # 3. Costo total
    costo_total = costo_ruta + costo_ruedas
    
    return jsonify({
        'exito': True,
        'ruta': {
            'ciudades': ruta_completa,
            'costo_km': costo_ruta
        },
        'ruedas': {
            'asignaciones': detalle_ruedas,
            'costo_total_ruedas': costo_ruedas
        },
        'costo_total': costo_total,
        'mensaje': f'Costo total calculado: ${costo_total} (${costo_ruta} de ruta + ${costo_ruedas} de ruedas)'
    })

# ============ ENDPOINTS PARA RUEDAS (PROBLEMA DE ASIGNACIÓN) ============
@app.route('/api/ruedas/precios', methods=['GET'])
def obtener_precios_ruedas():
    """Devuelve la tabla de precios de ruedas"""
    return jsonify({
        'precios': problema_ruedas.precios,
        'tipos': problema_ruedas.tipos_rueda,
        'empresas': problema_ruedas.nombres_empresas
    })

@app.route('/api/ruedas/solucion', methods=['GET'])
def obtener_solucion_ruedas():
    """Ejecuta A* y devuelve la solución óptima"""
    solucion = problema_ruedas.obtener_solucion()
    if solucion:
        return jsonify({
            'success': True,
            'solution': solucion
        })
    else:
        return jsonify({
            'success': False,
            'error': 'No se encontró solución'
        }), 404

@app.route('/api/ruedas/heuristica', methods=['GET'])
def explicar_heuristica():
    """Explica por qué la heurística es admisible"""
    return jsonify(problema_ruedas._explicar_heuristica())

if __name__ == '__main__':
    app.run(debug=True, port=5000)