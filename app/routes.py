# app/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, MainGenero, SubGenero, Mood, Artista

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

# --- RUTAS PARA MOODS ---

@main.route('/moods')
def list_moods():
    """Muestra una lista de todos los moods."""
    moods = Mood.query.order_by(Mood.nombre).all()
    return render_template('moods.html', moods=moods)

@main.route('/moods/add', methods=['GET', 'POST'])
def add_mood():
    """Maneja la creación de nuevos moods."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        
        # Evita crear moods duplicados
        if not Mood.query.filter_by(nombre=nombre).first():
            nuevo_mood = Mood(nombre=nombre)
            db.session.add(nuevo_mood)
            db.session.commit()
            
        return redirect(url_for('main.list_moods'))

    return render_template('mood_form.html')

@main.route('/moods/delete/<int:id>', methods=['POST'])
def delete_mood(id):
    """Elimina un mood."""
    mood = Mood.query.get_or_404(id)
    db.session.delete(mood)
    db.session.commit()
    return redirect(url_for('main.list_moods'))

# --- RUTAS PARA ARTISTAS (VERSIÓN CORREGIDA EN SINGULAR) ---

@main.route('/artist')
def list_artist(): # <--- Nombre de función en singular
    """Muestra una lista de todos los artistas."""
    artists = Artista.query.order_by(Artista.nombre).all()
    return render_template('artists.html', artists=artists)

@main.route('/artist/add', methods=['GET', 'POST'])
def add_artist():
    """Maneja la creación de nuevos artistas."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        
        if not Artista.query.filter_by(nombre=nombre).first():
            nuevo_artista = Artista(nombre=nombre)
            db.session.add(nuevo_artista)
            db.session.commit()
            
        return redirect(url_for('main.list_artist')) # <--- Redirección corregida

    return render_template('artist_form.html')

@main.route('/artist/delete/<int:id>', methods=['POST'])
def delete_artist(id):
    """Elimina un artista."""
    artista = Artista.query.get_or_404(id)
    db.session.delete(artista)
    db.session.commit()
    return redirect(url_for('main.list_artist')) # <--- Redirección corregida