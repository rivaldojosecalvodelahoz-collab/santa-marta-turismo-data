from flask import Flask, request, redirect, url_for, flash, Response
from markupsafe import Markup, escape
import sqlite3
import os
import csv
import io
from datetime import date
from statistics import mean

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "techmopau-demo-key")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "turismo.db")

DESTINOS = [
    {
        "slug": "rodadero",
        "nombre": "El Rodadero",
        "categoria": "Playa & familia",
        "icono": "☀",
        "descripcion": "Uno de los sectores turísticos más conocidos de Santa Marta, con playa, hoteles, restaurantes y actividades para visitantes.",
        "detalle": "El Rodadero combina servicios turísticos, comercio y playa. En el sistema se usa para analizar cantidad de visitas, gasto, satisfacción y razones de viaje.",
        "gradiente": "linear-gradient(135deg,#00b4d8,#90e0ef 55%,#ffd166)",
    },
    {
        "slug": "centro-historico",
        "nombre": "Centro Histórico",
        "categoria": "Cultura & patrimonio",
        "icono": "⌂",
        "descripcion": "Zona de arquitectura republicana, plazas, restaurantes y recorridos culturales en el corazón de la ciudad.",
        "detalle": "El Centro Histórico permite observar el comportamiento del turismo cultural, gastronómico y urbano, especialmente en temporadas de alta afluencia.",
        "gradiente": "linear-gradient(135deg,#f4a261,#e76f51 50%,#2a9d8f)",
    },
    {
        "slug": "taganga",
        "nombre": "Taganga",
        "categoria": "Mar & buceo",
        "icono": "≈",
        "descripcion": "Bahía tradicional cercana a Santa Marta, reconocida por actividades marinas, buceo y oferta gastronómica.",
        "detalle": "Taganga ayuda a comparar el turismo costero y las actividades de naturaleza con otros destinos de la ciudad.",
        "gradiente": "linear-gradient(135deg,#023e8a,#0077b6 55%,#48cae4)",
    },
    {
        "slug": "tayrona",
        "nombre": "Parque Tayrona",
        "categoria": "Naturaleza",
        "icono": "△",
        "descripcion": "Área natural protegida con playas, senderos y paisajes de gran interés para visitantes nacionales y extranjeros.",
        "detalle": "El Parque Tayrona representa el turismo de naturaleza y permite analizar patrones de gasto, satisfacción y procedencia de los visitantes.",
        "gradiente": "linear-gradient(135deg,#1b4332,#40916c 52%,#95d5b2)",
    },
    {
        "slug": "minca",
        "nombre": "Minca",
        "categoria": "Ecoturismo",
        "icono": "✦",
        "descripcion": "Destino de montaña con naturaleza, café, ríos y experiencias de descanso a pocos kilómetros de Santa Marta.",
        "detalle": "Minca permite estudiar el comportamiento de visitantes interesados en ecoturismo, descanso, gastronomía local y recorridos de montaña.",
        "gradiente": "linear-gradient(135deg,#386641,#6a994e 55%,#a7c957)",
    },
    {
        "slug": "playa-blanca",
        "nombre": "Playa Blanca",
        "categoria": "Sol & playa",
        "icono": "◒",
        "descripcion": "Playa de aguas claras a la que llegan turistas en recorridos marítimos desde diferentes sectores de la ciudad.",
        "detalle": "Playa Blanca ayuda a observar la demanda de experiencias de sol y playa y el nivel de satisfacción asociado a este tipo de visita.",
        "gradiente": "linear-gradient(135deg,#219ebc,#8ecae6 58%,#ffb703)",
    },
]

DESTINO_POR_NOMBRE = {d["nombre"]: d for d in DESTINOS}
DESTINO_POR_SLUG = {d["slug"]: d for d in DESTINOS}

