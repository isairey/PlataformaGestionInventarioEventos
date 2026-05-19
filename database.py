import sqlite3

def init_db():
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()

    # 1. Crear tabla de inventario con columna PRECIO
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            total INTEGER NOT NULL,
            precio REAL DEFAULT 0
        )
    ''')

    # 2. Insertar o actualizar los productos con sus precios
    productos = [
        ('Sillas', 100, 1.00),
        ('Mesas', 50, 5.00),
        ('Toldas', 10, 25.00)
    ]

    for nombre, cant, precio in productos:
        # Esto busca si ya existe el producto; si existe, actualiza el precio
        cursor.execute('''
            INSERT INTO inventario (nombre, total, precio) 
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET precio = excluded.precio
        ''', (nombre, cant, precio))
        
        # Por si ya tenías la tabla creada sin precios, forzamos la actualización por nombre
        cursor.execute('UPDATE inventario SET precio = ? WHERE nombre = ?', (precio, nombre))

    # 3. Asegurar que las otras tablas existen (Alquileres y Daños)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alquileres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            articulo_id INTEGER,
            cliente TEXT,
            telefono TEXT,
            ubicacion TEXT,
            cantidad INTEGER,
            fecha_entrega TEXT,
            hora_entrega TEXT,
            fecha_retiro TEXT,
            hora_retiro TEXT,
            estado TEXT,
            FOREIGN KEY(articulo_id) REFERENCES inventario(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS danos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            articulo_id INTEGER,
            descripcion TEXT,
            fecha_dano TEXT,
            FOREIGN KEY(articulo_id) REFERENCES inventario(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Base de datos actualizada con precios con éxito.")

if __name__ == "__main__":
    init_db()