"""
Generate the home page story and the demo-mode slides (English and Spanish) from one source.

    python scripts/build_story.py            # write web-src/pages/index.html and web-src/partials/nav.html
    python scripts/build_story.py --check    # exit 1 if those files differ from what this script produces

Every text block exists twice, wrapped in data-lang="en" / data-lang="es"; CSS shows only the language chosen with
the EN/ES switch in the navbar (stored in the browser). The home and the slides share the same blocks.
Numbers are copied from the README and results/ (Penmanshiel, protocol qwind-v1); the generated pages are then built
into web/ with scripts/build_web.py. Standard library only.
"""
import html
import itertools
import math
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
G, Y, R = "tl tl-green", "tl tl-yellow", "tl tl-red"

LANG = "en"
CTX = "slide"  # "home" keeps the full notes; the demo slides use shorter ones
_uid = itertools.count(1)


def L(en, es):
    return es if LANG == "es" else en


def esc(t):
    return html.escape(t, quote=True)


# ---------------------------------------------------------------- small building blocks
def flag(name):
    label = {"scotland": L("Scotland flag", "Bandera de Escocia"), "england": L("England flag", "Bandera de Inglaterra"),
             "argentina": L("Argentina flag", "Bandera de Argentina")}[name]
    body = {
        "scotland": '<rect width="30" height="20" fill="#0065bd"/><path d="M0 0L30 20M30 0L0 20" stroke="#fff" stroke-width="3"/>',
        "england": '<rect width="30" height="20" fill="#fff" stroke="#999" stroke-width="0.6"/><path d="M15 0V20M0 10H30" stroke="#ce1124" stroke-width="4"/>',
        "argentina": '<rect width="30" height="20" fill="#74acdf"/><rect y="6.6" width="30" height="6.8" fill="#fff"/><circle cx="15" cy="10" r="1.8" fill="#f6b40e"/>',
    }[name]
    return f'<svg class="flag" viewBox="0 0 30 20" width="30" height="20" role="img" aria-label="{label}">{body}</svg>'


def cell(c, tag="td"):
    if isinstance(c, tuple):
        return f'<{tag} class="{c[1]}">{c[0]}</{tag}>'
    return f"<{tag}>{c}</{tag}>"


def table(cap, head, rows, cls=""):
    h = "".join(f'<th scope="col">{x}</th>' for x in head)
    r = "".join("<tr>" + cell(row[0], "th").replace("<th", '<th scope="row"', 1) + "".join(cell(c) for c in row[1:]) + "</tr>" for row in rows)
    return f'<table class="slide-table {cls}">\n                <caption>{cap}</caption>\n                <thead><tr>{h}</tr></thead>\n                <tbody>{r}</tbody>\n            </table>'


def cards(items, cls=""):
    out = "".join(f'<div class="card {c}"><div class="card-big">{big}</div><div class="card-label">{lab}</div></div>' for big, lab, c in items)
    return f'<div class="cards {cls}">{out}</div>'


def pbars(rows):
    out = "".join(f'<div class="pbar-row"><span class="pbar-label">{l}</span><span class="pbar-track"><span class="pbar-fill {c}" style="--w:{w}%"></span></span><span class="pbar-val">{v}</span></div>' for l, v, w, c in rows)
    return f'<div class="pbars">{out}</div>'


def fig(img, alt, cap):
    return f'<figure>\n                <img src="img/{img}" alt="{esc(alt)}" loading="lazy">\n                <figcaption>{cap}</figcaption>\n            </figure>'


def icon(body):
    return f'<svg class="icon" viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{body}</svg>'


ICON_TURBINE = icon('<circle cx="12" cy="9" r="1.6"/><path d="M12 7.4V2M13.4 9.8l4.6 2.7M10.6 9.8L6 12.5M12 10.6V22M9 22h6"/>')
ICON_ATOM = icon('<circle cx="12" cy="12" r="1.5" fill="currentColor"/><ellipse cx="12" cy="12" rx="10" ry="4"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(120 12 12)"/>')
ICON_COIN = icon('<circle cx="12" cy="12" r="10"/><path d="M15 8.5c-.6-.9-1.7-1.5-3-1.5-1.7 0-3 .9-3 2.2 0 3 6 1.6 6 4.6 0 1.3-1.3 2.2-3 2.2-1.4 0-2.5-.6-3.1-1.6M12 5v14"/>')


def hero_turbine():
    """Minimalist wind turbine in SVG + CSS (the blades spin): tells in one second what the project is about."""
    blade = '<path d="M60 60L57.6 6Q60 2 62.4 6Z"/>'
    return ('<svg class="hero-turbine" viewBox="0 0 120 200" width="120" height="200" aria-hidden="true" focusable="false">'
            '<path class="ht-tower" d="M58 66H62L64 188H56Z"/>'
            '<path class="ht-ground" d="M30 190H90" />'
            f'<g class="ht-blades"><g class="ht-spin">{blade}<g transform="rotate(120 60 60)">{blade}</g><g transform="rotate(240 60 60)">{blade}</g></g></g>'
            '<circle class="ht-hub" cx="60" cy="60" r="4.5"/></svg>')


def turbine(x, cls=""):
    return (f'<g transform="translate({x} 0)"><rect x="-4" y="95" width="8" height="85" fill="#cbd5e1"/>'
            f'<g transform="translate(0 90)"><g class="spin {cls}"><g fill="#e2e8f0" stroke="#94a3b8" stroke-width="1"><path d="M0 0L-4 -72L4 -72Z"/><path d="M0 0L-4 -72L4 -72Z" transform="rotate(120)"/><path d="M0 0L-4 -72L4 -72Z" transform="rotate(240)"/></g></g></g>'
            '<circle cx="0" cy="90" r="7" fill="#94a3b8"/></g>')


def wake_svg():
    uid = next(_uid)
    return (f'<svg class="illus" viewBox="0 0 640 200" role="img" aria-label="{esc(L("Two wind turbines in a row. The first turbine leaves a widening wake of slower air; the second turbine stands inside that wake and produces less power.", "Dos turbinas en fila. La primera deja una estela de aire más lento que se ensancha; la segunda está dentro de esa estela y produce menos energía."))}">'
            f'<defs><linearGradient id="wk{uid}" x1="0" x2="1"><stop offset="0" stop-color="#38bdf8" stop-opacity=".55"/><stop offset="1" stop-color="#38bdf8" stop-opacity=".08"/></linearGradient></defs>'
            '<path class="wind-line" d="M10 40H90M10 90H90M10 140H90" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/>'
            f'<polygon class="wake" points="170,70 600,10 600,170 170,110" fill="url(#wk{uid})"/>'
            + turbine(160) + turbine(430, "slow") +
            f'<text x="160" y="196" text-anchor="middle" fill="currentColor" font-size="15">{L("full wind", "viento pleno")}</text>'
            f'<text x="430" y="196" text-anchor="middle" fill="currentColor" font-size="15">{L("slower wind, less power", "viento más lento, menos energía")}</text></svg>')


def switches():
    label = L("Six switches, one per turbine. Switches are swapped in pairs, so the number of switches on never changes.",
              "Seis interruptores, uno por turbina. Se intercambian de a pares, así que la cantidad de interruptores encendidos nunca cambia.")
    sw = "".join(f'<span class="sw {c}" style="--d:{d}s"><span class="knob"></span></span>' for c, d in [("a", 0), ("b", 0), ("a", 1.3), ("b", 1.3), ("a", 2.6), ("b", 2.6)])
    return f'<div class="switches" role="img" aria-label="{esc(label)}"><div class="sw-row">{sw}</div><p class="sw-count">{L("Always exactly 3 on", "Siempre exactamente 3 encendidos")}</p></div>'