SEED = [
    ("2026-01-12","El Rodadero","Nacional","Vacaciones",2,180000,4),
    ("2026-01-21","Centro Histórico","Nacional","Cultura",1,95000,5),
    ("2026-02-05","Taganga","Extranjero","Buceo",3,320000,5),
    ("2026-02-18","Minca","Nacional","Naturaleza",2,210000,4),
    ("2026-03-03","Parque Tayrona","Extranjero","Naturaleza",2,390000,5),
    ("2026-03-16","El Rodadero","Nacional","Vacaciones",4,280000,4),
    ("2026-04-02","Playa Blanca","Nacional","Vacaciones",3,240000,4),
    ("2026-04-19","Centro Histórico","Extranjero","Cultura",2,160000,5),
    ("2026-05-07","Minca","Extranjero","Naturaleza",2,270000,5),
    ("2026-05-23","Taganga","Nacional","Vacaciones",3,220000,4),
    ("2026-06-11","Parque Tayrona","Nacional","Naturaleza",4,450000,5),
    ("2026-06-26","El Rodadero","Nacional","Familia",5,360000,4),
    ("2026-07-04","El Rodadero","Extranjero","Vacaciones",2,310000,5),
    ("2026-07-15","Centro Histórico","Nacional","Gastronomía",2,140000,4),
    ("2026-07-28","Parque Tayrona","Extranjero","Naturaleza",3,520000,5),
    ("2026-08-09","Taganga","Extranjero","Buceo",2,350000,5),
    ("2026-08-17","Minca","Nacional","Descanso",2,200000,4),
    ("2026-08-29","Playa Blanca","Nacional","Vacaciones",4,300000,4),
    ("2026-09-05","Centro Histórico","Nacional","Cultura",1,85000,4),
    ("2026-09-14","El Rodadero","Nacional","Familia",3,260000,4),
    ("2026-09-20","Minca","Extranjero","Naturaleza",2,290000,5),
    ("2026-09-23","Parque Tayrona","Nacional","Naturaleza",2,410000,5),
    ("2026-09-27","Taganga","Nacional","Gastronomía",2,175000,4),
    ("2026-09-30","Playa Blanca","Extranjero","Vacaciones",2,285000,5),
]


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS visitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            destino TEXT NOT NULL,
            origen TEXT NOT NULL,
            motivo TEXT NOT NULL,
            personas INTEGER NOT NULL,
            gasto REAL NOT NULL,
            satisfaccion INTEGER NOT NULL
        )
        """
    )
    count = conn.execute("SELECT COUNT(*) FROM visitas").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO visitas(fecha,destino,origen,motivo,personas,gasto,satisfaccion) VALUES(?,?,?,?,?,?,?)",
            SEED,
        )
    conn.commit()
    conn.close()


def money(v):
    return "$" + f"{int(round(float(v))):,}".replace(",", ".")


def nav(active):
    items = [
        ("inicio", "Inicio", url_for("inicio")),
        ("lugares", "Lugares", url_for("lugares")),
        ("registro", "Registrar visita", url_for("registrar")),
        ("estadisticas", "Estadísticas", url_for("estadisticas")),
        ("datos", "Datos", url_for("datos")),
        ("acerca", "Acerca", url_for("acerca")),
    ]
    links = "".join(
        f'<a class="nav-link {"active" if key == active else ""}" href="{href}">{label}</a>'
        for key, label, href in items
    )
    return links


def page(title, active, body, extra_js=""):
    flashes = "".join(f'<div class="flash">{escape(msg)}</div>' for msg in _get_flashes())
    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · Techmopau</title>
<style>
:root{{--ink:#0b2031;--ink2:#19344a;--muted:#647586;--line:#dfe8ed;--bg:#f5f8f8;--card:#ffffff;--green:#0d8f72;--green2:#14b88e;--mint:#e7f7f2;--sand:#f4efe7;--shadow:0 18px 50px rgba(13,41,57,.09)}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Arial,sans-serif;background:var(--bg);color:var(--ink);line-height:1.55}}
a{{color:inherit;text-decoration:none}}button,input,select{{font:inherit}}
.shell{{max-width:1180px;margin:auto;padding:0 24px}}.topbar{{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.93);backdrop-filter:blur(18px);border-bottom:1px solid rgba(223,232,237,.8)}}
.nav{{height:78px;display:flex;align-items:center;justify-content:space-between;gap:24px}}.brand{{display:flex;align-items:center;gap:11px;font-weight:850;letter-spacing:-.3px}}.brandmark{{width:38px;height:38px;border-radius:13px;background:linear-gradient(145deg,#0d8f72,#1bc49b);display:grid;place-items:center;color:white;box-shadow:0 8px 22px rgba(13,143,114,.24)}}
.navlinks{{display:flex;align-items:center;gap:4px;flex-wrap:wrap;justify-content:flex-end}}.nav-link{{padding:10px 12px;border-radius:12px;color:#536675;font-size:14px;font-weight:700}}.nav-link:hover,.nav-link.active{{background:var(--mint);color:var(--green)}}
.hero{{padding:64px 0 50px;overflow:hidden;background:radial-gradient(circle at 80% 10%,rgba(20,184,142,.16),transparent 26%),radial-gradient(circle at 15% 65%,rgba(65,161,205,.12),transparent 25%),linear-gradient(180deg,#fff,#f5f8f8)}}
.hero-grid{{display:grid;grid-template-columns:1.08fr .92fr;gap:58px;align-items:center}}.eyebrow{{display:inline-flex;align-items:center;gap:8px;background:var(--mint);color:var(--green);border:1px solid #cfede4;padding:8px 12px;border-radius:999px;font-size:12px;font-weight:850;letter-spacing:.08em;text-transform:uppercase}}.dot{{width:8px;height:8px;border-radius:50%;background:var(--green2)}}
h1{{font-size:clamp(42px,6vw,72px);line-height:1.02;letter-spacing:-2.6px;margin:18px 0 20px;max-width:760px}}.lead{{font-size:18px;color:#607180;max-width:670px;margin:0 0 28px}}.actions{{display:flex;gap:12px;flex-wrap:wrap}}.btn{{border:none;border-radius:14px;padding:13px 18px;font-weight:800;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;gap:8px}}.btn-primary{{background:var(--ink);color:white;box-shadow:0 11px 28px rgba(11,32,49,.16)}}.btn-primary:hover{{transform:translateY(-1px)}}.btn-soft{{background:white;color:var(--ink);border:1px solid var(--line)}}
.visual{{position:relative;min-height:430px}}.visual-main{{position:absolute;inset:16px 0 0 44px;border-radius:30px;padding:26px;background:linear-gradient(145deg,#0c263a,#0d8f72 68%,#56d7b7);box-shadow:0 30px 70px rgba(18,67,83,.25);color:white;overflow:hidden}}.visual-main:after{{content:"";position:absolute;width:330px;height:330px;border-radius:50%;background:rgba(255,255,255,.08);right:-120px;top:-90px}}.visual-main:before{{content:"";position:absolute;width:240px;height:240px;border-radius:50%;border:1px solid rgba(255,255,255,.12);right:-30px;bottom:-95px}}.visual-title{{font-size:13px;text-transform:uppercase;letter-spacing:.13em;opacity:.8;font-weight:800}}.visual-number{{font-size:58px;font-weight:900;letter-spacing:-2px;margin-top:18px}}.visual-sub{{opacity:.83;margin-top:-8px}}.mini-chart{{display:flex;gap:10px;align-items:flex-end;height:110px;margin-top:52px}}.mini-chart span{{flex:1;background:rgba(255,255,255,.88);border-radius:7px 7px 2px 2px;min-height:18px}}.float-card{{position:absolute;left:0;bottom:22px;width:215px;background:white;border-radius:20px;padding:18px;box-shadow:var(--shadow);border:1px solid rgba(223,232,237,.8)}}.float-card strong{{display:block;font-size:29px;letter-spacing:-1px}}.float-card small{{color:var(--muted)}}
.section{{padding:58px 0}}.section.white{{background:white}}.section-head{{display:flex;align-items:end;justify-content:space-between;gap:20px;margin-bottom:26px}}.kicker{{color:var(--green);font-weight:850;text-transform:uppercase;font-size:12px;letter-spacing:.1em}}h2{{font-size:34px;line-height:1.1;letter-spacing:-1.2px;margin:6px 0 0}}.sub{{color:var(--muted);max-width:680px;margin:8px 0 0}}
.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}.metric{{background:white;border:1px solid var(--line);border-radius:22px;padding:22px;box-shadow:0 8px 30px rgba(13,41,57,.045)}}.metric-label{{font-size:13px;color:var(--muted);font-weight:700}}.metric-value{{font-size:30px;font-weight:900;letter-spacing:-1px;margin-top:6px}}.metric-note{{font-size:12px;color:#84939e;margin-top:4px}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}.place-card{{background:white;border:1px solid var(--line);border-radius:24px;overflow:hidden;box-shadow:0 12px 36px rgba(13,41,57,.055);transition:.2s}}.place-card:hover{{transform:translateY(-4px);box-shadow:0 22px 48px rgba(13,41,57,.11)}}.place-art{{height:185px;padding:18px;position:relative;overflow:hidden;color:white}}.place-art:after{{content:"";position:absolute;width:160px;height:160px;border-radius:50%;right:-35px;top:-48px;background:rgba(255,255,255,.15)}}.place-icon{{position:absolute;right:20px;bottom:11px;font-size:58px;font-weight:900;opacity:.75}}.tag{{display:inline-block;background:rgba(255,255,255,.88);color:#173346;border-radius:999px;padding:7px 10px;font-size:11px;font-weight:800}}.place-body{{padding:20px}}.place-body h3{{margin:0 0 6px;font-size:21px;letter-spacing:-.4px}}.place-body p{{margin:0;color:var(--muted);font-size:14px}}.place-foot{{display:flex;align-items:center;justify-content:space-between;margin-top:18px;font-size:13px;font-weight:800;color:var(--green)}}
.panel{{background:white;border:1px solid var(--line);border-radius:24px;padding:26px;box-shadow:0 12px 34px rgba(13,41,57,.055)}}.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}.grid-3{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}.form-grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}.field{{display:flex;flex-direction:column;gap:7px}}.field.full{{grid-column:1/-1}}label{{font-size:13px;font-weight:800;color:#304758}}input,select{{width:100%;padding:13px 14px;border-radius:13px;border:1px solid #d6e2e7;background:#fbfdfd;color:var(--ink);outline:none}}input:focus,select:focus{{border-color:#66cbb2;box-shadow:0 0 0 4px rgba(20,184,142,.09)}}.hint{{font-size:12px;color:#7c8d98}}.flash{{max-width:1180px;margin:16px auto 0;padding:12px 18px;border-radius:14px;background:#e7f7f2;color:#08765e;border:1px solid #c7eadf;font-weight:700}}
.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:18px}}table{{width:100%;border-collapse:collapse;background:white;min-width:800px}}th,td{{padding:14px 15px;text-align:left;border-bottom:1px solid #edf2f4;font-size:13px}}th{{background:#f8fbfb;color:#526774;font-size:11px;text-transform:uppercase;letter-spacing:.07em}}tr:last-child td{{border-bottom:none}}.pill{{display:inline-flex;padding:6px 9px;border-radius:999px;background:var(--mint);color:var(--green);font-weight:800;font-size:11px}}
.chart-card{{background:white;border:1px solid var(--line);border-radius:24px;padding:24px}}.chart-title{{font-weight:900;font-size:18px;margin-bottom:4px}}.chart-sub{{font-size:13px;color:var(--muted);margin-bottom:20px}}.bar-row{{display:grid;grid-template-columns:135px 1fr 66px;gap:10px;align-items:center;margin:12px 0}}.bar-label{{font-size:12px;font-weight:750;color:#415969;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.bar-track{{height:12px;background:#edf4f3;border-radius:999px;overflow:hidden}}.bar-fill{{height:100%;border-radius:999px;background:linear-gradient(90deg,#0d8f72,#27c49b)}}.bar-value{{font-size:12px;text-align:right;color:#647586;font-weight:800}}.svg-chart{{width:100%;height:180px;background:linear-gradient(180deg,#fbfdfd,#f6faf9);border-radius:18px;border:1px solid #edf3f2}}.legend{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px}}.legend-item{{display:flex;align-items:center;justify-content:space-between;gap:10px;font-size:12px;color:#5c707e}}.legend-item span:first-child{{display:flex;align-items:center;gap:8px}}.legend-dot{{width:9px;height:9px;border-radius:50%;display:inline-block;background:var(--green)}}
.callout{{background:linear-gradient(135deg,#0b2031,#15394d);color:white;border-radius:28px;padding:34px;position:relative;overflow:hidden}}.callout:after{{content:"";position:absolute;width:250px;height:250px;border-radius:50%;right:-70px;top:-90px;background:rgba(20,184,142,.18)}}.callout h3{{font-size:28px;margin:0 0 10px;letter-spacing:-.8px}}.callout p{{max-width:760px;color:#d1dde4;margin:0}}.stat-band{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:24px}}.stat-band div{{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.11);border-radius:16px;padding:15px}}.stat-band strong{{display:block;font-size:24px}}
.footer{{padding:34px 0 48px;color:#6d7d88;font-size:13px}}.footer-row{{display:flex;justify-content:space-between;gap:20px;border-top:1px solid var(--line);padding-top:26px}}.empty{{padding:40px;text-align:center;color:var(--muted)}}.detail-hero{{border-radius:28px;padding:38px;color:white;min-height:260px;display:flex;align-items:flex-end;position:relative;overflow:hidden}}.detail-hero:after{{content:"";position:absolute;width:300px;height:300px;border-radius:50%;right:-70px;top:-100px;background:rgba(255,255,255,.14)}}.detail-hero h1{{font-size:48px;margin:10px 0 5px;color:white}}.detail-hero p{{max-width:650px;margin:0;opacity:.9}}.back{{display:inline-flex;margin-bottom:15px;color:var(--green);font-weight:800}}
@media(max-width:900px){{.hero-grid,.grid-2{{grid-template-columns:1fr}}.visual{{min-height:360px}}.metrics{{grid-template-columns:1fr 1fr}}.cards{{grid-template-columns:1fr 1fr}}.nav{{height:auto;padding:14px 0;align-items:flex-start}}.navlinks{{max-width:70%}}}}
@media(max-width:640px){{.shell{{padding:0 16px}}.hero{{padding-top:42px}}h1{{font-size:43px;letter-spacing:-1.8px}}.visual-main{{inset:10px 0 0 20px}}.metrics,.cards,.grid-3,.form-grid{{grid-template-columns:1fr}}.field.full{{grid-column:auto}}.nav{{flex-direction:column}}.navlinks{{max-width:100%;justify-content:flex-start}}.bar-row{{grid-template-columns:105px 1fr 48px}}.stat-band{{grid-template-columns:1fr}}.footer-row{{flex-direction:column}}}}
</style>
</head>
<body>
<header class="topbar"><div class="shell nav"><a href="{url_for('inicio')}" class="brand"><span class="brandmark">T</span><span>Techmopau <span style="color:var(--green)">Turismo Data</span></span></a><nav class="navlinks">{nav(active)}</nav></div></header>
{flashes}
{body}
<footer class="footer"><div class="shell footer-row"><span>Proyecto de curso · Ingeniería de Datos</span><span>Python · Flask · SQLite · Techmopau.py</span></div></footer>
{extra_js}
</body></html>"""
    return html


