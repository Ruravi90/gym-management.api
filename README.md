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

- Python 3.11 (Recomendado) o 3.12
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

# Mentor IA (opcional — API compatible con OpenAI: OpenAI, Groq, OpenRouter, Ollama...)
OPENAI_API_KEY=tu_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

> 💡 **Mentor IA (FitMentor):** si no configuras `OPENAI_API_KEY`, el endpoint `/mentor/chat` responde con un mensaje por defecto para que la app no se rompa. También puedes apuntar `OPENAI_BASE_URL` a Groq, OpenRouter o un Ollama local.

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

## 🏋️ Rutinas y Ejercicios

- **Catálogo de ejercicios** (`/exercises`): se siembra automáticamente al arrancar con 55 ejercicios populares que incluyen GIF de demostración e instrucciones en español (dataset público [exercises-dataset](https://github.com/hasaneyldrm/exercises-dataset), media © Gym Visual).
- **Rutinas** (`/routines`): el staff crea rutinas con días y ejercicios (series/reps/peso/descanso) y las asigna a clientes; los clientes también pueden crear las suyas.
- **Seguimiento** (`/routines/sessions` y `/sets`): el cliente inicia una sesión, registra sus series (reps, peso, completada) y la cierra con duración.
- **Medidas corporales** (`/measurements`): registro semanal de cintura, abdomen bajo, pierna y brazos (cm) con deltas automáticos vs el registro anterior.
- **Mentor IA** (`/mentor/chat` y `/mentor/weekly-checkin`): chat con contexto de la rutina, progreso y medidas; y **reporte semanal** generado con IA (medidas vs semana anterior + adherencia + recomendaciones).

## 📚 Documentación API

Una vez ejecutando el servidor, visita:

- [Swagger UI](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)

---

_GymControl — Robust & Secure_