def flow():
    steps = [
        (L("Wind and positions", "Viento y posiciones"), L("real positions and a measured wind rose", "posiciones reales y una rosa de vientos medida"), icon('<path d="M2 8h11a3 3 0 100-3M2 13h16a3 3 0 110 3M2 18h8"/>'), ""),
        (L("Wake model", "Modelo de estelas"), L("which turbine shades which, and how much", "qué turbina tapa a cuál, y cuánto"), icon('<circle cx="5" cy="12" r="2"/><path d="M8 11l13-6v14L8 13z"/>'), ""),
        (L("Choice problem", "Problema de elección"), L("pick the K turbines with the least wake loss", "elegir las K turbinas con menos pérdida por estelas"), icon('<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 17.5l2.5 2.5 4.5-5"/>'), ""),
        (L("Quantum circuit", "Circuito cuántico"), L("built in Qiskit; keeps exactly K by construction", "hecho en Qiskit; mantiene exactamente K por construcción"), ICON_ATOM, "flow-hot"),
        (L("Answer", "Respuesta"), L("the K turbines to keep running", "las K turbinas que siguen funcionando"), icon('<circle cx="12" cy="12" r="10"/><path d="M7.5 12.5l3 3 6-7"/>'), ""),
    ]
    items = "".join(f'<li class="flow-step {c}"><span class="flow-num">{i}</span><div class="flow-icon">{ic}</div><strong>{t}</strong><span>{d}</span></li>' for i, (t, d, ic, c) in enumerate(steps, 1))
    return f'<ol class="flow">{items}</ol>'


def decision():
    on = {"T01": (362, 597), "T02": (451, 674), "T06": (579, 645), "T07": (650, 714), "T12": (631, 404), "T14": (794, 517), "T15": (869, 598)}
    off = {"T04": (426, 490), "T05": (502, 572), "T08": (520, 428), "T09": (616, 519), "T10": (690, 580), "T11": (781, 648), "T13": (720, 456)}
    dx, dy = math.sin(math.radians(22.5)), -math.cos(math.radians(22.5))
    px, py = -dy, dx
    pt = lambda x, y: f"{x:.0f},{y:.0f}"
    wakes = ""
    for (x, y) in on.values():
        pts = [(x + 12 * px, y + 12 * py), (x - 12 * px, y - 12 * py), (x + 190 * dx - 30 * px, y + 190 * dy - 30 * py), (x + 190 * dx + 30 * px, y + 190 * dy + 30 * py)]
        wakes += '<polygon class="dmap-wake" points="' + " ".join(pt(*q) for q in pts) + '"/>'
    dots = ""
    for name, (x, y) in on.items():
        dots += f'<g class="dmap-on"><circle class="dmap-ring" cx="{x}" cy="{y}" r="14"/><circle cx="{x}" cy="{y}" r="11"/><text x="{x}" y="{y + 32}">{name}</text></g>'
    for name, (x, y) in off.items():
        dots += f'<g class="dmap-off"><circle cx="{x}" cy="{y}" r="10"/><text x="{x}" y="{y + 32}">{name}</text></g>'
    label = L("Top view of the 14 real turbine positions of the Penmanshiel wind farm in Scotland. Seven turbines are blue (kept running) and seven are grey outlines (switched off); light blue strips downwind of the blue turbines show their wakes. An arrow shows the dominant wind direction.",
              "Vista desde arriba de las 14 posiciones reales de turbinas del parque Penmanshiel, en Escocia. Siete turbinas son azules (siguen funcionando) y siete son círculos grises (apagadas); las franjas celestes detrás de las azules muestran sus estelas. Una flecha indica la dirección dominante del viento.")
    svg = (f'<svg class="dmap" viewBox="230 190 760 620" role="img" aria-label="{esc(label)}">' + wakes + dots +
           '<g class="dmap-arrow"><path d="M270 770L318 668"/><path d="M300 676L320 652L330 682Z"/></g>'
           f'<text class="dmap-note" x="270" y="795">{L("wind from 202.5 degrees", "viento desde 202,5 grados")}</text></svg>')
    keys = (f'<p class="dmap-key"><span class="dot dot-on"></span> {L("Kept running (7)", "Siguen funcionando (7)")}</p>'
            f'<p class="dmap-key"><span class="dot dot-off"></span> {L("Switched off (7)", "Apagadas (7)")}</p>'
            f'<p class="dmap-key"><span class="dot dot-wake"></span> {L("Wake of a kept turbine", "Estela de una turbina encendida")}</p>')
    stats = cards([("4.0%".replace(".", L(".", ",")), L("power lost to wakes with the best choice", "de energía perdida por estelas con la mejor elección"), G),
                   ("8.0%".replace(".", L(".", ",")), L("for an average random choice of 7", "con una elección de 7 al azar, en promedio"), R)], "cards-2")
    note = f'<p class="slide-note">{L("The best of 3,432 plans (exact search). Real positions of Penmanshiel, Scotland. Model units, not measured production.", "La mejor de 3.432 combinaciones (búsqueda exacta). Posiciones reales de Penmanshiel, Escocia. Unidades del modelo, no producción medida.")}</p>'
    return '<div class="dmap-wrap">' + svg + '<div class="dmap-side">' + keys + stats + note + "</div></div>"


def legend():
    return (f'<p class="slide-legend"><span class="tl tl-green">{L("green", "verde")}</span> {L("all instances / yes", "todos los casos / sí")} '
            f'<span class="tl tl-yellow">{L("yellow", "amarillo")}</span> {L("most instances / partly", "la mayoría / en parte")} '
            f'<span class="tl tl-red">{L("red", "rojo")}</span> {L("no / worse", "no / peor")}</p>')


def d(x):
    """Decimal comma in Spanish for plain numbers."""
    return x.replace(".", ",") if LANG == "es" else x