def _get_flashes():
    from flask import get_flashed_messages
    return get_flashed_messages()


def summary_stats():
    conn = db()
    rows = conn.execute("SELECT * FROM visitas").fetchall()
    conn.close()
    if not rows:
        return {"registros": 0, "personas": 0, "gasto": 0, "sat": 0, "top": "Sin datos"}
    registros = len(rows)
    personas = sum(r["personas"] for r in rows)
    gasto = mean([r["gasto"] for r in rows])
    sat = mean([r["satisfaccion"] for r in rows])
    counts = {}
    for r in rows:
        counts[r["destino"]] = counts.get(r["destino"], 0) + r["personas"]
    top = max(counts, key=counts.get)
    return {"registros": registros, "personas": personas, "gasto": gasto, "sat": sat, "top": top}


def destination_metrics(nombre):
    conn = db()
    rows = conn.execute("SELECT * FROM visitas WHERE destino=?", (nombre,)).fetchall()
    conn.close()
    if not rows:
        return {"personas":0,"gasto":0,"sat":0,"registros":0}
    return {
        "personas": sum(r["personas"] for r in rows),
        "gasto": mean([r["gasto"] for r in rows]),
        "sat": mean([r["satisfaccion"] for r in rows]),
        "registros": len(rows),
    }


def metrics_html(stats):
    return f"""
    <div class="metrics">
      <div class="metric"><div class="metric-label">Personas registradas</div><div class="metric-value">{stats['personas']}</div><div class="metric-note">Suma de visitantes en la base de datos</div></div>
      <div class="metric"><div class="metric-label">Gasto promedio</div><div class="metric-value">{money(stats['gasto'])}</div><div class="metric-note">Promedio por registro de visita</div></div>
      <div class="metric"><div class="metric-label">Satisfacción</div><div class="metric-value">{stats['sat']:.1f}/5</div><div class="metric-note">Valoración promedio del visitante</div></div>
      <div class="metric"><div class="metric-label">Destino destacado</div><div class="metric-value" style="font-size:23px">{escape(stats['top'])}</div><div class="metric-note">Mayor cantidad de personas registradas</div></div>
    </div>"""


