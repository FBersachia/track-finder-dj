# app/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, MainGenero, SubGenero, Mood, Artista, Cancion
from sqlalchemy.orm import joinedload
from sqlalchemy import or_ # Añade 'or_' a las importaciones de sqlalchemy



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
    """Página principal que lista todas las canciones y prepara los filtros."""
    songs = Cancion.query.options(
        joinedload(Cancion.artista_principal),
        joinedload(Cancion.sub_genero).joinedload(SubGenero.main_genero),
        joinedload(Cancion.mood),
        joinedload(Cancion.artistas_featuring)
    ).order_by(Cancion.nombre).all()

    # También cargamos los datos para los dropdowns de los filtros
    artistas = Artista.query.order_by(Artista.nombre).all()
    sub_generos = SubGenero.query.join(MainGenero).order_by(MainGenero.nombre, SubGenero.nombre).all()
    moods = Mood.query.order_by(Mood.nombre).all()
    
    return render_template('list_songs.html', songs=songs, artistas=artistas, sub_generos=sub_generos, moods=moods)


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

@main.route('/song/search')
def search_songs():
    """Esta ruta es llamada por HTMX para filtrar las canciones."""
    q = request.args.get('q')
    artist_id = request.args.get('artist_id')
    sub_genero_id = request.args.get('sub_genero_id')
    mood_id = request.args.get('mood_id')

    # Empezamos con una consulta base
    query = Cancion.query.options(
        joinedload(Cancion.artista_principal),
        joinedload(Cancion.sub_genero).joinedload(SubGenero.main_genero),
        joinedload(Cancion.mood),
        joinedload(Cancion.artistas_featuring)
    )

    # Aplicamos filtros dinámicamente
    if q:
        query = query.filter(or_(Cancion.nombre.ilike(f'%{q}%'), Cancion.keywords.ilike(f'%{q}%')))
    if artist_id:
        query = query.filter(Cancion.artista_principal_id == artist_id)
    if sub_genero_id:
        query = query.filter(Cancion.sub_genero_id == sub_genero_id)
    if mood_id:
        query = query.filter(Cancion.mood_id == mood_id)
    
    songs = query.order_by(Cancion.nombre).all()

    # Devolvemos SÓLO el parcial, no la página completa
    return render_template('_song_rows.html', songs=songs)

@main.route('/song/edit/<int:id>', methods=['GET', 'POST'])
def edit_song(id):
    """Maneja la edición de una canción existente."""
    song = Cancion.query.get_or_404(id)

    if request.method == 'POST':
        # Actualizar los datos del objeto 'song' con los datos del formulario
        song.nombre = request.form.get('nombre')
        song.año = request.form.get('año') or None
        song.keywords = request.form.get('keywords')
        song.ubicacion = request.form.get('ubicacion')
        song.artista_principal_id = request.form.get('artista_principal_id')
        song.sub_genero_id = request.form.get('sub_genero_id') or None
        song.mood_id = request.form.get('mood_id') or None
        
        # Actualizar la relación muchos-a-muchos
        featuring_ids = request.form.getlist('featuring_ids')
        song.artistas_featuring.clear() # Limpiamos la lista actual
        if featuring_ids:
            artistas_ft = Artista.query.filter(Artista.id_artista.in_(featuring_ids)).all()
            song.artistas_featuring = artistas_ft

        db.session.commit() # Guardamos los cambios en la BD
        return redirect(url_for('main.list_songs'))

    # Para el método GET, preparamos los datos para los dropdowns
    artistas = Artista.query.order_by(Artista.nombre).all()
    sub_generos = SubGenero.query.join(MainGenero).order_by(MainGenero.nombre, SubGenero.nombre).all()
    moods = Mood.query.order_by(Mood.nombre).all()

    # Renderizamos el mismo formulario, pero pasándole el objeto 'song'
    return render_template('song_form.html', song=song, artistas=artistas, sub_generos=sub_generos, moods=moods)