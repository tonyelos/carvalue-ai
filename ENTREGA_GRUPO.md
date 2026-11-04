# Entrega · CarValue AI

**Grupo:** CarValue AI — Yiao TANG y Luis Wesinger
**Profesor:** José Luis Gómez Ortega
**Repositorio GitHub (público):** https://github.com/tonyelos/carvalue-ai

| Integrante | Parte implementada | Rama | 2 commits propios | URL del PR | ¿Quién revisó? |
|---|---|---|---|---|---|
| Yiao TANG (`tonyelos`) | Infraestructura Docker (A1–A4), persistencia SQLAlchemy (A5–A6), ingesta Notebook (A7–A8) y plantillas HTML (C2–C3) | `feature/infra-datos-web`, `feature/db-templates` | Sí (4 + 3 commits) | [PR #1](https://github.com/tonyelos/carvalue-ai/pull/1) · [PR #3](https://github.com/tonyelos/carvalue-ai/pull/3) | Luis Wesinger |
| Luis Wesinger (`luiswesinger`) | Predicción ML (B1), orquestación de la ruta Flask `/tasar` (B2) y Cohere Vision (C1-A prompt, C1-B API multimodal) | `feature/api-vision` | Sí (3 commits + 1 refactor) | [PR #2](https://github.com/tonyelos/carvalue-ai/pull/2) | Yiao TANG |

## Pruebas de funcionamiento

- [x] Docker Compose: 3 servicios activos (`db`, `app`, `jupyter`).
- [x] `SELECT COUNT(*) FROM anuncios` devuelve **50000**.
- [x] `GET /health` OK (`{"service": "carvalue", "status": "ok"}`).
- [x] Formulario POST sin JavaScript; fotografía recibida en Flask.
- [x] Modo `MOCK` integra modelo ML + SQLAlchemy y guarda tasación.
- [x] `/historial` muestra la tasación.
- [x] Modo real Cohere (`VISION_MOCK=0`): código multimodal implementado al completo (`cohere.ClientV2`, Base64, control de excepciones). **No se pudo probar con una clave/cuota activa**; el circuito completo se verificó con `VISION_MOCK=1` y la incidencia se documenta sin presentar el mock como análisis real.
- [x] `docker compose exec app pytest -q`: **6 tests superados (6/6 passed)**.
- [x] `.env` no está versionado.
- [x] Prompt propio escrito en `app/vision.py` (vocabulario cerrado, sin inferir mecánica, salida JSON estricta).
- [x] Formulario HTML y página de resultado programados por el equipo.

## Reflexión breve (4 preguntas)

**1. HTTP frente a SQL:**
HTTP es un protocolo de aplicación sin estado basado en peticiones y respuestas cliente-servidor (el navegador envía el formulario con POST y recibe HTML renderizado; Flask se comunica con servicios externos mediante REST). SQL es el lenguaje declarativo que opera sobre una conexión de base de datos dedicada (gestionada por SQLAlchemy y psycopg en `app/db.py`) para persistir registros estructurados y consultar `tasaciones` y `anuncios` en PostgreSQL.

**2. Host `db` frente a `localhost`:**
Dentro de la red interna de Docker Compose, cada contenedor tiene su propio espacio de red; desde el contenedor `app`, `localhost` apuntaría a sí mismo, mientras que `db` es el nombre de servicio que el DNS interno de Docker resuelve a la IP del contenedor PostgreSQL. En cambio, `localhost:5000` se usa desde el navegador del ordenador anfitrión porque el puerto está expuesto y mapeado al host.

**3. Valor del PR respecto a commits directos en `main`:**
El Pull Request actúa como barrera de calidad: aísla los cambios en ramas de funcionalidad, obliga a una revisión cruzada formal antes de integrar, evita roturas y colisiones directas en `main`, y documenta el propósito, las decisiones técnicas y las pruebas ejecutadas.

**4. Qué hacemos si Cohere devuelve `unknown`:**
Se interrumpe inmediatamente el flujo de tasación con un error descriptivo y HTTP 400. Nunca se asigna una categoría por defecto (como `good`), porque falsearía la tasación haciendo pasar por válida una estimación arbitraria ante una fotografía insuficiente o no reconocible.

## Incidencias que no pudimos resolver (si las hay)

- Prueba real de Cohere: sin clave/cuota activa en el entorno de evaluación; se verificó el circuito completo en modo `MOCK` y se documenta la incidencia sin falsear el resultado.
- En macOS el puerto 5000 estaba ocupado por el receptor de AirPlay; la aplicación se probó en el host con el puerto 5001 mediante un override temporal no versionado. En Linux (NixOS) se usa el 5000 estándar.
- `nbconvert` avisa de que el notebook no tiene `id` de celda (nbformat); es un aviso no bloqueante y la ejecución termina correctamente.

## BONUS (solo si se ha hecho)

- [ ] `/estadisticas` muestra gráfica(s) basadas en consultas a PostgreSQL `anuncios`.
- [ ] `/estadisticas/grafico.png` responde `image/png`.
- [ ] PR `feature/dashboard` revisado: URL ___

## Decisiones de implementación

**Criterio del prompt (cómo definimos las categorías y el caso `unknown`):**
El prompt delimita la evaluación al estado exterior visible de la carrocería y la pintura, prohibiendo deducciones mecánicas o de motor. Obliga a elegir entre cuatro categorías cerradas (`like new`, `excellent`, `good`, `fair`), devuelve `unknown` si la foto no permite una valoración clara (imágenes borrosas, piezas sueltas, fotos no automovilísticas) y exige una salida JSON pura sin bloques markdown.

**Decisión del HTML (atributos de formulario y envío de foto):**
Se prescindió totalmente de JavaScript, usando HTML estándar con Jinja2. El formulario emplea `method="post"`, `action="/tasar"` y `enctype="multipart/form-data"` para transferir el fichero binario. Los desplegables se llenan dinámicamente con las constantes válidas del dataset. No existe selector de estado, ya que la condición proviene exclusivamente del análisis visual.