# ---------------------------------------------------------------- content units (home + demo slides)
def units():
    U = []

    def add(key, title, body, home=True, cls="", slide=True):
        U.append(dict(key=key, title=title, body=body, home=home, cls=cls, slide=slide))

    K = L  # short alias for readability below
    add("what", K("1. What is it?", "1. ¿Qué es?"),
        wake_svg() + f'<p class="slide-lead">{K("QWind decides <strong>which turbines to keep running</strong> when a farm must produce less, so wakes waste as little energy as possible.", "QWind decide <strong>qué turbinas dejar funcionando</strong> cuando un parque tiene que producir menos, para que las estelas desperdicien la menor energía posible.")}</p>')
    add("data", K("Tested on real wind farms and real winds", "Probado en parques eólicos reales y con vientos reales"),
        table(K("What each dataset is, and how many turbine positions we choose from.", "Qué es cada conjunto de datos y entre cuántas posiciones de turbina elegimos."),
              [K("Place", "Lugar"), K("What it is", "Qué es"), K("Turbine positions", "Posiciones de turbina"), K("Test cases", "Casos de prueba")], [
            [flag("scotland") + " Penmanshiel, " + K("Scotland", "Escocia"), K("Real farm: real turbine positions and measured wind", "Parque real: posiciones reales de turbinas y viento medido"), K("14 (also a 10-turbine subset)", "14 (y también un subconjunto de 10)"), K("15 (3 + 3 + 9)", "15 (3 + 3 + 9)")],
            [flag("england") + " Kelmarsh, " + K("England", "Inglaterra"), K("Real farm: real turbine positions and measured wind", "Parque real: posiciones reales de turbinas y viento medido"), "6", "3"],
            [flag("argentina") + " Chubut, Argentina", K("Real wind (reanalysis data) on a made-up grid of positions", "Viento real (datos de reanálisis) sobre una grilla de posiciones inventada"), K("6 to 12", "6 a 12"), "8"],
            [flag("argentina") + " Bahía Blanca, Argentina", K("Real wind (reanalysis data) on a made-up grid of positions", "Viento real (datos de reanálisis) sobre una grilla de posiciones inventada"), K("6 to 12", "6 a 12"), "8"],
            [K("Synthetic", "Sintético"), K("Made-up wind and grid, generated by us", "Viento y grilla inventados, generados por nosotros"), K("6 to 12", "6 a 12"), "24"]], "slide-table-sm")
        + f'<p class="slide-note">{K("A test case is one question: &quot;keep K turbines out of N positions&quot;. Real wind data is open (CC BY 4.0).", "Un caso de prueba es una pregunta: &quot;dejar K turbinas de N posiciones&quot;. Los datos de viento reales son abiertos (CC BY 4.0).")}</p>')
    add("why", K("Why a quantum computer? The number of plans explodes", "¿Por qué una computadora cuántica? La cantidad de planes explota"),
        cards([
            ("3,432".replace(",", L(",", ".")), K("14 turbines, keep 7<br>Instant on a laptop", "14 turbinas, dejar 7<br>Instantáneo en una notebook"), G),
            ("10<sup>14</sup>", K("50 turbines, keep 25<br>About a day and a half to check them all", "50 turbinas, dejar 25<br>Un día y medio para revisarlos todos"), Y),
            ("10<sup>29</sup>", K("100 turbines, keep 50<br>About 3 trillion years", "100 turbinas, dejar 50<br>Unos 3 billones de años"), R),
            ("10<sup>299</sup>", K("1,000 turbines (hypothetical)<br>More plans than atoms in the universe (10<sup>80</sup>)", "1.000 turbinas (hipotético)<br>Más planes que átomos en el universo (10<sup>80</sup>)"), R)], "cards-4")
        + f'<p class="slide-note">{K("Checking one by one at a billion plans per second. Classical shortcuts (simulated annealing) keep working at larger sizes but do not guarantee the best answer. Whether our circuit can match them at 50 to 100 turbines is the open question; we do not answer it here.", "Revisándolos de a uno, a mil millones de planes por segundo. Los atajos clásicos (recocido simulado) siguen funcionando con tamaños mayores, pero no garantizan la mejor respuesta. Si nuestro circuito puede igualarlos con 50 a 100 turbinas es la pregunta abierta; acá no la respondemos.")}</p>')
    add("who", K("2. Why does it matter, and who is it for?", "2. ¿Por qué importa y para quién es?"),
        cards([
            (ICON_TURBINE, K("<strong>Wind farm operators</strong><br>who must produce less for a while: grid limits, maintenance, environmental rules", "<strong>Operadores de parques eólicos</strong><br>que deben producir menos por un tiempo: límites de la red, mantenimiento, reglas ambientales"), ""),
            (ICON_ATOM, K("<strong>Quantum developers</strong><br>who want a reproducible benchmark", "<strong>Desarrolladores cuánticos</strong><br>que quieren una referencia reproducible"), ""),
            (ICON_COIN, K("<strong>The choice has a money value</strong><br>which turbines are switched off changes the energy lost to wakes", "<strong>La elección tiene un valor en dinero</strong><br>qué turbinas se apagan cambia la energía perdida por estelas"), "")], "cards-3"))
    add("bars", K("Choosing well wastes less energy", "Elegir bien desperdicia menos energía"),
        f'<p class="slide-note">{K("Share of power lost to wakes, Penmanshiel (14 turbines). Best layout against an average random choice.", "Porcentaje de energía perdida por estelas, Penmanshiel (14 turbinas). Mejor elección contra una elección al azar promedio.")}</p>'
        + pbars([(K("Keep 5: best", "Dejar 5: la mejor"), d("1.0%"), 10, "pf-green"), (K("Keep 5: random", "Dejar 5: al azar"), d("5.3%"), 53, "pf-red"),
                 (K("Keep 7: best", "Dejar 7: la mejor"), d("4.0%"), 40, "pf-green"), (K("Keep 7: random", "Dejar 7: al azar"), d("8.0%"), 80, "pf-red"),
                 (K("Keep 9: best", "Dejar 9: la mejor"), d("7.0%"), 70, "pf-green"), (K("Keep 9: random", "Dejar 9: al azar"), d("10.6%"), 100, "pf-red")])
        + f'<p class="slide-note">{K("Modelled losses (Jensen wake model), not measured production.", "Pérdidas calculadas con un modelo (estelas de Jensen), no producción medida.")}</p>')
    add("money", K("What the choice could be worth (money)", "Cuánto podría valer la elección (dinero)"),
        table(K("Penmanshiel, 14 turbines, 1,000 hours with only K turbines running. Best layout against an average random choice.", "Penmanshiel, 14 turbinas, 1.000 horas con solo K turbinas funcionando. Mejor elección contra una elección al azar promedio."),
              [K("Turbines kept (of 14)", "Turbinas que siguen (de 14)"), K("Power lost to wakes: best vs random", "Energía perdida por estelas: mejor vs azar"), K("More energy", "Más energía"), K("Extra energy", "Energía extra"), K("At $66/MWh", "A $66/MWh"), K("At $99/MWh", "A $99/MWh"), K("At $132/MWh", "A $132/MWh")], [
            ["5", d("1.0% vs 5.3%"), d("+4.5%"), "136 MWh", (d("$9.0k"), G), (d("$13.5k"), G), (d("$18.0k"), G)],
            ["7", d("4.0% vs 8.0%"), d("+4.3%"), "176 MWh", (d("$11.6k"), G), (d("$17.4k"), G), (d("$23.2k"), G)],
            ["9", d("7.0% vs 10.6%"), d("+4.0%"), "207 MWh", (d("$13.7k"), G), (d("$20.5k"), G), (d("$27.3k"), G)]], "slide-table-sm")
        + f'<p class="slide-note">{K("An illustrative scale from a model, not a forecast and not a measured saving.", "Una escala ilustrativa a partir de un modelo, no un pronóstico ni un ahorro medido.")}</p>')
    add("assumptions", K("How the money numbers are built", "Cómo se calculan los números de dinero"),
        table(K("Every assumption behind the previous table.", "Cada supuesto detrás de la tabla anterior."), [K("Assumption", "Supuesto"), K("Value", "Valor")], [
            [K("Output of each running turbine", "Producción de cada turbina encendida"), K("637 kW on average (measured in 2019, 31.1% capacity factor)", "637 kW en promedio (medido en 2019, factor de capacidad de 31,1%)")],
            [K("Time in that configuration", "Tiempo en esa configuración"), K("1,000 hours (a year has 8,760)", "1.000 horas (un año tiene 8.760)")],
            [K("Wake losses", "Pérdidas por estelas"), K("From our wake model (Jensen), best choice vs average random choice", "De nuestro modelo de estelas (Jensen), mejor elección contra elección al azar promedio")],
            [K("Energy prices", "Precios de la energía"), K("£50, £75 and £100 per MWh = $66, $99 and $132 (1 GBP = 1.3220 USD, ECB rate of 2026-10-09)", "£50, £75 y £100 por MWh = $66, $99 y $132 (1 GBP = 1,3220 USD, cotización del BCE del 2026-10-09)")],
            [K("Not counted", "No se cuenta"), K("Costs, contracts, and what an operator does today", "Costos, contratos y lo que hace hoy un operador")]], "slide-table-sm"), home="details")
    add("quantum", K("3. How does the quantum part work?", "3. ¿Cómo funciona la parte cuántica?"),
        switches() + f"""
            <ol class="steps">
                <li><span>1</span>{K("Start from a valid plan", "Partir de un plan válido")}</li>
                <li><span>2</span>{K("Only swap switches in pairs", "Solo intercambiar interruptores de a pares")}</li>
                <li><span>3</span>{K("Tune the circuit (about 120 tries)", "Ajustar el circuito (unos 120 intentos)")}</li>
                <li><span>4</span>{K("Sample 1,000 times, keep the best", "Muestrear 1.000 veces y quedarse con la mejor")}</li>
            </ol>
            <p class="slide-note">{K("The usual approach discourages invalid answers with a penalty but still produces many. Ours makes them impossible. Technical names: QAOA with an XY mixer and a Dicke start state.", "El enfoque habitual desalienta las respuestas inválidas con una penalización, pero igual produce muchas. El nuestro las hace imposibles. Nombres técnicos: QAOA con mezclador XY y estado inicial de Dicke.")}</p>""")
    add("baselines", K("Our circuit against the alternatives", "Nuestro circuito frente a las alternativas"),
        table(K("Ranges across the six datasets.", "Rangos en los seis conjuntos de datos."), ["", K("Our circuit", "Nuestro circuito"), K("Usual penalty version", "Versión habitual con penalización"), K("Random valid choice", "Elección válida al azar")], [
            [K("Output that is a valid plan", "Resultados que son un plan válido"), ("100%", G), (d("26% to 64%") if LANG == "en" else "26% a 64%", R), ("100%", G)],
            [K("Chance of sampling the best layout", "Chance de muestrear la mejor elección"), (K("reference", "referencia"), G), (K("3.4 to 17.1 times lower than ours", "de 3,4 a 17,1 veces menor que la nuestra"), R), (K("3 to 7.5 times lower than ours", "de 3 a 7,5 veces menor que la nuestra"), Y)],
            [K("Best sampled layout is the exact best", "La mejor elección muestreada es la mejor exacta"), (K("all instances of 5 of 6 datasets; 2 of 3 on Penmanshiel", "todos los casos de 5 de 6 conjuntos; 2 de 3 en Penmanshiel"), G), (K("less often", "con menos frecuencia"), R), (K("0.95 to 1.00 chance up to 12 positions, 0.35 on average at 14", "chance de 0,95 a 1,00 hasta 12 posiciones, 0,35 en promedio con 14"), Y)]], "slide-table-sm") + legend())
    n_of = lambda a, b: K(f"{a} of {b}", f"{a} de {b}")
    add("scorecard", K("Our test results", "Nuestros resultados de prueba"),
        table(K("Our circuit (XY mixer + Dicke start, depth 3) on every dataset. Counts are test cases.", "Nuestro circuito (mezclador XY + estado de Dicke, profundidad 3) en cada conjunto de datos. Los conteos son casos de prueba."),
              [K("Dataset", "Conjunto de datos"), K("Positions", "Posiciones"), K("Always a valid plan", "Siempre un plan válido"), K("Better average quality than random valid choice", "Mejor calidad promedio que la elección válida al azar"), K("Higher chance of the best layout than random valid choice", "Más chance de la mejor elección que la elección válida al azar"), K("Finds the exact best layout", "Encuentra la mejor elección exacta")], [
            [K("Synthetic", "Sintético"), K("6 to 12", "6 a 12"), ("100%", G), (n_of(24, 24), G), (n_of(20, 24), Y), (n_of(24, 24), G)],
            ["Penmanshiel", "14", ("100%", G), (n_of(3, 3), G), (n_of(3, 3), G), (n_of(2, 3), Y)],
            ["Penmanshiel-10", "10", ("100%", G), (n_of(3, 3), G), (n_of(3, 3), G), (n_of(3, 3), G)],
            [K("Penmanshiel, every K", "Penmanshiel, todos los K"), "14", ("100%", G), (n_of(9, 9), G), (n_of(9, 9), G), (n_of(8, 9), Y)],
            ["Kelmarsh", "6", ("100%", G), (n_of(3, 3), G), (n_of(3, 3), G), (n_of(3, 3), G)],
            ["Chubut", K("6 to 12", "6 a 12"), ("100%", G), (n_of(8, 8), G), (n_of(7, 8), Y), (n_of(8, 8), G)],
            ["Bahía Blanca" if LANG == "es" else "Bahia Blanca", K("6 to 12", "6 a 12"), ("100%", G), (n_of(8, 8), G), (n_of(8, 8), G), (n_of(8, 8), G)]], "slide-table-sm") + legend())
    add("versus", K("Our circuit against the classical methods", "Nuestro circuito frente a los métodos clásicos"),
        cards([("7 " + K("of", "de") + " 7", K("<strong>Simulated annealing</strong> (classical)<br>finds the exact best answer in every dataset", "<strong>Recocido simulado</strong> (clásico)<br>encuentra la mejor respuesta exacta en todos los conjuntos de datos"), G),
               ("4 " + K("of", "de") + " 7", K("<strong>Greedy search</strong> (classical)<br>finds the exact best answer in 4 datasets", "<strong>Búsqueda voraz</strong> (clásico)<br>encuentra la mejor respuesta exacta en 4 conjuntos de datos"), Y),
               ("5 " + K("of", "de") + " 7", K("<strong>Our circuit</strong> (quantum)<br>exact best in every case of 5 datasets; 2 of 3 and 8 of 9 cases in the other two", "<strong>Nuestro circuito</strong> (cuántico)<br>mejor exacta en todos los casos de 5 conjuntos; 2 de 3 y 8 de 9 casos en los otros dos"), Y)], "cards-3")
        + f'<p class="slide-note">{K("Tries used to get there", "Intentos usados para llegar ahí")}</p>'
        + pbars([(K("Simulated annealing", "Recocido simulado"), d("5,005") if LANG == "en" else "5.005", 100, "pf-blue"), (K("Our circuit", "Nuestro circuito"), "120", 2.4, "pf-green")])
        + (f'<p class="slide-note"><strong>{K("Almost the same result with about 40 times fewer tries.", "Casi el mismo resultado con unas 40 veces menos intentos.")}</strong></p>' if CTX == "slide" else
           f'<p class="slide-note"><strong>{K("Almost the same result with about 40 times fewer tries, and we claim no quantum advantage:", "Casi el mismo resultado con unas 40 veces menos intentos, y no afirmamos ventaja cuántica:")}</strong> {K("the classical method is still exact in every case. The budgets are not matched (one circuit try costs more than a classical one) and the circuit is simulated on a CPU.", "el método clásico sigue siendo exacto en todos los casos. Los presupuestos no son equivalentes (un intento del circuito cuesta más que uno clásico) y el circuito se simula en una CPU.")}</p>'))
    z, a1, a2, a3 = d("0.0000"), d("0.0129"), d("0.0060"), d("0.0020")
    add("competitive", K("Competitive with the classical methods", "Competitivo con los métodos clásicos"),
        table(K("Average gap to the exact best answer (0 = perfect). Same instances as the scorecard.", "Diferencia promedio con la mejor respuesta exacta (0 = perfecto). Mismos casos que el cuadro anterior."),
              [K("Dataset", "Conjunto de datos"), K("Simulated annealing (about 5,005 tries)", "Recocido simulado (unos 5.005 intentos)"), K("Greedy search", "Búsqueda voraz"), K("Our circuit (about 120 tries, best of 1,000 samples)", "Nuestro circuito (unos 120 intentos, la mejor de 1.000 muestras)")], [
            [K("Synthetic", "Sintético"), (z, G), (a1, Y), (z, G)],
            ["Penmanshiel (14)", (z, G), (a2, Y), (a2, Y)],
            [K("Penmanshiel, every K (14)", "Penmanshiel, todos los K (14)"), (z, G), (a3, Y), (a3, Y)],
            ["Penmanshiel-10", (z, G), (z, G), (z, G)],
            ["Kelmarsh", (z, G), (z, G), (z, G)],
            ["Chubut", (z, G), (z, G), (z, G)],
            ["Bahía Blanca" if LANG == "es" else "Bahia Blanca", (z, G), (z, G), (z, G)]], "slide-table-sm")
        + (f'<p class="slide-note"><strong>{K("Our results are competitive with classical methods at these sizes.", "Nuestros resultados son competitivos con los métodos clásicos a estos tamaños.")}</strong></p>' if CTX == "slide" else
           f'<p class="slide-note"><strong>{K("Our results are competitive with classical methods at these sizes, and we claim no quantum advantage.", "Nuestros resultados son competitivos con los métodos clásicos a estos tamaños, y no afirmamos ventaja cuántica.")}</strong> {K("Classical methods also solve all of these exactly.", "Los métodos clásicos también resuelven todos estos casos de forma exacta.")}</p>') + legend())
    add("kit", K("Built with the hackathon kit", "Hecho con el kit del hackatón"),
        table(K("What the rules asked for, and what we used.", "Lo que pedían las reglas y lo que usamos."), [K("Requirement", "Requisito"), K("What we did", "Qué hicimos")], [
            [K("Use the Qiskit framework", "Usar el framework Qiskit"), (K("Qiskit 2.5.2; the circuit is built by hand with Qiskit, plus NumPy and SciPy", "Qiskit 2.5.2; el circuito está hecho a mano con Qiskit, más NumPy y SciPy"), G)],
            [K("Run on Qollab's free simulator", "Correr en el simulador gratuito de Qollab"), (K("The live Run on Qollab uses its built-in simulator (about 20 seconds)", "La ejecución en vivo en Qollab usa su simulador integrado (unos 20 segundos)"), G)],
            [K("Published and runnable on Qollab, MIT license", "Publicado y ejecutable en Qollab, licencia MIT"), (K("Project page on Qollab; open source (MIT), 150+ tests", "Página del proyecto en Qollab; código abierto (MIT), más de 150 tests"), G)],
            [K("Full experiments", "Experimentos completos"), K("Same Qiskit code, run offline on a CPU (exact simulation, no noise) with a protocol fixed before running", "El mismo código de Qiskit, ejecutado offline en una CPU (simulación exacta, sin ruido) con un protocolo fijado antes de correr")]], "slide-table-sm"))
    add("hw", K("Tested on real quantum hardware", "Probado en hardware cuántico real"),
        cards([("IonQ Forte 1", K("Real quantum computer, 36 qubits, run through Qollab", "Computadora cuántica real, 36 qubits, usada a través de Qollab"), ""),
               ("997", K("shots (samples), one run", "disparos (muestras), una sola corrida"), ""),
               ("78", K("two-qubit gates (plus 123 one-qubit gates)", "compuertas de dos qubits (más 123 de un qubit)"), ""),
               ("6 / 3", K("positions / turbines kept (a small case)", "posiciones / turbinas que siguen (un caso chico)"), "")], "cards-4")
        + f'<p class="slide-note">{K("The circuit was tuned on the exact simulator; the real machine only produced the samples. A single small run, not a noise study.", "El circuito se ajustó en el simulador exacto; la máquina real solo produjo las muestras. Una sola corrida chica, no un estudio de ruido.")}</p>')
    add("hwres", K("What the real quantum computer gave us", "Lo que nos dio la computadora cuántica real"),
        f'<p class="slide-note">{K("Chance of sampling the best layout, valid samples only (22% of the hardware samples were invalid and are discarded).", "Chance de muestrear la mejor elección, solo con muestras válidas (el 22% de las muestras del hardware eran inválidas y se descartan).")}</p>'
        + pbars([(K("Ideal simulator", "Simulador ideal"), d("0.1784"), 100, "pf-blue"), (K("IonQ Forte 1 (real hardware)", "IonQ Forte 1 (hardware real)"), d("0.1665"), 93, "pf-green"), (K("Random valid choice", "Elección válida al azar"), d("0.1000"), 56, "pf-red")])
        + f'<p class="slide-note">{K("The hardware came close to the ideal and stayed above random. The best sample was the exact best layout. Without filtering: 0.1304 chance of the best layout, 78% valid layouts.", "El hardware se acercó al ideal y quedó por encima del azar. La mejor muestra fue la mejor elección exacta. Sin filtrar: chance de 0,1304 de la mejor elección y 78% de elecciones válidas.")}</p>')
    add("run", K("4. How do I run it?", "4. ¿Cómo lo ejecuto?"),
        cards([(K("On Qollab", "En Qollab"), K("Open the project page and click <strong>Run your code</strong> with the built-in simulator. About 20 seconds.", "Abrí la página del proyecto y hacé clic en <strong>Run your code</strong> con el simulador integrado. Unos 20 segundos."), ""),
               (K("Locally", "En tu computadora"), "<code>pip install -r qollab/requirements.txt pytest</code><br><code>python qollab/main.py</code>", ""),
               (K("Open source", "Código abierto"), K("MIT license, 150+ tests, protocol fixed before running.", "Licencia MIT, más de 150 tests, protocolo fijado antes de correr."), "")], "cards-3"))
    add("wakepic", K("The problem in pictures", "El problema en imágenes"),
        fig("what_is_a_wake.png", L("Schematic side view of two wind turbines in a row with the wind coming from the left. The first turbine has full wind and leaves behind a widening blue wake of slower, turbulent air; the second turbine stands inside that wake and gets slower wind and less power.", "Vista lateral esquemática de dos turbinas en fila con el viento viniendo de la izquierda. La primera recibe todo el viento y deja atrás una estela azul que se ensancha, de aire más lento y turbulento; la segunda está dentro de esa estela y recibe menos viento y produce menos."),
            K("A turbine standing inside another one's wake gets slower wind and produces less.", "Una turbina dentro de la estela de otra recibe menos viento y produce menos.")), home=False)
    add("decision", K("Which 7 of the 14 turbines should keep running?", "¿Cuáles 7 de las 14 turbinas deberían seguir funcionando?"), decision())
    add("flow", K("How QWind works", "Cómo funciona QWind").replace("QWind", 'Q<span class="wind">Wind</span>'),
        flow() + f'<p class="slide-note">{K("From the wind and the turbine positions to the turbines to keep running. Compared against exact search, simulated annealing, greedy search and random valid choice.", "Del viento y las posiciones de las turbinas a las turbinas que siguen funcionando. Comparado con la búsqueda exacta, el recocido simulado, la búsqueda voraz y la elección válida al azar.")}</p>')
    charts = [
        ("multipliers.png", K("Results: better odds of the best layout", "Resultados: más chance de la mejor elección"),
         K("Horizontal bar chart for six datasets: how many times more likely the XY mixer + Dicke circuit is to sample the best layout than random valid choice (3 to 7.5 times) and than the best penalty version (3.4 to 17.1 times); the tallest bar is Penmanshiel, 17.1 times.", "Gráfico de barras horizontales para seis conjuntos de datos: cuántas veces es más probable que el circuito con mezclador XY + Dicke muestree la mejor elección que una elección válida al azar (3 a 7,5 veces) y que la mejor versión con penalización (3,4 a 17,1 veces); la barra más alta es Penmanshiel, 17,1 veces."),
         K("How many times more likely the circuit is to sample the best layout, on six datasets.", "Cuántas veces es más probable que el circuito muestree la mejor elección, en seis conjuntos de datos.")),
        ("chance_of_best.png", K("Results: reaching the exact best layout", "Resultados: llegar a la mejor elección exacta"),
         K("Horizontal bar chart for six datasets: share of instances where the best of 1000 samples is the exact optimum. The XY mixer + Dicke circuit reaches 100% on five datasets and 67% on Penmanshiel; the penalty formulation reaches between 0% and 100%.", "Gráfico de barras horizontales para seis conjuntos de datos: porcentaje de casos en que la mejor de 1000 muestras es el óptimo exacto. El circuito con mezclador XY + Dicke llega al 100% en cinco conjuntos y al 67% en Penmanshiel; la versión con penalización llega entre 0% y 100%."),
         K("Share of instances where the best of 1000 samples is the exact best layout.", "Porcentaje de casos en que la mejor de 1000 muestras es la mejor elección exacta.")),
        ("valid_plans.png", K("Results: always a valid plan", "Resultados: siempre un plan válido"),
         K("Horizontal bar chart for six datasets: share of the circuit's probability that falls on valid layouts. The XY mixer + Dicke circuit is at 100% everywhere; the penalty formulation is between 26% and 64%.", "Gráfico de barras horizontales para seis conjuntos de datos: porcentaje de la probabilidad del circuito que cae en elecciones válidas. El circuito con mezclador XY + Dicke está en 100% en todos; la versión con penalización está entre 26% y 64%."),
         K("Share of the circuit's probability that falls on valid layouts.", "Porcentaje de la probabilidad del circuito que cae en elecciones válidas.")),
        ("depth.png", K("Results: circuit depth", "Resultados: profundidad del circuito"),
         K("Line chart for the synthetic dataset: probability of sampling the best layout at circuit depths 1, 2 and 3. The XY mixer + Dicke circuit rises from 5.0% to 7.2%; the penalty formulation stays near 1%; random valid choice is a flat line near 2%.", "Gráfico de líneas para el conjunto sintético: probabilidad de muestrear la mejor elección con profundidades 1, 2 y 3. El circuito con mezclador XY + Dicke sube de 5,0% a 7,2%; la versión con penalización queda cerca de 1%; la elección válida al azar es una línea plana cerca de 2%."),
         K("Probability of sampling the best layout at circuit depths 1, 2 and 3 (synthetic dataset).", "Probabilidad de muestrear la mejor elección con profundidades 1, 2 y 3 (conjunto sintético).")),
    ]
    for i, (img, title, alt, cap) in enumerate(charts):
        add(f"chart{i}", title, fig(img, alt, cap), home="chart")
    add("found", K("What we found", "Lo que encontramos"),
        cards([(K("3 to 7.5&times;", "3 a 7,5&times;"), K("more likely to sample the best layout than random valid choice (3.4 to 17.1&times; than the penalty version)", "más probable muestrear la mejor elección que con una elección válida al azar (3,4 a 17,1&times; que la versión con penalización)"), G),
               (K("5 of 6", "5 de 6"), K("datasets: exact best layout in every instance, matching simulated annealing with about 120 tries", "conjuntos de datos: la mejor elección exacta en todos los casos, igualando al recocido simulado con unos 120 intentos"), G),
               (K("2 of 3", "2 de 3"), K("instances on the 14 real turbines of Penmanshiel", "casos con las 14 turbinas reales de Penmanshiel"), Y),
               ("100%", K("valid plans, always, and a reproducible benchmark", "planes válidos, siempre, y una referencia reproducible"), G)], "cards-4"))
    return U


