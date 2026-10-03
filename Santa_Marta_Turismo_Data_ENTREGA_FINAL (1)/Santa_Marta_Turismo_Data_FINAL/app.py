from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
app.secret_key = "santa-marta-turismo-data-2026"
DB_PATH = Path(__file__).with_name("turismo.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS categorias (
        id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_categoria TEXT NOT NULL UNIQUE,
        descripcion TEXT
    );

    CREATE TABLE IF NOT EXISTS lugares (
        id_lugar INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        id_categoria INTEGER NOT NULL,
        ubicacion TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        precio REAL NOT NULL DEFAULT 0 CHECK(precio >= 0),
        FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
    );

    CREATE TABLE IF NOT EXISTS visitas (
        id_visita INTEGER PRIMARY KEY AUTOINCREMENT,
        id_lugar INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        cantidad_personas INTEGER NOT NULL CHECK(cantidad_personas > 0),
        calificacion INTEGER NOT NULL CHECK(calificacion BETWEEN 1 AND 5),
        comentario TEXT,
        FOREIGN KEY (id_lugar) REFERENCES lugares(id_lugar) ON DELETE RESTRICT
    );
    """)

    if cur.execute("SELECT COUNT(*) FROM categorias").fetchone()[0] == 0:
        categorias = [
            ("Playas", "Sitios de sol y playa."),
            ("Naturaleza", "Parques, montañas y espacios naturales."),
            ("Historia", "Sitios históricos y patrimoniales."),
            ("Cultura", "Espacios culturales y tradicionales."),
            ("Gastronomía", "Experiencias relacionadas con comida local.")
        ]
        cur.executemany(
            "INSERT INTO categorias(nombre_categoria, descripcion) VALUES (?, ?)",
            categorias
        )

    if cur.execute("SELECT COUNT(*) FROM lugares").fetchone()[0] == 0:
        lugares = [
            ("Parque Tayrona", 2, "Santa Marta, Magdalena",
             "Parque natural reconocido por sus playas, senderos y biodiversidad.", 65000),
            ("Playa El Rodadero", 1, "El Rodadero, Santa Marta",
             "Una de las playas urbanas más conocidas de Santa Marta.", 0),
            ("Taganga", 1, "Taganga, Santa Marta",
             "Bahía tradicional de pescadores con actividades de playa y buceo.", 0),
            ("Quinta de San Pedro Alejandrino", 3, "Avenida del Libertador, Santa Marta",
             "Lugar histórico asociado a los últimos días de Simón Bolívar.", 23000),
            ("Museo del Oro Tairona", 4, "Centro Histórico, Santa Marta",
             "Museo dedicado al patrimonio arqueológico y cultural del Caribe colombiano.", 0),
            ("Centro Histórico", 4, "Centro de Santa Marta",
             "Zona de arquitectura colonial, plazas, restaurantes y vida cultural.", 0)
        ]
        cur.executemany("""
            INSERT INTO lugares(nombre, id_categoria, ubicacion, descripcion, precio)
            VALUES (?, ?, ?, ?, ?)
        """, lugares)

    if cur.execute("SELECT COUNT(*) FROM visitas").fetchone()[0] == 0:
        visitas = [
            (1, "2026-07-12", 3, 5, "Muy buena experiencia."),
            (1, "2026-08-05", 2, 5, "Paisajes excelentes."),
            (2, "2026-07-20", 4, 4, "Buena playa y fácil acceso."),
            (2, "2026-08-10", 2, 4, "Ambiente agradable."),
            (3, "2026-08-15", 3, 4, "Buen lugar para pasar la tarde."),
            (4, "2026-09-01", 2, 5, "Interesante para conocer la historia."),
            (5, "2026-09-12", 1, 5, "Muy educativo."),
            (6, "2026-09-18", 4, 4, "Bonito para caminar y conocer.")
        ]
        cur.executemany("""
            INSERT INTO visitas(id_lugar, fecha, cantidad_personas, calificacion, comentario)
            VALUES (?, ?, ?, ?, ?)
        """, visitas)

    conn.commit()
    conn.close()


def porcentaje(valor, maximo):
    if not maximo:
        return 0
    return round((valor / maximo) * 100, 2)


@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year}


@app.route("/")
def index():
    conn = get_db()
    destacados = conn.execute("""
        SELECT l.*, c.nombre_categoria,
               COALESCE(SUM(v.cantidad_personas), 0) AS total_visitantes,
               ROUND(AVG(v.calificacion), 1) AS promedio
        FROM lugares l
        JOIN categorias c ON c.id_categoria = l.id_categoria
        LEFT JOIN visitas v ON v.id_lugar = l.id_lugar
        GROUP BY l.id_lugar
        ORDER BY total_visitantes DESC, l.nombre
        LIMIT 3
    """).fetchall()

    resumen = conn.execute("""
        SELECT
            (SELECT COUNT(*) FROM lugares) AS lugares,
            (SELECT COUNT(*) FROM visitas) AS registros,
            (SELECT COALESCE(SUM(cantidad_personas), 0) FROM visitas) AS visitantes,
            (SELECT ROUND(AVG(calificacion), 2) FROM visitas) AS promedio
    """).fetchone()
    conn.close()
    return render_template("index.html", destacados=destacados, resumen=resumen)


@app.route("/lugares")
def lugares():
    categoria = request.args.get("categoria", type=int)
    conn = get_db()
    categorias = conn.execute("SELECT * FROM categorias ORDER BY nombre_categoria").fetchall()

    sql = """
        SELECT l.*, c.nombre_categoria,
               COALESCE(SUM(v.cantidad_personas), 0) AS total_visitantes,
               ROUND(AVG(v.calificacion), 1) AS promedio
        FROM lugares l
        JOIN categorias c ON c.id_categoria = l.id_categoria
        LEFT JOIN visitas v ON v.id_lugar = l.id_lugar
    """
    params = ()
    if categoria:
        sql += " WHERE l.id_categoria = ? "
        params = (categoria,)
    sql += " GROUP BY l.id_lugar ORDER BY l.nombre "

    datos = conn.execute(sql, params).fetchall()
    conn.close()
    return render_template("lugares.html", lugares=datos, categorias=categorias, categoria=categoria)


@app.route("/lugar/<int:id_lugar>")
def detalle(id_lugar):
    conn = get_db()
    lugar = conn.execute("""
        SELECT l.*, c.nombre_categoria,
               COALESCE(SUM(v.cantidad_personas), 0) AS total_visitantes,
               ROUND(AVG(v.calificacion), 1) AS promedio
        FROM lugares l
        JOIN categorias c ON c.id_categoria = l.id_categoria
        LEFT JOIN visitas v ON v.id_lugar = l.id_lugar
        WHERE l.id_lugar = ?
        GROUP BY l.id_lugar
    """, (id_lugar,)).fetchone()

    if not lugar:
        conn.close()
        return "Lugar no encontrado", 404

    opiniones = conn.execute("""
        SELECT fecha, cantidad_personas, calificacion, comentario
        FROM visitas
        WHERE id_lugar = ?
        ORDER BY fecha DESC, id_visita DESC
        LIMIT 8
    """, (id_lugar,)).fetchall()
    conn.close()
    return render_template("detalle.html", lugar=lugar, opiniones=opiniones)


@app.route("/visitas", methods=["GET", "POST"])
def visitas():
    conn = get_db()
    lugares = conn.execute("SELECT id_lugar, nombre FROM lugares ORDER BY nombre").fetchall()

    if request.method == "POST":
        id_lugar = request.form.get("id_lugar", type=int)
        fecha = request.form.get("fecha")
        cantidad = request.form.get("cantidad_personas", type=int)
        calificacion = request.form.get("calificacion", type=int)
        comentario = request.form.get("comentario", "").strip()

        if not id_lugar or not fecha or not cantidad or not calificacion:
            flash("Completa todos los campos obligatorios.", "error")
        elif cantidad < 1 or not 1 <= calificacion <= 5:
            flash("Verifica la cantidad de personas y la calificación.", "error")
        else:
            existe = conn.execute("SELECT 1 FROM lugares WHERE id_lugar = ?", (id_lugar,)).fetchone()
            if not existe:
                flash("El lugar seleccionado no existe.", "error")
            else:
                conn.execute("""
                    INSERT INTO visitas(id_lugar, fecha, cantidad_personas, calificacion, comentario)
                    VALUES (?, ?, ?, ?, ?)
                """, (id_lugar, fecha, cantidad, calificacion, comentario))
                conn.commit()
                conn.close()
                flash("Visita registrada correctamente. Las estadísticas ya fueron actualizadas.", "success")
                return redirect(url_for("visitas"))

    ultimas = conn.execute("""
        SELECT v.*, l.nombre
        FROM visitas v
        JOIN lugares l ON l.id_lugar = v.id_lugar
        ORDER BY v.fecha DESC, v.id_visita DESC
        LIMIT 10
    """).fetchall()
    conn.close()
    return render_template("visitas.html", lugares=lugares, ultimas=ultimas)


@app.route("/estadisticas")
def estadisticas():
    conn = get_db()

    por_lugar = [dict(x) for x in conn.execute("""
        SELECT l.nombre, COALESCE(SUM(v.cantidad_personas), 0) AS total
        FROM lugares l
        LEFT JOIN visitas v ON v.id_lugar = l.id_lugar
        GROUP BY l.id_lugar
        ORDER BY total DESC, l.nombre
    """).fetchall()]

    por_categoria = [dict(x) for x in conn.execute("""
        SELECT c.nombre_categoria AS categoria,
               COALESCE(SUM(v.cantidad_personas), 0) AS total
        FROM categorias c
        LEFT JOIN lugares l ON l.id_categoria = c.id_categoria
        LEFT JOIN visitas v ON v.id_lugar = l.id_lugar
        GROUP BY c.id_categoria
        ORDER BY total DESC, c.nombre_categoria
    """).fetchall()]

    calificaciones = conn.execute("""
        SELECT l.nombre,
               ROUND(AVG(v.calificacion), 2) AS promedio,
               COUNT(v.id_visita) AS cantidad
        FROM lugares l
        LEFT JOIN visitas v ON v.id_lugar = l.id_lugar
        GROUP BY l.id_lugar
        ORDER BY promedio DESC, l.nombre
    """).fetchall()

    por_mes = [dict(x) for x in conn.execute("""
        SELECT substr(fecha, 1, 7) AS mes,
               SUM(cantidad_personas) AS total
        FROM visitas
        GROUP BY substr(fecha, 1, 7)
        ORDER BY mes
    """).fetchall()]

    indicadores = conn.execute("""
        SELECT
            COALESCE(SUM(cantidad_personas), 0) AS visitantes,
            ROUND(AVG(calificacion), 2) AS promedio,
            COUNT(*) AS registros
        FROM visitas
    """).fetchone()

    conn.close()

    max_lugar = max([x["total"] for x in por_lugar], default=0)
    max_categoria = max([x["total"] for x in por_categoria], default=0)
    max_mes = max([x["total"] for x in por_mes], default=0)

    for x in por_lugar:
        x["porcentaje"] = porcentaje(x["total"], max_lugar)
    for x in por_categoria:
        x["porcentaje"] = porcentaje(x["total"], max_categoria)
    for x in por_mes:
        x["porcentaje"] = porcentaje(x["total"], max_mes)

    return render_template(
        "estadisticas.html",
        por_lugar=por_lugar,
        por_categoria=por_categoria,
        calificaciones=calificaciones,
        por_mes=por_mes,
        indicadores=indicadores
    )


@app.route("/administrar")
def administrar():
    conn = get_db()
    datos = conn.execute("""
        SELECT l.*, c.nombre_categoria
        FROM lugares l
        JOIN categorias c ON c.id_categoria = l.id_categoria
        ORDER BY l.nombre
    """).fetchall()
    conn.close()
    return render_template("administrar.html", lugares=datos)


@app.route("/administrar/nuevo", methods=["GET", "POST"])
def nuevo_lugar():
    conn = get_db()
    categorias = conn.execute("SELECT * FROM categorias ORDER BY nombre_categoria").fetchall()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        id_categoria = request.form.get("id_categoria", type=int)
        ubicacion = request.form.get("ubicacion", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        precio = request.form.get("precio", type=float)
        precio = 0 if precio is None else precio

        if not nombre or not id_categoria or not ubicacion or not descripcion or precio < 0:
            flash("Verifica los campos ingresados.", "error")
        else:
            conn.execute("""
                INSERT INTO lugares(nombre, id_categoria, ubicacion, descripcion, precio)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, id_categoria, ubicacion, descripcion, precio))
            conn.commit()
            conn.close()
            flash("Lugar creado correctamente.", "success")
            return redirect(url_for("administrar"))

    conn.close()
    return render_template("form_lugar.html", categorias=categorias, lugar=None, titulo="Nuevo lugar")


