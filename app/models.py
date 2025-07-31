# app/models.py

from flask_sqlalchemy import SQLAlchemy

# Creamos una instancia de SQLAlchemy que se vinculará a nuestra app de Flask más adelante.
db = SQLAlchemy()

# Tabla Pivote (Asociación) para la relación muchos-a-muchos entre Cancion y Artista (featuring)
# No es una clase/modelo porque no tiene datos adicionales más allá de las claves foráneas.
cancion_artista_featuring = db.Table('cancion_artista_featuring',
    db.Column('cancion_id', db.Integer, db.ForeignKey('cancion.id_cancion'), primary_key=True),
    db.Column('artista_id', db.Integer, db.ForeignKey('artista.id_artista'), primary_key=True)
)

class MainGenero(db.Model):
    __tablename__ = 'main_genero'
    id_main_genero = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relación uno-a-muchos: Un género principal puede tener muchos subgéneros.
    sub_generos = db.relationship('SubGenero', back_populates='main_genero', cascade="all, delete-orphan")

class SubGenero(db.Model):
    __tablename__ = 'sub_genero'
    id_sub_genero = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    id_main_genero = db.Column(db.Integer, db.ForeignKey('main_genero.id_main_genero'), nullable=False)
    
    # Relación inversa (muchos-a-uno) que nos permite acceder al MainGenero desde un SubGenero.
    main_genero = db.relationship('MainGenero', back_populates='sub_generos')

class Mood(db.Model):
    __tablename__ = 'mood'
    id_mood = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

class Artista(db.Model):
    __tablename__ = 'artista'
    id_artista = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False, unique=True)

    # Relación para las canciones donde es el artista principal.
    canciones_principales = db.relationship('Cancion', back_populates='artista_principal', foreign_keys='Cancion.artista_principal_id')
    
    # Relación para las colaboraciones (muchos-a-muchos).
    canciones_featuring = db.relationship('Cancion', secondary=cancion_artista_featuring, back_populates='artistas_featuring')

class Cancion(db.Model):
    __tablename__ = 'cancion'
    id_cancion = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    año = db.Column(db.Integer)
    keywords = db.Column(db.String(255))
    ubicacion = db.Column(db.String(1024), nullable=False)
    
    # Claves Foráneas
    artista_principal_id = db.Column(db.Integer, db.ForeignKey('artista.id_artista'))
    sub_genero_id = db.Column(db.Integer, db.ForeignKey('sub_genero.id_sub_genero'))
    mood_id = db.Column(db.Integer, db.ForeignKey('mood.id_mood'))

    # Relaciones que nos permiten acceder a los objetos completos.
    artista_principal = db.relationship('Artista', back_populates='canciones_principales', foreign_keys=[artista_principal_id])
    sub_genero = db.relationship('SubGenero')
    mood = db.relationship('Mood')
    
    # Relación muchos-a-muchos con los artistas colaboradores (featuring).
    artistas_featuring = db.relationship('Artista', secondary=cancion_artista_featuring, back_populates='canciones_featuring')