def plain(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t))


# ---------------------------------------------------------------- page assembly
def lang_block(lang, inner, tag="div", cls="", extra=""):
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c} lang="{lang}" data-lang="{lang}"{extra}>{inner}</{tag}>'


def both(fn):
    """Render fn() once per language and wrap each result in a language block."""
    global LANG
    out = []
    for lang in ("en", "es"):
        LANG = lang
        out.append((lang, fn()))
    LANG = "en"
    return out


def span2(en, es):
    return f'<span lang="en" data-lang="en">{en}</span><span lang="es" data-lang="es">{es}</span>'


def decision_short():
    """Penmanshiel map with the 4.0% vs 8.0% numbers, for the short deck."""
    return decision().replace('<div class="dmap-wrap">', '<div class="dmap-wrap short-dmap">', 1)


def short_deck(first):
    """Condensed presentation (11 slides): real hardware first, then problem, real data, impact, money, why quantum,
    how it works, key results, the classical comparison in one slide, closing."""
    U = {u["key"]: u for u in units()}
    K = L

    def slide(title, h2, body, cls=""):
        return (title, f"<h2>{h2}</h2>\n            {body}", cls)

    slides = [("QWind", first, "slide-center")]

    # 2. real hardware (the one that lands best, right after the hello)
    hw = (cards([("IonQ Forte 1", K("Real quantum computer, 36 qubits, through Qollab. A small case: 6 positions, keep 3 turbines, 997 shots, one run.", "Computadora cuántica real, 36 qubits, a través de Qollab. Un caso chico: 6 posiciones, dejar 3 turbinas, 997 disparos, una corrida."), ""),
                 ("22%", K("of the samples were invalid because of real noise; they are spotted and discarded", "de las muestras fueron inválidas por el ruido real; se detectan y se descartan"), Y)], "cards-2")
          + f'<p class="slide-note">{K("Chance of sampling the best layout, valid samples only.", "Chance de muestrear la mejor elección, solo con muestras válidas.")}</p>'
          + pbars([(K("Ideal simulator", "Simulador ideal"), d("0.1784"), 100, "pf-blue"), (K("IonQ Forte 1 (real hardware)", "IonQ Forte 1 (hardware real)"), d("0.1665"), 93, "pf-green"), (K("Random valid choice", "Elección válida al azar"), d("0.1000"), 56, "pf-red")])
          + f'<p class="slide-note">{K("Even with real noise, the best sample was the exact best layout.", "Aun con ruido real, la mejor muestra fue la mejor elección exacta.")}</p>')
    slides.append(slide(K("Real quantum hardware", "Hardware cuántico real"), K("Tested on real quantum hardware", "Probado en hardware cuántico real"), hw))

    slides.append(slide(K("The problem", "El problema"), K("The problem: turbines steal wind from each other", "El problema: las turbinas se roban viento entre sí"), U["what"]["body"]))
    slides.append(slide(K("Real data", "Datos reales"), U["data"]["title"], U["data"]["body"]))
    slides.append(slide(K("The impact", "El impacto"), U["decision"]["title"], decision_short()))
    slides.append(slide(K("The money", "El dinero"), U["money"]["title"], U["money"]["body"]))
    slides.append(slide(K("Why quantum", "Por qué cuántica"), U["why"]["title"], U["why"]["body"]))
    slides.append(slide(K("How it works", "Cómo funciona"), U["flow"]["title"], U["flow"]["body"]))

    charts = "".join(U[f"chart{i}"]["body"] for i in (0, 1, 2))
    results = (cards([("100%", K("valid plans, always", "de planes válidos, siempre"), G),
                      (K("up to 17.1&times;", "hasta 17,1&times;"), K("more likely to find the best layout than the usual quantum penalty version", "más chance de encontrar la mejor elección que la versión cuántica habitual con penalización"), G),
                      (K("5 of 6", "5 de 6"), K("datasets: the exact best layout in every case", "conjuntos de datos: la mejor elección exacta en todos los casos"), G)], "cards-3")
               + f'<div class="short-charts">{charts}</div>')
    slides.append(slide(K("Key results", "Resultados clave"), K("Key results", "Resultados clave"), results, "short-results"))

    # 10. both classical comparisons in one slide: the three cards + tries on the right, the gap table on the left
    vb, cb = U["versus"]["body"], U["competitive"]["body"]
    cards_part = vb[vb.index('<div class="cards'):vb.index('<p class="slide-note">')]
    bars_part = vb[vb.index('<p class="slide-note">'):]
    merged = f'<div class="short-versus"><div class="sv-left">{cb}</div><div class="sv-right">{cards_part}{bars_part}</div></div>'
    slides.append(slide(K("Against the classical methods", "Frente a los métodos clásicos"), U["versus"]["title"], merged, "short-versus-slide"))

    closing = (f'<h2>{K("Built on Qollab, open source, try it yourself", "Hecho en Qollab, código abierto, probalo vos")}</h2>\n            ' + cards([
        ("Qiskit + Qollab", K("Our circuit is a QAOA, built by hand in Qiskit with the hackathon kit; it runs on Qollab's built-in simulator in about 20 seconds.", "Nuestro circuito es un QAOA, hecho a mano en Qiskit con el kit del hackatón; corre en el simulador integrado de Qollab en unos 20 segundos."), ""),
        (K("Open source", "Código abierto"), K("MIT license, 150+ tests, protocol fixed before running.", "Licencia MIT, más de 150 tests, protocolo fijado antes de correr."), ""),
        (K("Try it", "Probalo"), K("Open the project page on Qollab and click <strong>Run your code</strong>.", "Abrí la página del proyecto en Qollab y hacé clic en <strong>Run your code</strong>."), "")], "cards-3")
        + f'\n            <p class="slide-lead">{K("Thank you.", "Gracias.")}</p>'
        + f'\n            <p class="slide-support"><strong>This effort is supported by Qollab &amp; IonQ</strong> · {K("MIT License", "Licencia MIT")} · <a href="https://github.com/agustindiazcano/qwind-qaoa-windfarm">github.com/agustindiazcano/qwind-qaoa-windfarm</a> · <a href="https://qollab.xyz/u/agustindiazcano/qwind">{K("Qollab project page", "Página del proyecto en Qollab")}</a> · <a href="https://youtu.be/UGVkgYGXkF4">{K("Demo video", "Video de la demo")}</a></p>')
    slides.append((K("Thank you", "Gracias"), closing, ""))
    return slides