def places_cards(limit=None):
    items = DESTINOS[:limit] if limit else DESTINOS
    cards = []
    for d in items:
        m = destination_metrics(d["nombre"])
        cards.append(f"""
        <a class="place-card" href="{url_for('detalle_lugar', slug=d['slug'])}">
          <div class="place-art" style="background:{d['gradiente']}"><span class="tag">{escape(d['categoria'])}</span><span class="place-icon">{d['icono']}</span></div>
          <div class="place-body"><h3>{escape(d['nombre'])}</h3><p>{escape(d['descripcion'])}</p><div class="place-foot"><span>{m['personas']} personas registradas</span><span>Ver →</span></div></div>
        </a>""")
    return "".join(cards)


@app.route("/")
def inicio():
    stats = summary_stats()
    body = f"""
    <section class="hero"><div class="shell hero-grid">
      <div><span class="eyebrow"><span class="dot"></span> Sistema de información turística</span><h1>Descubre Santa Marta a través de sus datos.</h1><p class="lead">Una aplicación web sencilla para registrar visitas, organizar información turística y convertir los datos en indicadores útiles para comprender el comportamiento de los visitantes.</p><div class="actions"><a class="btn btn-primary" href="{url_for('estadisticas')}">Ver estadísticas →</a><a class="btn btn-soft" href="{url_for('registrar')}">Registrar una visita</a></div></div>
      <div class="visual"><div class="visual-main"><div class="visual-title">Panel turístico · 2026</div><div class="visual-number">{stats['personas']}</div><div class="visual-sub">personas analizadas</div><div class="mini-chart"><span style="height:39%"></span><span style="height:62%"></span><span style="height:51%"></span><span style="height:78%"></span><span style="height:66%"></span><span style="height:94%"></span></div></div><div class="float-card"><small>Satisfacción promedio</small><strong>{stats['sat']:.1f}/5</strong><small>Basada en registros del sistema</small></div></div>
    </div></section>
    <section class="section"><div class="shell"><div class="section-head"><div><div class="kicker">Indicadores</div><h2>Resumen del sistema</h2><p class="sub">Los datos se actualizan automáticamente cuando se registra una nueva visita.</p></div></div>{metrics_html(stats)}</div></section>
    <section class="section white"><div class="shell"><div class="section-head"><div><div class="kicker">Explora</div><h2>Destinos analizados</h2><p class="sub">Una selección de lugares turísticos de Santa Marta incluidos en el sistema.</p></div><a class="btn btn-soft" href="{url_for('lugares')}">Ver todos</a></div><div class="cards">{places_cards()}</div></div></section>
    <section class="section"><div class="shell"><div class="callout"><h3>De registros simples a información útil.</h3><p>El proyecto combina captura de datos, almacenamiento en SQLite y visualización estadística para identificar tendencias de demanda, gasto y satisfacción en diferentes destinos turísticos.</p><div class="stat-band"><div><small>Vistas principales</small><strong>6</strong></div><div><small>Reportes estadísticos</small><strong>5+</strong></div><div><small>Tecnología</small><strong>Python</strong></div></div></div></div></section>
    """
    return page("Inicio", "inicio", body)


