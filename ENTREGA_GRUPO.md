# Entrega · CarValue AI

**Grupo:** Grupo Luis Wesinger & Yiao TANG

**Repositorio GitHub (privado, con acceso al profesor):** https://github.com/tonyelos/carvalue-ai

| Integrante | Parte implementada | Rama | 2 commits propios | URL del PR | ¿Quién revisó? |
|---|---|---|---|---|---|
| Yiao TANG (`tonyelos`) | Infraestructura Docker (A1-A4), DB SQLAlchemy (A5-A6), Ingesta Notebook (A7-A8) y Plantillas HTML (C2-C3) | `feature/infra-datos-web`, `feature/db-templates` | Sí | https://github.com/tonyelos/carvalue-ai/pull/1 , https://github.com/tonyelos/carvalue-ai/pull/3 | Luis Wesinger (`luiswesinger`) |
| Luis Wesinger (`luiswesinger`) | Predicción ML (B1), Orquestación ruta Flask `/tasar` (B2) y Cohere Vision (C1-A Prompt, C1-B API Multimodal) | `feature/api-vision` | Sí | https://github.com/tonyelos/carvalue-ai/pull/2 | Yiao TANG (`tonyelos`) |

## Pruebas de funcionamiento

- [x] Docker Compose: 3 servicios activos (`db`, `app`, `jupyter`).
- [x] `SELECT COUNT(*) FROM anuncios` devuelve 50000.
- [x] `GET /health` OK (`{"service": "carvalue", "status": "ok"}`).
- [x] Formulario POST sin JavaScript; fotografía recibida en Flask.
- [x] Modo `MOCK` integra modelo ML + SQLAlchemy y guarda tasación.
- [x] `/historial` muestra tasación.
- [x] Modo real Cohere (`VISION_MOCK=0`): código multimodal implementado al completo con `cohere.ClientV2`, Base64 y control de excepciones. Por falta de cuota/clave de API activa en el entorno de evaluación, se ha verificado el circuito completo en modo `VISION_MOCK=1` tal y como indica la guía, sin falsear la prueba.
- [x] `docker compose exec app pytest -q`: 6 tests superados (6/6 passed).
- [x] `.env` no está versionado.
- [x] Prompt propio escrito en `app/vision.py` (vocabulario cerrado, sin inferir mecánica, output JSON estricto).
- [x] Formulario HTML y página de resultado programados por el equipo.

## Reflexión breve (4 preguntas)

**1. HTTP frente a SQL:** 
HTTP es un protocolo de nivel de aplicación sin estado basado en peticiones y respuestas cliente-servidor (el navegador envía datos con POST y recibe HTML renderizado; Flask se comunica con servicios externos mediante REST). SQL es el lenguaje de consulta declarativo que opera sobre una conexión de base de datos dedicada (manejada por SQLAlchemy y psycopg en `app/db.py`) para gestionar transacciones ACID y persistir registros estructurados en PostgreSQL.

**2. Host `db` frente a `localhost`:** 
Dentro de la red interna de Docker Compose, cada contenedor dispone de su propio espacio de red aislado; por tanto, desde el contenedor `app`, `localhost` apuntaría a sí mismo, mientras que `db` es el nombre de servicio que el servidor DNS interno de Docker resuelve a la dirección IP del contenedor PostgreSQL. Por el contrario, `localhost:5000` se utiliza desde el navegador del ordenador anfitrión porque el puerto 5000 está expuesto y mapeado al host.

**3. Valor del PR respecto a commits directos en `main`:** 
El Pull Request actúa como una barrera de calidad fundamental: aísla los cambios en ramas de funcionalidad, obliga a una revisión cruzada formal por parte de otro compañero antes de la integración, previene roturas y colisiones directas en `main`, y documenta el propósito, las decisiones técnicas y las pruebas ejecutadas.

**4. Qué hacemos si Cohere devuelve `unknown`:** 
Interrumpimos inmediatamente el flujo de tasación lanzando un error descriptivo con código HTTP 400. Nunca debemos asignar una categoría por defecto (como `good`), ya que falsearía la tasación haciendo pasar por válida una estimación arbitraria ante una fotografía insuficiente o no reconocible.

## Incidencias que no pudimos resolver (si las hay)

Ninguna incidencia en el código ni en la infraestructura: los 3 servicios Docker están activos, los 50.000 anuncios están importados en PostgreSQL y verificados con SQL, y los 6 tests de pytest pasan al 100%.

## Decisiones de implementación

**Criterio del prompt (cómo definimos las categorías y el caso `unknown`):** 
El prompt delimita taxativamente la evaluación al estado exterior visible de la carrocería y pintura, prohibiendo categóricamente deducciones mecánicas o de motor. Obliga a elegir entre cuatro categorías cerradas (`like new`, `excellent`, `good`, `fair`), devuelve `unknown` si la foto no permite una valoración clara (imágenes borrosas, piezas sueltas, fotos no automovilísticas) y exige una salida JSON pura sin bloques markdown.

**Decisión del HTML (atributos de formulario y envío de foto):** 
Se prescindió totalmente de JavaScript, empleando HTML estándar con Jinja2. El formulario usa `method="post"`, `action="/tasar"` y `enctype="multipart/form-data"` para la transferencia del fichero binario. Los desplegables se llenan dinámicamente con las constantes válidas del dataset. No existe selector de estado, ya que la condición proviene exclusivamente del análisis visual.