def slides_html():
    global LANG
    out = ""
    n = None
    for lang in ("en", "es"):
        LANG = lang
        U = [u for u in units() if u["slide"]]
        # first and last slides
        first = (f'<div class="slide-brand"><img class="slide-header-img" src="img/qwind-header.png" alt="QWind, with Qollab, IonQ and Facultad de Ciencias Exactas UNICEN" width="1200" height="250">{hero_turbine()}</div>'
                 f'\n            <p class="slide-lead slide-lead-xl">{L("Quantum Optimization for Wind Farms", "Optimización cuántica para parques eólicos")}</p>'
                 f'\n            <p class="slide-kicker">{L("Quantum Impact · Hackathon submission (Qollab)", "Impacto cuántico · Proyecto del hackatón (Qollab)")}</p>'
                 '\n            <p class="slide-support"><strong>This effort is supported by Qollab &amp; IonQ</strong></p>')
        last = (f'<p class="slide-kicker">{L("Quantum Impact · Qollab x IonQ hackathon", "Impacto cuántico · Hackatón Qollab x IonQ")}</p>'
                '\n            <p class="slide-title slide-title-sm">Q<span class="wind">Wind</span></p>'
                f'\n            <p class="slide-lead">{L("Put the rule inside the circuit, and always compare against the simple baselines.", "Poné la regla dentro del circuito y comparalo siempre con las alternativas simples.")}</p>'
                f'\n            <p class="slide-support"><strong>This effort is supported by Qollab &amp; IonQ</strong> · {L("MIT License", "Licencia MIT")} · <a href="https://github.com/agustindiazcano/qwind-qaoa-windfarm">github.com/agustindiazcano/qwind-qaoa-windfarm</a> · <a href="https://qollab.xyz/u/agustindiazcano/qwind">{L("Qollab project page", "Página del proyecto en Qollab")}</a> · <a href="https://youtu.be/UGVkgYGXkF4">{L("Demo video", "Video de la demo")}</a></p>')
        slides = [("QWind", first, "slide-center")]
        slides += [(plain(u["title"]), f'<h2>{u["title"]}</h2>\n            {u["body"]}', u["cls"]) for u in U]
        slides.append((L("Thank you", "Gracias"), last, "slide-center"))
        n = len(slides)
        for i, (t, body, cls) in enumerate(slides, 1):
            label = L(f"Slide {i} of {n}: {t}", f"Diapositiva {i} de {n}: {t}")
            out += f'        <section class="slide {cls}" id="slide-{lang}-{i}" lang="{lang}" data-lang="{lang}" data-deck="full" aria-label="{esc(label)}" hidden>\n            {body}\n        </section>\n'
        short = short_deck(first)
        for i, (t, body, cls) in enumerate(short, 1):
            label = L(f"Short demo, slide {i} of {len(short)}: {t}", f"Demo corta, diapositiva {i} de {len(short)}: {t}")
            out += f'        <section class="slide {cls}" id="slide-{lang}-s{i}" lang="{lang}" data-lang="{lang}" data-deck="short" aria-label="{esc(label)}" hidden>\n            {body}\n        </section>\n'
    LANG = "en"
    return n, out