@app.route("/lugares")
def lugares():
    body = f"""<section class="section"><div class="shell"><div class="section-head"><div><div class="kicker">Vista 2</div><h2>Lugares turísticos</h2><p class="sub">Destinos incluidos para registrar y analizar el comportamiento de visitantes en Santa Marta.</p></div></div><div class="cards">{places_cards()}</div></div></section>"""
    return page("Lugares", "lugares", body)


@app.route("/lugares/<slug>")
def detalle_lugar(slug):
    d = DESTINO_POR_SLUG.get(slug)
    if not d:
        return redirect(url_for("lugares"))
    m = destination_metrics(d["nombre"])
    body = f"""
    <section class="section"><div class="shell"><a class="back" href="{url_for('lugares')}">← Volver a lugares</a><div class="detail-hero" style="background:{d['gradiente']}"><div style="position:relative;z-index:2"><span class="tag">{escape(d['categoria'])}</span><h1>{escape(d['nombre'])}</h1><p>{escape(d['detalle'])}</p></div></div></div></section>
    <section class="section white"><div class="shell"><div class="metrics"><div class="metric"><div class="metric-label">Personas</div><div class="metric-value">{m['personas']}</div></div><div class="metric"><div class="metric-label">Registros</div><div class="metric-value">{m['registros']}</div></div><div class="metric"><div class="metric-label">Gasto promedio</div><div class="metric-value">{money(m['gasto'])}</div></div><div class="metric"><div class="metric-label">Satisfacción</div><div class="metric-value">{m['sat']:.1f}/5</div></div></div></div></section>
    """
    return page(d["nombre"], "lugares", body)


