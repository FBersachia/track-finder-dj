# run.py

from app import create_app

# Creamos una instancia de la aplicación llamando a nuestra fábrica
app = create_app()

if __name__ == '__main__':
    # El modo debug activa el recargado automático y muestra errores detallados en el navegador
    app.run(debug=True)