def glassify(body):
    """Home only: give the blocks the glass look and hover lift of the original home cards (slides keep their own look)."""
    body = body.replace('<div class="card ', '<div class="card glass-surface ')
    body = body.replace('<li class="flow-step ', '<li class="flow-step home-lift ')
    body = body.replace('<li><span>', '<li class="home-lift"><span>')
    body = body.replace('<figure>', '<figure class="figure-card glass-surface">')
    body = body.replace('<div class="pbars">', '<div class="pbars home-box glass-surface">')
    body = body.replace('<div class="dmap-wrap">', '<div class="dmap-wrap home-box glass-surface">')
    body = body.replace('<div class="switches"', '<div class="switches home-box glass-surface"')
    body = re.sub(r'<table class="slide-table.*?</table>', lambda m: f'<div class="home-box glass-surface"><div class="table-wrap">{m.group(0)}</div></div>', body, flags=re.S)
    body = body.replace('<svg class="illus"', '<div class="home-box glass-surface"><svg class="illus"', 1)
    if '<div class="home-box glass-surface"><svg class="illus"' in body:
        body = body.replace('</svg>', '</svg></div>', 1)
    return body


def home_html():
    globals()["CTX"] = "home"
    parts = []
    for lang, _ in (("en", 0), ("es", 0)):
        pass
    for lang in ("en", "es"):
        globals()["LANG"] = lang
        vtitle = L("QWind demo video", "Video de la demo de QWind")
        h = (f'\n        <section class="home-section"><h2 class="section-title">{L("Watch the demo", "Mirá la demo")}</h2>'
             f'<div class="video-frame home-box glass-surface"><iframe src="https://www.youtube-nocookie.com/embed/UGVkgYGXkF4" title="{vtitle}" loading="lazy" '
             'allow="accelerometer; encrypted-media; picture-in-picture; fullscreen" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>'
             f'<p class="slide-note">{L("Prefer YouTube?", "¿Preferís YouTube?")} <a href="https://youtu.be/UGVkgYGXkF4">youtu.be/UGVkgYGXkF4</a></p></section>')
        charts = ""
        for u in units():
            if u["home"] is False:
                continue
            if u["home"] == "details":
                h += f'\n        <details class="home-details"><summary>{u["title"]}</summary>{glassify(u["body"])}</details>'
            elif u["home"] == "chart":
                charts += f'<div class="chart-card"><h3>{u["title"]}</h3>{glassify(u["body"])}</div>'
            else:
                h += f'\n        <section class="home-section"><h2 class="section-title">{u["title"]}</h2>{glassify(u["body"])}</section>'
            if u["key"] == "decision":
                pass
        h += (f'\n        <section class="home-section"><h2 class="section-title">{L("More charts", "Más gráficos")}</h2>'
              f'<p class="slide-note">{L("The charts are in English.", "Los gráficos están en inglés.")}</p><div class="chart-grid">{charts}</div></section>')
        parts.append(lang_block(lang, h, cls="home-story"))
    globals()["LANG"] = "en"
    globals()["CTX"] = "slide"
    return "\n        ".join(parts)


