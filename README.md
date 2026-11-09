# Family Flow

Panel Django para controlar integrantes, cuotas y pagos de una cuenta familiar. Las vistas se renderizan con el motor de plantillas de Django; los datos se guardan en SQLite.

La interfaz interna utiliza Bootstrap 5 y Bootstrap Icons desde jsDelivr, por lo que se requiere conexión a internet para cargar esos recursos. El login no usa Bootstrap.

## Requisitos

- Python 3.10 o superior

## Preparar el proyecto

Desde la carpeta del proyecto, crea y activa un entorno virtual e instala las dependencias:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Inicializa la base de datos y ejecuta el servidor de desarrollo:

```powershell
python manage.py migrate
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`. Los módulos de integrantes, pagos, dashboard y reportes usan los registros almacenados en `db.sqlite3`.

La primera vez, crea el usuario administrador requerido para iniciar sesión:

```powershell
python manage.py createsuperuser
```

Inicia sesión con esa cuenta en la aplicación. Para administrar los datos desde Django Admin, visita `/admin/`.

> La aplicación registra manualmente las cuotas del grupo; no se conecta ni sincroniza con Spotify.
