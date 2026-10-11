# PENDING-FRONT: lo que falta en la web

Lista para quien trabaja en `web/` (landing de GitHub Pages). El resto del proyecto ya está en `main`; lo que falta es que la web cuente lo mismo que el README, con buena accesibilidad.

Estado actual de `web/` (revisado en `main`): `index.html` (~5 KB) y `styles.css` (~6,5 KB), con `<nav>` y `<main>`, dos secciones ("Simulación y Esquemas" y "Core Team"), `lang="es"`, **sin imágenes, sin resultados, sin carpeta `web/data/`, sin estilos de foco, sin enlace para saltar al contenido y sin modo oscuro**.

## Reglas que no se pueden romper

- **Todo número de la web sale de un archivo de `results/`.** Nada escrito a mano. Si hace falta una cifra, copiarla del README (que se genera desde `results/`) o leer `web/data/summary.json`.
- **No se afirma ventaja cuántica, aceleración ni ahorro.** Es una regla del proyecto (`agents.md`). Las estimaciones de impacto están en `docs/IMPACT.md` y hay que presentarlas como lo que son: ilustrativas, no medidas.
- **Accesibilidad:** contraste suficiente, navegación con teclado, texto alternativo (`alt`) en cada figura, subtítulos en el video. Es un requisito de la hackathon.
- **Licencia MIT** para todo lo que se publique; los datos mantienen su atribución (CC BY 4.0, ver el pie del README).
- La web es **estática**: HTML y CSS (un poco de JavaScript solo si se leen tablas de `summary.json`).

## Corregir lo que ya existe

| # | Prioridad | Tarea | Hecho |
|---|---|---|---|
| 1 | 🔴 | Cambiar `<html lang="es">` por `lang="en"` y pasar los textos al inglés (proyecto, README y jurado están en inglés) | [ ] |
| 2 | 🔴 | Añadir un `<h1>` (hoy solo hay `<h2>`) | [ ] |
| 3 | 🔴 | Estilos de foco visibles para teclado (`:focus-visible`) en enlaces y botones | [ ] |
| 4 | 🟡 | Enlace "Skip to content" al inicio de la página | [ ] |
| 5 | 🟡 | Revisar el contraste del texto y de los botones (mínimo 4,5:1) | [ ] |
| 6 | 🟢 | Modo oscuro con `prefers-color-scheme` | [ ] |

Fragmentos útiles:

```html
<a class="skip-link" href="#main">Skip to content</a>
<main id="main"> ... </main>
```

```css
:focus-visible { outline: 3px solid #2a78d6; outline-offset: 2px; }
.skip-link { position: absolute; left: -999px; }
.skip-link:focus { left: 8px; top: 8px; background: #fff; padding: 8px 12px; z-index: 10; }
```

## Contenido que falta

| # | Prioridad | Tarea | Hecho |
|---|---|---|---|
| 7 | 🔴 | Mostrar los **4 gráficos y las 3 ilustraciones** con `alt` (lista de archivos abajo) | [ ] |
| 8 | 🔴 | **Copiar esas imágenes dentro de `web/`** (por ejemplo `web/img/`): el flujo de Pages solo publica la carpeta `web/`, no se pueden enlazar desde `results/` | [ ] |
| 9 | 🔴 | Cabecera con lo mejor: resumen de tres líneas, la línea de **IonQ Forte 1 (36q)** y los multiplicadores (3 a 7,5 veces frente al azar válido y 3,4 a 17,1 veces frente a la penalización) | [ ] |
| 10 | 🟡 | Botones a: el repositorio, la página de Qollab, el README y el video (el video debe llevar subtítulos) | [ ] |
| 11 | 🟡 | La línea obligatoria `This effort is supported by Qollab & IonQ` y las atribuciones de los datos (ver "Data and sources" al final del README) | [ ] |
| 12 | 🟢 | Tablas de resultados leídas de `web/data/summary.json` (necesita un poco de JavaScript) | [ ] |

### Imágenes (ya generadas en `results/figures/`)

| Archivo | Qué muestra |
|---|---|
| `what_is_a_wake.png` | Qué es una estela: una turbina y otra dentro de su estela |
| `the_decision.png` | Las 14 turbinas reales de Penmanshiel (Escocia) y las 7 que se mantienen |
| `how_it_works.png` | El esquema de cinco pasos de QWind |
| `multipliers.png` | Cuántas veces más probable es hallar el mejor layout |
| `chance_of_best.png` | Porcentaje de instancias donde la mejor muestra es el óptimo exacto |
| `valid_plans.png` | Porcentaje de planes válidos: 100% frente a 26% a 64% |
| `depth.png` | Probabilidad de hallar el mejor layout según la profundidad del circuito |

El **texto alternativo de cada una ya está escrito** en el `README.md` (secciones "The problem in pictures" y "Results at a glance"): copiarlo tal cual. Se regeneran con `python experiments/make_figures.py` y `python experiments/make_illustrations.py`.

## Publicar

| # | Prioridad | Tarea | Hecho |
|---|---|---|---|
| 13 | 🟡 | Si se hace el punto 12: ejecutar `python scripts/sync_results_to_web.py` (copia `results/summary.json` a `web/data/summary.json`; se niega a copiar un resumen de prueba) | [ ] |
| 14 | 🟡 | Lanzar a mano el flujo "Deploy to GitHub Pages" (`.github/workflows/pages.yml`, solo se ejecuta con `workflow_dispatch`, después de mergear). Hay que comprobar que Pages esté activado en la configuración del repositorio con la fuente "GitHub Actions" | [ ] |
| 15 | 🟢 | Poner la URL resultante en el campo "Project Website" de la página de Qollab (lo hace quien tiene la cuenta) | [ ] |

## Antes de abrir el PR

- Una rama por tarea, PR con revisión humana, sin merge propio (`agents.md`).
- Probar la página con el teclado (Tab recorre todo y el foco se ve) y con el zoom al 200%.
- Comprobar que cada imagen tiene `alt` y que cada número viene de `results/`.
- Hablar con quien mantiene el README si se cambia el discurso: la historia es "poner la restricción dentro del circuito mejora mucho la probabilidad del óptimo; competitivo con los métodos clásicos a estos tamaños; sin afirmar ventaja".
