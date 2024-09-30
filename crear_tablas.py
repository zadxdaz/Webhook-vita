import sqlite3
DATABASE = 'vita.db'

CREATE_TABLES_QUERY="""
-- Crear tabla de clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo TEXT NOT NULL,
    celular TEXT NOT NULL,
    direccion TEXT NOT NULL,
    estado_conversacion TEXT,
    producto_seleccionado TEXT
);

CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    precio REAL NOT NULL
);


-- Crear tabla de pedidos
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    estado TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);


-- (Opcional) Crear tabla de rutas
CREATE TABLE IF NOT EXISTS rutas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    direccion TEXT NOT NULL,
    fecha_ruta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
);
"""

# Función para conectar a la base de datos y ejecutar la query
def inicializar_db():
    # Conectar a la base de datos (se crea el archivo si no existe)
    conexion = sqlite3.connect(DATABASE)
    
    # Crear un cursor para ejecutar las queries
    cursor = conexion.cursor()
    
    # Ejecutar el script de creación de tablas
    cursor.executescript(CREATE_TABLES_QUERY)
    
    # Confirmar los cambios en la base de datos
    conexion.commit()
    
    # Cerrar la conexión
    conexion.close()

# Ejecutar la función para inicializar la base de datos
if __name__ == '__main__':
    inicializar_db()
    print("Tablas creadas con éxito.")