@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        try:
            fecha = request.form.get("fecha", "").strip()
            destino = request.form.get("destino", "").strip()
            origen = request.form.get("origen", "").strip()
            motivo = request.form.get("motivo", "").strip()
            personas = int(request.form.get("personas", "0"))
            gasto = float(request.form.get("gasto", "0"))
            satisfaccion = int(request.form.get("satisfaccion", "0"))
            if not fecha or destino not in DESTINO_POR_NOMBRE or not origen or not motivo:
                raise ValueError("Faltan datos obligatorios")
            if personas < 1 or gasto < 0 or satisfaccion not in range(1, 6):
                raise ValueError("Valores fuera de rango")
            conn = db()
            conn.execute("INSERT INTO visitas(fecha,destino,origen,motivo,personas,gasto,satisfaccion) VALUES(?,?,?,?,?,?,?)", (fecha,destino,origen,motivo,personas,gasto,satisfaccion))
            conn.commit(); conn.close()
            flash("Visita registrada correctamente. Los indicadores ya fueron actualizados.")
            return redirect(url_for("estadisticas"))
        except Exception:
            flash("No fue posible guardar el registro. Revisa los datos ingresados.")
    options = "".join(f'<option value="{escape(d["nombre"])}">{escape(d["nombre"])}</option>' for d in DESTINOS)
    today = date.today().isoformat()
    body = f"""
    <section class="section"><div class="shell"><div class="section-head"><div><div class="kicker">Vista 3</div><h2>Registrar una visita</h2><p class="sub">Agrega un registro para alimentar la base de datos y actualizar automáticamente los reportes.</p></div></div>
    <div class="grid-2"><div class="panel"><form method="post" class="form-grid">
      <div class="field"><label>Fecha de la visita</label><input type="date" name="fecha" value="{today}" required></div>
      <div class="field"><label>Destino</label><select name="destino" required><option value="">Selecciona un destino</option>{options}</select></div>
      <div class="field"><label>Origen del visitante</label><select name="origen" required><option>Nacional</option><option>Extranjero</option><option>Local</option></select></div>
      <div class="field"><label>Motivo principal</label><select name="motivo" required><option>Vacaciones</option><option>Naturaleza</option><option>Cultura</option><option>Familia</option><option>Gastronomía</option><option>Buceo</option><option>Descanso</option><option>Negocios</option></select></div>
      <div class="field"><label>Número de personas</label><input type="number" name="personas" min="1" max="50" value="2" required></div>
      <div class="field"><label>Gasto estimado (COP)</label><input type="number" name="gasto" min="0" step="1000" value="200000" required></div>
      <div class="field full"><label>Satisfacción</label><select name="satisfaccion" required><option value="5">5 · Excelente</option><option value="4">4 · Buena</option><option value="3">3 · Aceptable</option><option value="2">2 · Baja</option><option value="1">1 · Muy baja</option></select><span class="hint">Escala de 1 a 5.</span></div>
      <div class="field full"><button class="btn btn-primary" type="submit">Guardar registro →</button></div>
    </form></div>
    <div class="callout"><div class="kicker" style="color:#74e1c6">Captura de datos</div><h3 style="margin-top:8px">Cada registro alimenta el análisis.</h3><p>La información se guarda en una base de datos SQLite. Al registrar una visita cambian automáticamente los totales, promedios y gráficos de la sección de estadísticas.</p><div class="stat-band"><div><small>Base de datos</small><strong>SQLite</strong></div><div><small>Backend</small><strong>Flask</strong></div><div><small>Lenguaje</small><strong>Python</strong></div></div></div></div>
    </div></section>"""
    return page("Registrar visita", "registro", body)


