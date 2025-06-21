from flask import Flask, request, jsonify, g
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

# --- 1. Configuración de la Aplicación Flask ---
app = Flask(__name__)
auth = HTTPBasicAuth()
DATABASE = 'database.db'



# --- 2. Funciones para la Base de Datos ---

# Función para conectar a la base de datos
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row 
    return db

# Función para cerrar la conexión de la base de datos cuando la aplicación termine
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Función para inicializar la base de datos (crear tablas si no existen)
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                contrasena TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descripcion TEXT,
                completada BOOLEAN DEFAULT 0,
                usuario_id INTEGER,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        db.commit()
    print("Base de datos inicializada correctamente.")



# --- 3. Autenticación de Usuarios ---

@auth.verify_password
def verify_password(username, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (username,))
    user = cursor.fetchone()
    if user and check_password_hash(user['contrasena'], password):
        g.user = user # Almacenamos el usuario en 'g' para usarlo en otras rutas
        return True
    return False

# Manejo de errores de autenticación
@auth.error_handler
def auth_error():
    return jsonify({"mensaje": "Acceso no autorizado. Credenciales inválidas."}), 401



# --- 4. Endpoints de la API ---

# 4.1. Registro de Usuarios
@app.route('/registro', methods=['POST'])
def registro():
    data = request.get_json()
    usuario = data.get('usuario')
    contrasena = data.get('contrasena')

    if not usuario or not contrasena:
        return jsonify({"mensaje": "Usuario y contraseña son requeridos"}), 400

    db = get_db()
    cursor = db.cursor()

    try:
        hashed_password = generate_password_hash(contrasena)
        cursor.execute("INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)", (usuario, hashed_password))
        db.commit()
        return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"mensaje": "El usuario ya existe"}), 409

# 4.2. Inicio de Sesión
@app.route('/login', methods=['POST'])
@auth.login_required
def login():
    return jsonify({"mensaje": f"Inicio de sesión exitoso para {g.user['usuario']}. ¡Bienvenido!"})

# 4.3. Gestión de Tareas (GET /tareas)
@app.route('/tareas', methods=['GET'])
@auth.login_required
def obtener_tareas():
    return """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Bienvenida a la Gestión de Tareas</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 50px; text-align: center; background-color: #f4f4f4; }}
                h1 {{ color: #333; }}
                p {{ color: #666; }}
                .container {{ background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>¡Bienvenido/a al Sistema de Gestión de Tareas!</h1>
                <p>Has accedido exitosamente a la sección de tareas.</p>
                <p>Aquí es donde eventualmente se podrían gestionar las tareas.</p>
                <p>Usuario autenticado: <strong>{}</strong></p>
            </div>
        </body>
        </html>
    """.format(g.user['usuario'])


# --- 5. Punto de entrada de la aplicación ---
if __name__ == '__main__':
    init_db()
    app.run(debug=True) 