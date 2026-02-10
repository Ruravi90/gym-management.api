# GymControl — API Backend 🛡️

Potente API REST para la gestión de gimnasios, desarrollada con **FastAPI** y **Tortoise ORM**.

## 🚀 Características del Backend

- **🔐 Seguridad Reforzada:**
  - Bcrypt con parche de compatibilidad para contraseñas de más de 72 caracteres.
  - Validación estricta de emails con `EmailStr`.
  - Roles predefinidos y protegidos: `AdminOnly`, `ManagerOrAbove`.
  - Fail-safe de `SECRET_KEY` para entornos de producción.
- **⚙️ Automatización Inteligente:**
  - Cálculo de fechas y precios de membresías en tiempo real.
  - Soporte para biometría facial (Reconocimiento facial).
- **🗄️ Base de Datos Moderna:**
  - Integridad referencial con `ForeignKeyField` en modelos críticos.
  - Uso de Tortoise ORM para consultas rápidas y seguras.
  - Soporte de zonas horarias (`timezone-aware`) en todos los registros.
- **📝 Logging Centralizado:** Sistema de logs estructurado para depuración y auditoría.

## 🛠️ Instalación y Uso

### Pre-requisitos

- Python 3.12+
- MySQL Server

### Configuración

1. Crea un entorno virtual: `python -m venv venv`
2. Actívalo: `source venv/bin/activate` (Mac/Linux) o `venv\Scripts\activate` (Windows)
3. Instala dependencias: `pip install -r requirements.txt`

### Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```env
DATABASE_URL=mysql://root:root@localhost:3306/gymcontrol
SECRET_KEY=tu_clave_secreta_aqui
ENVIRONMENT=development
```

### Base de Datos y Migraciones (Aerich)

```bash
# Inicializar base de datos
aerich upgrade
# Crear nueva migración después de cambios en modelos
aerich migrate
aerich upgrade
```

### Ejecutar Servidor

```bash
uvicorn app.main:app --reload
```

## 📚 Documentación API

Una vez ejecutando el servidor, visita:

- [Swagger UI](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)

---

_GymControl — Robust & Secure_