def hero_html():
    parts = []
    for lang in ("en", "es"):
        globals()["LANG"] = lang
        inner = (f'<p>{L("QWind is a quantum algorithm that decides <strong>which wind turbines to keep running</strong> when a farm has to produce less, so the energy lost to wakes is as small as possible. Our circuit never proposes an invalid plan, and we tested it on real wind farms.", "QWind es un algoritmo cuántico que decide <strong>qué turbinas eólicas dejar funcionando</strong> cuando un parque tiene que producir menos, para que la energía perdida por estelas sea la menor posible. Nuestro circuito nunca propone un plan inválido, y lo probamos en parques eólicos reales.")}</p>'
                 '<ul class="summary-list">'
                 f'<li>{L("<strong>3 to 7.5 times</strong> more likely to find the best layout than a random valid choice, and <strong>3.4 to 17.1 times</strong> more likely than the usual penalty approach.", "<strong>De 3 a 7,5 veces</strong> más probable encontrar la mejor elección que con una elección válida al azar, y <strong>de 3,4 a 17,1 veces</strong> más que con el enfoque habitual de penalización.")}</li>'
                 f'<li>{L("<strong>The exact best layout</strong> in every test of 5 of 6 datasets, matching a classical method (simulated annealing) with about 120 tries.", "<strong>La mejor elección exacta</strong> en todas las pruebas de 5 de 6 conjuntos de datos, igualando a un método clásico (recocido simulado) con unos 120 intentos.")}</li>'
                 f'<li>{L("<strong>100% valid plans:</strong> the rule &quot;keep exactly K turbines&quot; is built into the circuit. We claim no quantum advantage.", "<strong>100% de planes válidos:</strong> la regla &quot;dejar exactamente K turbinas&quot; está dentro del circuito. No afirmamos ventaja cuántica.")}</li>'
                 '</ul>')
        parts.append(lang_block(lang, inner, cls="hero-text"))
    globals()["LANG"] = "en"
    return "\n        ".join(parts)


def badge_html():
    return span2('Runs on real quantum hardware:', 'Corre en hardware cuántico real:')


def team_html():
    return ('<ul class="demo-team">'
            f'<li><strong>Agustin Diaz-Cano</strong> {span2("MS Candidate, Information Systems Engineering", "Maestrando, Ingeniería en Sistemas de Información")}</li>'
            f'<li><strong>Baltazar Salerno</strong> {span2("Frontend Developer", "Desarrollador Frontend")}</li></ul>')


