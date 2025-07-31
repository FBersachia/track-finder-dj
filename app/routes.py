# app/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, MainGenero, SubGenero

# Creamos un Blueprint para organizar nuestras rutas
main = Blueprint('main', __name__)

@main.route('/genres')
def list_genres():
    """Muestra una lista de todos los géneros principales y sus subgéneros."""
    main_genres = MainGenero.query.order_by(MainGenero.nombre).all()
    return render_template('genres.html', main_genres=main_genres)

@main.route('/genres/add', methods=['GET', 'POST'])
def add_genre():
    """Maneja la creación de nuevos géneros (principales y subgéneros)."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        tipo = request.form.get('tipo')
        
        if tipo == 'main':
            nuevo_genero = MainGenero(nombre=nombre)
        else:
            main_genero_id = request.form.get('main_genero_id')
            nuevo_genero = SubGenero(nombre=nombre, id_main_genero=main_genero_id)
        
        db.session.add(nuevo_genero)
        db.session.commit()
        return redirect(url_for('main.list_genres'))

    # Para el método GET, necesitamos los géneros principales para el dropdown
    main_genres = MainGenero.query.order_by(MainGenero.nombre).all()
    return render_template('genre_form.html', main_genres=main_genres)

@main.route('/genres/delete/main/<int:id>', methods=['POST'])
def delete_main_genre(id):
    """Elimina un género principal."""
    genero = MainGenero.query.get_or_404(id)
    db.session.delete(genero)
    db.session.commit()
    return redirect(url_for('main.list_genres'))

@main.route('/genres/delete/sub/<int:id>', methods=['POST'])
def delete_sub_genre(id):
    """Elimina un subgénero."""
    genero = SubGenero.query.get_or_404(id)
    db.session.delete(genero)
    db.session.commit()
    return redirect(url_for('main.list_genres'))