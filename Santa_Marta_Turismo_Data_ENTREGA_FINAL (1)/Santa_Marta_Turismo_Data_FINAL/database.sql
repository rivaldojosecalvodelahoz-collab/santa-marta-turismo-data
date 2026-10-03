PRAGMA foreign_keys = ON;

CREATE TABLE categorias (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_categoria TEXT NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE lugares (
    id_lugar INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    id_categoria INTEGER NOT NULL,
    ubicacion TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    precio REAL NOT NULL DEFAULT 0 CHECK(precio >= 0),
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
);

CREATE TABLE visitas (
    id_visita INTEGER PRIMARY KEY AUTOINCREMENT,
    id_lugar INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    cantidad_personas INTEGER NOT NULL CHECK(cantidad_personas > 0),
    calificacion INTEGER NOT NULL CHECK(calificacion BETWEEN 1 AND 5),
    comentario TEXT,
    FOREIGN KEY (id_lugar) REFERENCES lugares(id_lugar) ON DELETE RESTRICT
);