def query_stats():
    conn = db()
    rows = conn.execute("SELECT * FROM visitas ORDER BY fecha").fetchall()
    conn.close()
    by_dest, spend_dest, sat, months, motives = {}, {}, {i:0 for i in range(1,6)}, {}, {}
    for r in rows:
        by_dest[r["destino"]] = by_dest.get(r["destino"], 0) + r["personas"]
        spend_dest.setdefault(r["destino"], []).append(r["gasto"])
        sat[r["satisfaccion"]] = sat.get(r["satisfaccion"], 0) + 1
        month = r["fecha"][:7]
        months[month] = months.get(month, 0) + r["personas"]
        motives[r["motivo"]] = motives.get(r["motivo"], 0) + r["personas"]
    spend_avg = {k: mean(v) for k,v in spend_dest.items()}
    return rows, by_dest, spend_avg, sat, months, motives


def bar_chart(data, formatter=lambda x:str(x)):
    if not data:
        return '<div class="empty">Sin datos.</div>'
    maxv = max(data.values()) or 1
    return "".join(
        f'<div class="bar-row"><div class="bar-label" title="{escape(k)}">{escape(k)}</div><div class="bar-track"><div class="bar-fill" style="width:{max(4,(v/maxv)*100):.1f}%"></div></div><div class="bar-value">{formatter(v)}</div></div>'
        for k,v in sorted(data.items(), key=lambda kv: kv[1], reverse=True)
    )


def line_svg(data):
    if not data:
        return '<div class="empty">Sin datos.</div>'
    pts = list(sorted(data.items()))
    vals = [v for _,v in pts]
    maxv = max(vals) or 1
    w,h,pad = 600,180,26
    coords=[]
    n=max(len(pts)-1,1)
    for i,(_,v) in enumerate(pts):
        x=pad+(w-2*pad)*(i/n)
        y=h-pad-(h-2*pad)*(v/maxv)
        coords.append((x,y,v))
    poly=" ".join(f"{x:.1f},{y:.1f}" for x,y,_ in coords)
    circles="".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#0d8f72" />' for x,y,_ in coords)
    labels="".join(f'<text x="{x:.1f}" y="169" text-anchor="middle" font-size="10" fill="#748692">{m[5:]}</text>' for (m,_),(x,_,_) in zip(pts,coords))
    return f'<svg class="svg-chart" viewBox="0 0 {w} {h}" preserveAspectRatio="none"><line x1="26" y1="150" x2="574" y2="150" stroke="#dfe8ed"/><polyline fill="none" stroke="#0d8f72" stroke-width="4" points="{poly}"/>{circles}{labels}</svg>'


@app.route("/estadisticas")
def estadisticas():
    rows, by_dest, spend_avg, sat, months, motives = query_stats()
    stats = summary_stats()
    sat_data = {f"{k} estrellas": v for k,v in sorted(sat.items(), reverse=True)}
    body = f"""
    <section class="section"><div class="shell"><div class="section-head"><div><div class="kicker">Vista 4</div><h2>Reportes estadísticos</h2><p class="sub">Indicadores construidos a partir de los registros almacenados en el sistema.</p></div></div>{metrics_html(stats)}</div></section>
    <section class="section white"><div class="shell"><div class="grid-2">
      <div class="chart-card"><div class="chart-title">1. Personas por destino</div><div class="chart-sub">Comparación de visitantes registrados.</div>{bar_chart(by_dest)}</div>
      <div class="chart-card"><div class="chart-title">2. Gasto promedio por destino</div><div class="chart-sub">Promedio estimado en pesos colombianos.</div>{bar_chart(spend_avg, money)}</div>
      <div class="chart-card"><div class="chart-title">3. Distribución de satisfacción</div><div class="chart-sub">Cantidad de registros por nivel de valoración.</div>{bar_chart(sat_data)}</div>
      <div class="chart-card"><div class="chart-title">4. Comportamiento mensual</div><div class="chart-sub">Personas registradas por mes.</div>{line_svg(months)}</div>
      <div class="chart-card"><div class="chart-title">5. Motivos de viaje</div><div class="chart-sub">Cantidad de personas según el motivo principal.</div>{bar_chart(motives)}</div>
      <div class="chart-card"><div class="chart-title">Lectura rápida</div><div class="chart-sub">Interpretación general del conjunto de datos.</div><div style="font-size:15px;color:#455d6c;line-height:1.75">El sistema permite identificar cuáles destinos concentran más visitantes, comparar el gasto estimado y observar el nivel de satisfacción. También muestra cómo cambia la demanda durante los meses registrados y cuáles son los principales motivos de viaje. Estos reportes pueden apoyar decisiones sencillas sobre promoción, servicios y atención al turista.</div></div>
    </div></div></section>"""
    return page("Estadísticas", "estadisticas", body)


