# app/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, MainGenero, SubGenero, Mood, Artista, Cancion
from sqlalchemy.orm import joinedload


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

# --- RUTAS PARA CANCIONES ---

@main.route('/song')
def list_songs():
    """Página principal que listará todas las canciones. (La implementaremos después)"""
     # Usamos joinedload para cargar eficientemente los datos relacionados y evitar múltiples consultas
    songs = Cancion.query.options(
        joinedload(Cancion.artista_principal),
        joinedload(Cancion.sub_genero).joinedload(SubGenero.main_genero),
        joinedload(Cancion.mood),
        joinedload(Cancion.artistas_featuring)
    ).order_by(Cancion.nombre).all()
    return render_template('list_songs.html', songs=songs)


@main.route('/song/add', methods=['GET', 'POST'])
def add_song():
    """Maneja la creación de nuevas canciones."""
    if request.method == 'POST':
        # 1. Obtener todos los datos del formulario
        nombre = request.form.get('nombre')
        año = request.form.get('año')
        keywords = request.form.get('keywords')
        ubicacion = request.form.get('ubicacion')
        artista_principal_id = request.form.get('artista_principal_id')
        sub_genero_id = request.form.get('sub_genero_id')
        mood_id = request.form.get('mood_id')
        featuring_ids = request.form.getlist('featuring_ids')

        # --- ### CORRECCIÓN ### ---
        # Convertimos las cadenas vacías de los campos opcionales a None
        # para que la base de datos las acepte como valores NULL.
        if not año:
            año = None
        if not sub_genero_id:
            sub_genero_id = None
        if not mood_id:
            mood_id = None
        # -------------------------

        # 2. Crear la nueva instancia de Cancion
        nueva_cancion = Cancion(
            nombre=nombre,
            año=año,
            keywords=keywords,
            ubicacion=ubicacion,
            artista_principal_id=artista_principal_id,
            sub_genero_id=sub_genero_id,
            mood_id=mood_id
        )

        # 3. Manejar la relación muchos-a-muchos (featuring)
        if featuring_ids:
            artistas_ft = Artista.query.filter(Artista.id_artista.in_(featuring_ids)).all()
            nueva_cancion.artistas_featuring = artistas_ft
        
        # 4. Guardar en la base de datos
        db.session.add(nueva_cancion)
        db.session.commit()
        
        return redirect(url_for('main.list_songs'))

    # Para el método GET, necesitamos pasar todos los datos para los dropdowns
    artistas = Artista.query.order_by(Artista.nombre).all()
    sub_generos = SubGenero.query.join(MainGenero).order_by(MainGenero.nombre, SubGenero.nombre).all()
    moods = Mood.query.order_by(Mood.nombre).all()
    
    return render_template('song_form.html', artistas=artistas, sub_generos=sub_generos, moods=moods)