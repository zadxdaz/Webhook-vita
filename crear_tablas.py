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

CREATE TABLE IF NOT EXISTS mensajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    whatsapp_id TEXT NOT NULL,
    message TEXT NOT NULL,
    direction TEXT NOT NULL, -- 'sent' or 'received'
    timestamp TEXT NOT NULL,
    type TEXT NOT NULL -- 'text', 'image', etc.
);

CREATE TABLE client_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE list_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER,
    client_id INTEGER,
    FOREIGN KEY (list_id) REFERENCES client_lists(id),
    FOREIGN KEY (client_id) REFERENCES clientes(id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    amount REAL NOT NULL,
    description TEXT,
    date TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clientes(id)
);

CREATE TABLE IF NOT EXISTS hojas_de_ruta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT DEFAULT CURRENT_TIMESTAMP,
    estado TEXT DEFAULT 'on delivery'
);

CREATE TABLE IF NOT EXISTS hojas_de_ruta_pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hoja_de_ruta_id INTEGER,
    pedido_id INTEGER,
    posicion INTEGER,
    estado TEXT DEFAULT 'on delivery',
    FOREIGN KEY (hoja_de_ruta_id) REFERENCES hojas_de_ruta(id),
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);

CREATE VIEW hoja_de_ruta_detalle AS
SELECT hdp.hoja_de_ruta_id,  -- Include hoja_de_ruta_id for filtering
       p.id AS pedido_id, 
       c.nombre_completo AS cliente, 
       pro.nombre AS producto, 
       p.cantidad, 
       c.direccion AS ubicacion, 
       p.estado
FROM hojas_de_ruta_pedidos hdp
JOIN pedidos p ON hdp.pedido_id = p.id
JOIN clientes c ON p.cliente_id = c.id
JOIN productos pro ON p.producto_id = pro.id;



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