def results_details():
    th = lambda en, es: f'<th scope="col">{span2(en, es)}</th>'
    return f"""        <details class="home-details results-details">
            <summary>{span2("Technical results by dataset", "Resultados técnicos por conjunto de datos")}</summary>
            <div class="results-box glass-surface">
                <div class="results-controls">
                    <label for="datasetSelect">{span2("Dataset", "Conjunto de datos")}</label>
                    <select id="datasetSelect" disabled></select>
                    <span id="resultsMeta" class="results-meta"></span>
                </div>
                <div class="table-scroll" tabindex="0" role="region" aria-labelledby="results-title">
                    <h3 id="results-title" class="visually-hidden">{span2("Results by dataset", "Resultados por conjunto de datos")}</h3>
                    <table class="results-table" id="resultsTable">
                        <caption id="resultsCaption">{span2("Loading results...", "Cargando resultados...")}</caption>
                        <thead>
                            <tr>
                                {th("Method", "Método")}
                                {th("Variant", "Variante")}
                                <th scope="col">p</th>
                                <th scope="col">P(optimal)</th>
                                <th scope="col">P(valid)</th>
                                {th("Energy gap", "Brecha de energía")}
                                {th("Time (s)", "Tiempo (s)")}
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
                <noscript><p class="note">{span2("The results tables need JavaScript. The same numbers are in the README of the repository.", "Las tablas de resultados necesitan JavaScript. Los mismos números están en el README del repositorio.")}</p></noscript>
                <p class="note" id="resultsNotes">{span2("Means over the instances of each dataset, read from <code>data/summary.json</code> (copy of <code>results/summary.json</code>). P(optimal) is the probability of sampling the best layout, P(valid) the share of probability on valid layouts, energy gap the distance to the exact optimum (0 is optimal).", "Promedios sobre los casos de cada conjunto de datos, leídos de <code>data/summary.json</code> (copia de <code>results/summary.json</code>). P(optimal) es la probabilidad de muestrear la mejor elección, P(valid) el porcentaje de probabilidad en elecciones válidas y la brecha de energía la distancia al óptimo exacto (0 es óptimo).")}</p>
            </div>
        </details>"""


GITHUB_SVG = '<svg viewBox="0 0 16 16" width="17" height="17" aria-hidden="true" focusable="false"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>'
YT_SVG = '<svg viewBox="0 0 24 17" width="22" height="16" aria-hidden="true" focusable="false"><path fill="currentColor" fill-rule="evenodd" d="M4 0h16a4 4 0 014 4v9a4 4 0 01-4 4H4a4 4 0 01-4-4V4a4 4 0 014-4zm5.5 4.5v8l7-4z"/></svg>'


THEME_ICONS = ('<svg class="i-sun" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
               '<svg class="i-moon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"/></svg>')


def nav_html(n):
    buttons = "".join(f'            <button type="button" class="slide-btn" data-slide="{i}" aria-label="Slide {i}" data-es-label="Diapositiva {i}">{i}</button>\n' for i in range(1, n + 1))
    return f"""    <!-- NAVBAR WITH GLASS SURFACE -->
    <nav class="glass-surface" aria-label="Site" data-es-label="Sitio">
        <a class="nav-logo" href="index.html" aria-label="QWind, back to the top" data-es-label="QWind, volver al inicio">Q<span>Wind</span></a>
        <div class="nav-links">
            <a class="btn btn-icon" href="https://github.com/agustindiazcano/qwind-qaoa-windfarm" aria-label="GitHub repository" data-es-label="Repositorio de GitHub">{GITHUB_SVG}</a>
            <a class="btn" href="https://qollab.xyz/u/agustindiazcano/qwind">{span2("Qollab page", "Página en Qollab")}</a>
            <a class="btn btn-icon" href="https://youtu.be/UGVkgYGXkF4" aria-label="Demo video on YouTube" data-es-label="Video de la demo en YouTube">{YT_SVG}</a>
            <a class="btn" href="references.html"{{{{current:references.html}}}}>{span2("References", "Referencias")}</a>
            <a class="btn" href="team.html"{{{{current:team.html}}}}>{span2("Team", "Equipo")}</a>
        </div>
{{{{#demo}}}}
        <div class="demo-nav" id="demoNav" role="group" aria-label="Demo slides" data-es-label="Diapositivas del demo" hidden>
{buttons}        </div>
{{{{/demo}}}}
        <div class="lang-switch" role="group" aria-label="Language" data-es-label="Idioma">
            <button type="button" class="lang-btn" data-set-lang="en" aria-pressed="true" aria-label="English">EN</button>
            <button type="button" class="lang-btn" data-set-lang="es" aria-pressed="false" aria-label="Español">ES</button>
        </div>
        <button type="button" class="theme-toggle" id="themeToggle" aria-pressed="false" aria-label="Switch to light mode">{THEME_ICONS}</button>
{{{{#demo}}}}
        <div class="demo-switch">
            <button type="button" class="demo-toggle" id="demoToggle" role="switch" aria-checked="false" aria-label="Demo mode" data-es-label="Modo demo"><span class="knob" aria-hidden="true"></span></button>
            <span class="demo-label">demo</span>
        </div>
{{{{/demo}}}}
{{{{^demo}}}}
        <span class="nav-spacer" aria-hidden="true"></span>
{{{{/demo}}}}
    </nav>
{{{{#demo}}}}
    <div class="short-switch" id="shortSwitch" hidden>
        <button type="button" class="demo-toggle" id="shortToggle" role="switch" aria-checked="false" aria-label="Short demo" data-es-label="Demo corta"><span class="knob" aria-hidden="true"></span></button>
        <span class="demo-label">{span2("short demo", "demo corta")}</span>
    </div>
{{{{/demo}}}}
"""


def index_html():
    n, slides = slides_html()
    return f"""---
title: QWind — Quantum Wind Farm Optimization
demo: true
---
{{{{> head}}}}

{{{{> nav}}}}

    <!-- HERO WITH CYCLING SPLIT-FLAP (generated by scripts/build_story.py) -->
    <header>
        <div class="hero-brand">
            {hero_turbine()}
            <h1 class="split-flap-container" id="splitFlap" aria-label="QWind">
                <div class="split-flap-char" data-target="Q" aria-hidden="true">Q</div>
                <div class="split-flap-char" data-target="W" aria-hidden="true">W</div>
                <div class="split-flap-char" data-target="i" aria-hidden="true">i</div>
                <div class="split-flap-char" data-target="n" aria-hidden="true">n</div>
                <div class="split-flap-char" data-target="d" aria-hidden="true">d</div>
            </h1>
        </div>

        <div class="badge-pill">
            {badge_html()}
            <a href="https://github.com/agustindiazcano/qwind-qaoa-windfarm#run-on-real-quantum-hardware">IonQ Forte 1 (36q)</a>
        </div>

        {hero_html()}
    </header>

    <!-- MAIN CONTENT: same story as the demo slides, in plain language -->
    <main id="main">
        {home_html()}

{results_details()}
    </main>

{{{{> footer}}}}

{{{{> totop_button}}}}

    <!-- DEMO MODE: {n} full-screen slides per language, same order as the README, shown only when the Demo switch is on -->
    <div id="demo" hidden>
{slides}        <footer class="demo-footer">
            <div class="demo-footer-logos">
                <a class="demo-logo" href="https://qollab.xyz/"><img src="img/qollab-mark.svg" alt="" width="28" height="28"><span>Qollab</span></a>
                <a class="demo-logo" href="https://ionq.com/"><img src="img/ionq-logo.svg" alt="IonQ" width="78" height="28"></a>
                <a class="demo-logo demo-logo-light" href="https://exa.unicen.edu.ar/"><img src="img/unicen-logo.png" alt="Facultad de Ciencias Exactas, UNICEN" width="104" height="28"></a>
            </div>
            {team_html()}
        </footer>
    </div>

{{{{> index_scripts}}}}

{{{{> totop_script}}}}
{{{{> scroll_bg}}}}

</body>
</html>
"""


def render():
    global LANG
    LANG = "en"
    n, _ = slides_html()
    return {"index": index_html(), "nav": nav_html(n)}


def main(argv):
    out = render()
    targets = {"index": os.path.join(ROOT, "web-src", "pages", "index.html"), "nav": os.path.join(ROOT, "web-src", "partials", "nav.html")}
    if "--check" in argv:
        bad = []
        for k, path in targets.items():
            with open(path, encoding="utf-8", newline="") as f:
                if f.read().replace("\r\n", "\n") != out[k]:
                    bad.append(path)
        if bad:
            print("out of date:", ", ".join(bad), "- run python scripts/build_story.py")
            return 1
        return 0
    for k, path in targets.items():
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(out[k])
        print("wrote", os.path.relpath(path, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
