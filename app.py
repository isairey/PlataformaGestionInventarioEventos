from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "eventos_pro_key"

def get_db_connection():
    conn = sqlite3.connect('inventario.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- MONITOR DE ACTUALIZACIONES ---
@app.route('/api/check_updates')
def check_updates():
    conn = get_db_connection()
    # Sumamos alquileres y daños. Si cualquiera de las dos tablas cambia, la versión cambia.
    res = conn.execute('''
        SELECT 
        (SELECT COUNT(*) FROM alquileres) + 
        (SELECT SUM(CASE WHEN estado LIKE "%Retirado%" THEN 1 ELSE 0 END) FROM alquileres) +
        (SELECT COUNT(*) FROM danos)
    ''').fetchone()[0]
    conn.close()
    return jsonify({"version": res})
# --- VISTA ADMIN (INDEX) ---
@app.route('/')
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM inventario').fetchall()
    resumen = []
    for item in items:
        alquiladas = conn.execute('SELECT SUM(cantidad) FROM alquileres WHERE articulo_id = ? AND estado NOT LIKE "Retirado%"', (item['id'],)).fetchone()[0] or 0
        danadas = conn.execute('SELECT COUNT(*) FROM danos WHERE articulo_id = ?', (item['id'],)).fetchone()[0]
        resumen.append({
            'id': item['id'], 'nombre': item['nombre'], 'total_global': item['total'],
            'en_bodega': item['total'] - alquiladas - danadas,
            'alquiladas': alquiladas, 'danadas': danadas
        })
    conn.close()
    return render_template('index.html', resumen=resumen)

# --- VISTA VENDEDOR (COTIZADOR) ---
@app.route('/vendedor')
def vista_vendedor():
    conn = get_db_connection()
    inventario = conn.execute('SELECT * FROM inventario').fetchall()
    conn.close()
    return render_template('vendedor.html', inventario=inventario)

@app.route('/api/crear_reserva', methods=['POST'])
def crear_reserva():
    f = request.form
    metodo = f.get('metodo_pago')
    total = f.get('monto_total')
    ids = f.getlist('articulo_id[]')
    cants = f.getlist('cantidad[]')
    
    conn = get_db_connection()
    for i in range(len(ids)):
        conn.execute('''INSERT INTO alquileres 
            (articulo_id, cliente, telefono, ubicacion, cantidad, fecha_entrega, hora_entrega, fecha_retiro, hora_retiro, estado) 
            VALUES (?,?,?,?,?,?,?,?,?,?)''', 
            (ids[i], f.get('nombre'), f.get('celular'), f.get('direccion'), cants[i], 
             f.get('fecha_entrega'), f.get('hora_entrega'), f.get('fecha_retiro'), f.get('hora_retiro'), 
             f'Por entregar | {metodo} ($' + str(total) + ')'))
    conn.commit()
    conn.close()
    return redirect(url_for('vista_vendedor'))

# --- NUEVA RUTA: VISTA EMPLEADO (PARA QUITAR EL 404) ---
@app.route('/empleado')
def vista_empleado():
    conn = get_db_connection()
    raw = conn.execute('''
        SELECT a.*, i.nombre as art_nom 
        FROM alquileres a 
        JOIN inventario i ON a.articulo_id = i.id 
        WHERE a.estado NOT LIKE "Retirado%" 
        ORDER BY a.fecha_entrega ASC, a.hora_entrega ASC
    ''').fetchall()
    
    agrupados = {}
    for r in raw:
        # La clave ahora incluye fechas para evitar confusiones
        key = f"{r['cliente']}_{r['fecha_entrega']}_{r['fecha_retiro']}"
        if key not in agrupados:
            agrupados[key] = {
                'cliente': r['cliente'], 
                'tel': r['telefono'], 
                'ubi': r['ubicacion'],
                'f_e': r['fecha_entrega'], 
                'h_e': r['hora_entrega'],
                'f_r': r['fecha_retiro'],   # Agregamos fecha retiro
                'h_r': r['hora_retiro'],   # Agregamos hora retiro
                'estado': r['estado'],
                'articulos_lista': []
            }
        agrupados[key]['articulos_lista'].append({
            'id': r['id'], 'nom': r['art_nom'], 'cant': r['cantidad'], 'art_id': r['articulo_id']
        })
    
    inv = conn.execute('SELECT * FROM inventario').fetchall()
    conn.close()
    return render_template('empleado.html', pedidos=agrupados.values(), inventario=inv)
# --- ACCIÓN: FINALIZAR PEDIDO GRUPAL ---
@app.route('/api/finalizar_pedido_grupal', methods=['POST'])
def finalizar_pedido_grupal():
    ids = request.form.getlist('pedido_ids[]')
    nuevo_estado = request.form.get('nuevo_estado')
    
    conn = get_db_connection()
    for pid in ids:
        conn.execute('UPDATE alquileres SET estado = ? WHERE id = ?', (nuevo_estado, pid))
    
    # Lógica de daño si el estado es Retirado
    if request.form.get('hubo_dano') == 'si' and nuevo_estado == 'Retirado':
        art_id = request.form.get('articulo_dano_id')
        cant_d = int(request.form.get('cantidad_danada') or 0)
        desc = request.form.get('descripcion_dano')
        for _ in range(cant_d):
            conn.execute('INSERT INTO danos (articulo_id, descripcion, fecha_dano) VALUES (?,?,?)',
                         (art_id, desc, datetime.now().date()))
    
    conn.commit()
    conn.close()
    return redirect(url_for('vista_empleado'))

# --- API DETALLES ---
@app.route('/api/detalles/<int:articulo_id>/<tipo>')
def obtener_detalles(articulo_id, tipo):
    conn = get_db_connection()
    if tipo == 'danadas':
        detalles = conn.execute('SELECT descripcion, fecha_dano FROM danos WHERE articulo_id = ? ORDER BY id DESC', (articulo_id,)).fetchall()
    else:
        detalles = conn.execute('SELECT cliente, ubicacion, (fecha_entrega || " " || hora_entrega) as tiempo, estado FROM alquileres WHERE articulo_id = ? AND estado NOT LIKE "Retirado%"', (articulo_id,)).fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in detalles])

# --- GESTIÓN DE STOCK ---
@app.route('/api/agregar_stock', methods=['POST'])
def agregar_stock():
    conn = get_db_connection()
    conn.execute('UPDATE inventario SET total = total + ? WHERE id = ?', 
                 (request.form.get('cantidad'), request.form.get('id')))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))
@app.route('/api/eventos_calendario')
def eventos_calendario():
    conn = get_db_connection()
    # Traemos los datos clave para el calendario
    pedidos = conn.execute('''
        SELECT a.*, i.nombre as art_nom 
        FROM alquileres a 
        JOIN inventario i ON a.articulo_id = i.id
    ''').fetchall()
    conn.close()

    eventos = []
    for p in pedidos:
        eventos.append({
            'title': f"{p['cliente']} ({p['art_nom']})",
            'start': p['fecha_entrega'],
            'end': p['fecha_retiro'],
            'extendedProps': {
                'cliente': p['cliente'],
                'ubicacion': p['ubicacion'],
                'entrega': f"{p['fecha_entrega']} {p['hora_entrega']}",
                'retiro': f"{p['fecha_retiro']} {p['hora_retiro']}",
                'estado': p['estado'],
                'articulo': f"{p['cantidad']}x {p['art_nom']}"
            },
            'color': '#7d5fff' if "Por entregar" in p['estado'] else '#2ecc71'
        })
    return jsonify(eventos)

if __name__ == '__main__':
    app.run(debug=True)