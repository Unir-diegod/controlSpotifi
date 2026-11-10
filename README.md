# Family Flow

Sistema de gestión y control de aportes y cuotas familiares, desarrollado en Django con interfaz plana corporativa y arquitectura lista para producción con PostgreSQL.

---

## 🚀 Requisitos

- **Python 3.10** o superior
- **PostgreSQL 14** o superior (local o gestionado en la nube como Neon, Supabase, Railway, Render, AWS RDS, etc.)

---

## ⚙️ Configuración de Variables de Entorno (Cero datos quemados)

El proyecto no contiene contraseñas, secretos ni conexiones fijas en el código. Toda la configuración se realiza mediante variables de entorno.

Copia el archivo de ejemplo para configurar tu entorno:

```bash
cp .env.example .env
```

### Variables requeridas:

| Variable | Descripción | Ejemplo |
|---|---|---|
| `DJANGO_SECRET_KEY` | Clave criptográfica de Django (obligatoria) | `django-insecure-tu-clave-super-secreta` |
| `DJANGO_DEBUG` | `True` para desarrollo local, `False` para producción | `False` |
| `ALLOWED_HOSTS` | Dominios permitidos separados por comas | `miapp.com,www.miapp.com` |
| `DATABASE_URL` | Cadena de conexión a PostgreSQL (opción recomendada) | `postgresql://usuario:password@host:5432/nombre_db` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes permitidos para peticiones POST HTTPS | `https://miapp.com,https://www.miapp.com` |

> Alternativamente a `DATABASE_URL`, puedes usar variables individuales: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

---

## 📦 Puesta en Marcha Local

1. **Activa el entorno virtual e instala las dependencias**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Aplica las migraciones en PostgreSQL**:
   ```powershell
   python manage.py migrate
   ```

3. **Crea el usuario administrador**:
   ```powershell
   python manage.py createsuperuser
   ```

4. **Inicia el servidor**:
   ```powershell
   python manage.py runserver
   ```

---

## 🌐 Despliegue en Producción (Railway / Render / Fly.io / VPS)

El proyecto incluye:
- **WhiteNoise** preconfigurado para servir archivos estáticos (`collectstatic`) con compresión y caché de alto rendimiento.
- **Gunicorn** como servidor WSGI listo para recibir tráfico de producción.
- **Protección HTTPS**: Redirección SSL automática, cookies seguras (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`) y cabeceras HSTS activas cuando `DJANGO_DEBUG=False`.

### Comando de inicio en producción (Procfile / Start Command):
```bash
gunicorn familyflow.wsgi:application
```

### Comando de compilación (Build Command):
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```
