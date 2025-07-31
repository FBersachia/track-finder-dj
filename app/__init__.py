# app/__init__.py

from flask import Flask
from .models import db
from .routes import main as main_blueprint

def create_app():
    """Crea y configura una instancia de la aplicación Flask."""
    app = Flask(__name__)

    # --- Configuración de la Base de Datos ---
    # Reemplaza 'usuario', 'contraseña', 'host' y 'nombre_db' con tus datos de MySQL.
    # El formato es: mysql+pymysql://usuario:contraseña@host/nombre_db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://francisco:mce775Mysql@localhost/track_finder_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Recomendado para desactivar notificaciones innecesarias

    # Inicializa la base de datos con la aplicación
    db.init_app(app)

    # Registra el Blueprint que contiene nuestras rutas
    app.register_blueprint(main_blueprint)

    return app