@app.route("/administrar/editar/<int:id_lugar>", methods=["GET", "POST"])
def editar_lugar(id_lugar):
    conn = get_db()
    categorias = conn.execute("SELECT * FROM categorias ORDER BY nombre_categoria").fetchall()
    lugar = conn.execute("SELECT * FROM lugares WHERE id_lugar = ?", (id_lugar,)).fetchone()

    if not lugar:
        conn.close()
        return "Lugar no encontrado", 404

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        id_categoria = request.form.get("id_categoria", type=int)
        ubicacion = request.form.get("ubicacion", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        precio = request.form.get("precio", type=float)
        precio = 0 if precio is None else precio

        if not nombre or not id_categoria or not ubicacion or not descripcion or precio < 0:
            flash("Verifica los campos ingresados.", "error")
        else:
            conn.execute("""
                UPDATE lugares
                SET nombre = ?, id_categoria = ?, ubicacion = ?, descripcion = ?, precio = ?
                WHERE id_lugar = ?
            """, (nombre, id_categoria, ubicacion, descripcion, precio, id_lugar))
            conn.commit()
            conn.close()
            flash("Lugar actualizado correctamente.", "success")
            return redirect(url_for("administrar"))

    conn.close()
    return render_template("form_lugar.html", categorias=categorias, lugar=lugar, titulo="Editar lugar")


@app.route("/administrar/eliminar/<int:id_lugar>", methods=["POST"])
def eliminar_lugar(id_lugar):
    conn = get_db()
    visitas = conn.execute(
        "SELECT COUNT(*) FROM visitas WHERE id_lugar = ?", (id_lugar,)
    ).fetchone()[0]

    if visitas > 0:
        flash("No se puede eliminar un lugar que tiene visitas registradas.", "error")
    else:
        conn.execute("DELETE FROM lugares WHERE id_lugar = ?", (id_lugar,))
        conn.commit()
        flash("Lugar eliminado correctamente.", "success")

    conn.close()
    return redirect(url_for("administrar"))


@app.route("/api/resumen")
def api_resumen():
    conn = get_db()
    datos = conn.execute("""
        SELECT l.nombre, COALESCE(SUM(v.cantidad_personas), 0) AS visitantes
        FROM lugares l
        LEFT JOIN visitas v ON v.id_lugar = l.id_lugar
        GROUP BY l.id_lugar
        ORDER BY visitantes DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(x) for x in datos])


# Permite que la base se cree tanto al ejecutar localmente como al desplegar.
init_db()

if __name__ == "__main__":
    app.run(debug=True)
