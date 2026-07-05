# Task & Calc

Aplicación web sencilla para proyecto universitario de **DevOps**: CI/CD y
**variabilidad del software** mediante feature flags.

## Stack

- **Backend:** Python + Django (arquitectura MVT)
- **Base de datos:** PostgreSQL (Supabase) vía `dj-database-url`, con fallback a SQLite en desarrollo
- **Frontend:** HTML + CSS + JavaScript puro (sin frameworks), responsive para móvil
- **Iconos:** Lucide Icons
- **Producción:** gunicorn + WhiteNoise

## Módulos

1. **Tablero de Tareas (Kanban)** — CRUD de tareas con tres columnas:
   Pendiente, En curso y Finalizada. Las tarjetas se arrastran entre columnas
   (mouse o táctil) y el orden dentro de la columna define la prioridad:
   la primera es la más importante.
2. **Calculadora Técnica** — depreciación por Línea Recta:
   `(Valor Inicial − Valor Salvamento) / Vida Útil`, con tabla año por año
   y una interfaz tipo calculadora (pantalla LCD y teclas C / =).

## Variabilidad (Feature Flags)

La versión visible se controla con la variable de entorno `FEATURE_CALCULATOR`:

| Versión | Variable | Resultado |
|---------|----------|-----------|
| **v1** | `FEATURE_CALCULATOR=False` | Solo Sistema de Tareas (la calculadora responde 404) |
| **v2** | `FEATURE_CALCULATOR=True` | Tareas + Calculadora Técnica en el menú |

No requiere cambios de código: basta cambiar la variable y reiniciar el proceso.

## Ejecución local

```bash
python -m venv venv
venv\Scripts\activate          # Windows (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt

copy .env.example .env         # editar valores si hace falta
python manage.py migrate
python manage.py runserver
```

Abrir <http://127.0.0.1:8000>. Para alternar versiones, editar
`FEATURE_CALCULATOR` en `.env` y reiniciar el servidor.

## Despliegue (Render / Railway / similar)

Variables de entorno requeridas:

- `SECRET_KEY` — clave secreta fuerte
- `DEBUG=False`
- `ALLOWED_HOSTS=mi-dominio.com`
- `CSRF_TRUSTED_ORIGINS=https://mi-dominio.com`
- `DATABASE_URL=postgresql://...` (cadena de conexión de Supabase)
- `FEATURE_CALCULATOR=True|False` (según la versión a desplegar)

Comandos en Render:

- **Build Command:** `./build.sh` (instala dependencias, collectstatic y migrate)
- **Start Command:** `gunicorn taskcalc.wsgi:application`
  (si se deja el comando por defecto `gunicorn app:app`, también funciona
  gracias al alias `app.py`)

La versión de Python se fija con el archivo `.python-version` (3.13.5).
