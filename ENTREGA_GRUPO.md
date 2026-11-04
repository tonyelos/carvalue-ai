# Entrega · CarValue AI

**Grupo:** Equipo CarValue AI — Yiao TANG y Luis Wesinger
**Profesor:** José Luis Gómez Ortega
**Repositorio GitHub (público):** https://github.com/tonyelos/carvalue-ai

| Integrante | Parte implementada | Rama | 2 commits propios | URL del PR | ¿Quién revisó? |
|---|---|---|---|---|---|
| Yiao TANG (`tonyelos`) | Infraestructura, datos, persistencia y web: A1–A8, C2–C3 | `feature/infra-datos-web`, `feature/db-templates` | Sí (4 + 3 commits) | [PR #1](https://github.com/tonyelos/carvalue-ai/pull/1) · [PR #3](https://github.com/tonyelos/carvalue-ai/pull/3) | Luis Wesinger |
| Luis Wesinger (`luiswesinger`) | API, modelo ML y Cohere Vision: B1–B2, C1 | `feature/api-vision` | Sí (3 commits + 1 refactor) | [PR #2](https://github.com/tonyelos/carvalue-ai/pull/2) | Yiao TANG |

## Pruebas de funcionamiento

- [x] Docker Compose: 3 servicios activos (`db`, `app`, `jupyter`).
- [x] `SELECT COUNT(*) FROM anuncios` devuelve **50000**.
- [x] `GET /health` OK.
- [x] Formulario POST sin JavaScript; fotografía recibida en Flask.
- [x] Modo `MOCK` integra modelo ML + SQLAlchemy y guarda tasación.
- [x] `/historial` muestra la tasación.
- [ ] Modo real Cohere (`VISION_MOCK=0`): **pendiente de probar con clave propia**; el modo `MOCK` está verificado de extremo a extremo. Se documenta la incidencia sin presentar el mock como análisis real.
- [x] `docker compose exec app pytest -q`: **6 tests superados**.
- [x] `.env` no está versionado.
- [x] Prompt propio escrito en `app/vision.py` (sin usar uno prefabricado).
- [x] Formulario HTML y página de resultado programados por el equipo.

## Reflexión breve (4 preguntas)

**1. HTTP frente a SQL:**
HTTP se usa entre el navegador y Flask (formulario `POST /tasar`, respuesta HTML y API JSON); SQL se usa entre Flask/Jupyter y PostgreSQL (SQLAlchemy) para persistir y consultar `tasaciones` y `anuncios`. Son dos canales distintos: uno transporta la petición web y el otro habla con la base de datos.

**2. Host `db` frente a `localhost`:**
Dentro de Docker Compose, `db` es el nombre del servicio y se resuelve por la red interna de Compose; `localhost` dentro del contenedor apunta al propio contenedor, no a PostgreSQL. Desde el navegador del host se usa `localhost:5000` (o `5001` en macOS si AirPlay ocupa el 5000).

**3. Valor del PR respecto a commits directos en `main`:**
Permite revisar el diff antes de integrar, discutir cambios, dejar evidencia de revisión cruzada y evitar que un error rompa `main`. Además deja trazabilidad de quién propuso, quién revisó y cuándo se fusionó.

**4. Qué hacemos si Cohere devuelve `unknown`:**
Se detiene el flujo: no se llama al modelo, no se guarda tasación y se muestra un error comprensible pidiendo una foto mejor. No se inventa un estado ni se usa `good` por defecto, porque sería una predicción basada en un dato falso.

## Incidencias que no pudimos resolver (si las hay)

- En macOS, el puerto 5000 estaba ocupado por el receptor de AirPlay; la aplicación se probó en el host con el puerto 5001 mediante un override temporal no versionado. En Linux (NixOS) se usa el 5000 estándar.
- La prueba real de Cohere queda pendiente por falta de clave en el entorno de pruebas; se verificó el circuito completo con `VISION_MOCK=1`.
- `nbconvert` avisa de que el notebook no tiene `id` de celda (nbformat); es un aviso no bloqueante y la ejecución termina correctamente.

## BONUS (solo si se ha hecho)

- [ ] `/estadisticas` muestra gráfica(s) basadas en consultas a PostgreSQL `anuncios`.
- [ ] `/estadisticas/grafico.png` responde `image/png`.
- [ ] PR `feature/dashboard` revisado: URL ___

## Decisiones de implementación

**Criterio del prompt (cómo definimos las categorías y el caso `unknown`):**
Se pidió al modelo evaluar solo el exterior visible, con vocabulario cerrado (`like new`, `excellent`, `good`, `fair`), prohibiendo inferir motor, accidentes o kilometraje real. Si la imagen no permite una valoración razonable, debe responder `unknown`; la salida es un JSON con `condition` y `reason` en español, sin markdown ni campos extra.

**Decisión del HTML (atributos de formulario y envío de foto):**
Formulario `POST` a `/tasar` con `enctype="multipart/form-data"`, campos `name` exactos del contrato, `select` generados con bucles Jinja2 sobre `opciones.*`, años 1995–2021, millas 1.000–250.000, foto `accept="image/jpeg,image/png,image/webp"` y sin campo `condition` (lo determina la visión). Sin JavaScript.