@app.route("/datos")
def datos():
    conn=db(); rows=conn.execute("SELECT * FROM visitas ORDER BY fecha DESC, id DESC").fetchall(); conn.close()
    trs="".join(f"<tr><td>{r['id']}</td><td>{escape(r['fecha'])}</td><td><strong>{escape(r['destino'])}</strong></td><td><span class='pill'>{escape(r['origen'])}</span></td><td>{escape(r['motivo'])}</td><td>{r['personas']}</td><td>{money(r['gasto'])}</td><td>{r['satisfaccion']}/5</td></tr>" for r in rows)
    body=f"""<section class="section"><div class="shell"><div class="section-head"><div><div class="kicker">Vista 5</div><h2>Datos registrados</h2><p class="sub">Tabla de observaciones utilizadas para construir los reportes estadísticos.</p></div><a class="btn btn-primary" href="{url_for('exportar')}">Exportar CSV</a></div><div class="table-wrap"><table><thead><tr><th>ID</th><th>Fecha</th><th>Destino</th><th>Origen</th><th>Motivo</th><th>Personas</th><th>Gasto</th><th>Satisfacción</th></tr></thead><tbody>{trs}</tbody></table></div></div></section>"""
    return page("Datos", "datos", body)


@app.route("/exportar")
def exportar():
    conn=db(); rows=conn.execute("SELECT * FROM visitas ORDER BY fecha").fetchall(); conn.close()
    out=io.StringIO(); writer=csv.writer(out); writer.writerow(["id","fecha","destino","origen","motivo","personas","gasto","satisfaccion"])
    for r in rows: writer.writerow([r["id"],r["fecha"],r["destino"],r["origen"],r["motivo"],r["personas"],r["gasto"],r["satisfaccion"]])
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=turismo_santa_marta.csv"})


@app.route("/acerca")
def acerca():
    body=f"""
    <section class="section"><div class="shell"><div class="section-head"><div><div class="kicker">Vista 6</div><h2>Acerca del proyecto</h2><p class="sub">Planteamiento académico y descripción de la solución desarrollada.</p></div></div>
    <div class="grid-2"><div class="panel"><div class="kicker">Problemática</div><h3 style="font-size:26px;margin:8px 0 15px">Información turística dispersa</h3><p style="color:var(--muted)">Santa Marta recibe visitantes interesados en playas, naturaleza, cultura, gastronomía y actividades recreativas. Sin embargo, cuando la información sobre cantidad de visitantes, gasto estimado, nivel de satisfacción y motivos de viaje se encuentra dispersa o no se registra de manera organizada, resulta difícil identificar qué destinos tienen mayor demanda y qué tipo de experiencia buscan los turistas.</p><p style="color:var(--muted)">La falta de un registro sencillo también limita la posibilidad de comparar lugares y observar cambios durante el año. Un sistema de información web puede concentrar estos datos en una sola herramienta, facilitar su consulta y generar reportes estadísticos que permitan comprender mejor el comportamiento turístico de la ciudad.</p></div>
    <div class="panel"><div class="kicker">Herramienta propuesta</div><h3 style="font-size:26px;margin:8px 0 15px">Techmopau Turismo Data</h3><p style="color:var(--muted)">La herramienta propuesta es una aplicación web desarrollada en Python con Flask y una base de datos SQLite. Permite consultar destinos turísticos de Santa Marta, registrar nuevas visitas, almacenar información de fecha, origen, motivo, número de personas, gasto y satisfacción, visualizar reportes estadísticos y revisar los datos utilizados en el análisis. El sistema fue diseñado con una interfaz clara y adaptable a computadores y dispositivos móviles, de forma que pueda demostrarse fácilmente durante la sustentación del proyecto.</p><div style="margin-top:22px;padding:16px;border-radius:16px;background:#f6faf9;border:1px solid var(--line)"><strong>URL local</strong><div style="margin-top:5px;color:var(--green);font-weight:850">http://127.0.0.1:5000</div><div class="hint" style="margin-top:5px">Para la entrega final se puede publicar en Render y reemplazar esta dirección por la URL pública.</div></div></div></div>
    </div></section>"""
    return page("Acerca", "acerca", body)


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
