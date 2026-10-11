# PENDING-FRONT: estado de la web

La web (`web/`, landing de GitHub Pages) ya está construida: Home, References y Team, en HTML, CSS y JavaScript puros. Las páginas se generan desde `web-src/` (`partials/` y `pages/`) con `python scripts/build_web.py`; se edita `web-src/`, nunca `web/*.html` (`tests/test_build_web.py` falla si se desincronizan).

## Reglas que no se pueden romper

- **Todo número de la web sale de un archivo de `results/`.** Nada escrito a mano; las tablas leen `web/data/summary.json` (`python scripts/sync_results_to_web.py`).
- **No se afirma ventaja cuántica, aceleración ni ahorro.** Es una regla del proyecto (`AGENTS.md`). Las estimaciones de impacto (`docs/IMPACT.md`) son ilustrativas, no medidas.
- **Accesibilidad:** contraste suficiente, navegación con teclado, texto alternativo (`alt`) en cada figura, subtítulos en el video.
- **Licencia MIT** para lo publicado; los datos mantienen su atribución (CC BY 4.0, ver `web/references.html` y el README).
- La web es **estática**; JavaScript solo para leer `summary.json` y para la interfaz.

## Estado

| # | Prioridad | Tarea | Estado |
|---|---|---|---|
| 1 | 🔴 | Botón de YouTube con la URL pública del video con subtítulos (hoy es un `TODO(owner)` en `web-src/partials/nav.html`; luego `python scripts/build_web.py`) | [ ] |
| 2 | 🟡 | Lanzar a mano el flujo "Deploy to GitHub Pages" (`.github/workflows/pages.yml`, solo `workflow_dispatch`, después de mergear); comprobar que Pages esté activado con la fuente "GitHub Actions" | [ ] |
| 3 | 🟡 | Poner la URL resultante en "Project Website" de la página de Qollab (lo hace quien tiene la cuenta) | [ ] |
| 4 | 🟢 | Revisar con teclado (Tab) y zoom al 200% la versión final antes de publicar | [ ] |
| 5 | ✅ | `lang="en"`, `<h1>`, `:focus-visible`, enlace "Skip to content", modo oscuro con `prefers-color-scheme` | [x] |
| 6 | ✅ | Figuras con `alt` copiadas dentro de `web/img/` (Pages solo publica `web/`), cabecera con IonQ Forte 1 y multiplicadores | [x] |
| 7 | ✅ | Línea `This effort is supported by Qollab & IonQ`, atribuciones de datos, enlaces al repositorio, a Qollab y a la sección de hardware | [x] |
| 8 | ✅ | Tablas leídas de `web/data/summary.json` | [x] |

## Imágenes (generadas en `results/figures/`)

`what_is_a_wake.png`, `the_decision.png`, `how_it_works.png`, `multipliers.png`, `chance_of_best.png`, `valid_plans.png`, `depth.png`. El texto alternativo está en el `README.md` (secciones "The problem in pictures" y "Results at a glance"). Se regeneran con `python experiments/make_figures.py` y `python experiments/make_illustrations.py`.

## Antes de abrir un PR

- Una rama por tarea, PR con revisión humana, sin merge propio (`AGENTS.md`).
- Comprobar que cada imagen tiene `alt` y que cada número viene de `results/`.
- Hablar con quien mantiene el README si se cambia el discurso: la historia es "poner la restricción dentro del circuito mejora mucho la probabilidad del óptimo; competitivo con los métodos clásicos a estos tamaños; sin afirmar ventaja".
