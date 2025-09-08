# 🚀 FastAPI Fingerprint API

Una API REST moderna construida con FastAPI para capturar y gestionar huellas dactilares usando dispositivos ZKTeco con integración SQLAlchemy.

## 📋 Características

- ✅ **Captura de huellas dactilares** en tiempo real
- ✅ **Almacenamiento persistente** con SQLAlchemy + SQLite
- ✅ **Identificación de huellas** (comparación 1:N)
- ✅ **Control de luces** del dispositivo
- ✅ **API REST completa** con documentación automática
- ✅ **Modo demo** para pruebas sin dispositivo físico
- ✅ **Logging completo** y manejo de errores
- ✅ **Migraciones de base de datos** con Alembic

## 🏗️ Estructura del Proyecto

```
fastApi-huella/
├── app/                          # Aplicación principal
│   ├── __init__.py              # Inicializador del paquete
│   ├── main.py                  # Servidor completo con ZKTeco
│   ├── main_demo.py             # Servidor demo (sin dispositivo)
│   ├── models.py                # Modelos SQLAlchemy
│   ├── database_service.py      # Servicios de base de datos
│   └── fingerprint_service.py   # Servicio de huellas ZKTeco
├── alembic/                     # Migraciones de base de datos
│   ├── versions/                # Archivos de migración
│   └── env.py                   # Configuración Alembic
├── dll/                         # Archivos DLL del SDK ZKTeco
├── venv/                        # Entorno virtual Python
├── requirements.txt             # Dependencias del proyecto
├── pyproject.toml              # Configuración Poetry
├── alembic.ini                 # Configuración Alembic
├── test_demo.py                # Script de pruebas
└── README.md                   # Este archivo
```

## 🚀 Instalación y Configuración

### 1. Prerrequisitos

- **Python 3.8+**
- **SDK ZKTeco** (para uso con dispositivo físico)
- **Git** (opcional)

### 2. Clonar/Descargar el Proyecto

```bash
# Si tienes Git
git clone <tu-repositorio>
cd fastApi-huella

# O simplemente descarga y extrae el proyecto
```

### 3. Configurar Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 4. Instalar Dependencias

```bash
# Instalar dependencias
pip install -r requirements.txt

# O con Poetry (opcional)
pip install poetry
poetry install
```

### 5. Configurar Base de Datos

```bash
# Crear migración inicial
alembic revision --autogenerate -m "Initial migration"

# Aplicar migraciones
alembic upgrade head
```

### 6. Configurar SDK ZKTeco (Opcional)

```bash
# Crear carpeta para DLL
mkdir dll

# Copiar libzkfpcsharp.dll del SDK ZKTeco a la carpeta dll/
# Puedes descargar el SDK desde: https://www.zkteco.com/
```

## 🎯 Uso del Proyecto

### Modo Demo (Sin Dispositivo)

Perfecto para pruebas y desarrollo:

```bash
# Activar entorno virtual
venv\Scripts\activate

# Ejecutar servidor demo
python -m app.main_demo

# El servidor estará disponible en: http://localhost:8000
```

### Modo Completo (Con Dispositivo ZKTeco)

Para uso con dispositivo físico:

```bash
# Activar entorno virtual
venv\Scripts\activate

# Asegúrate de tener libzkfpcsharp.dll en la carpeta dll/
# Ejecutar servidor completo
python -m app.main

# El servidor estará disponible en: http://localhost:8000
```

## 📚 API Endpoints

### Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Información básica de la API |
| `GET` | `/health` | Estado de salud del sistema |
| `GET` | `/device/status` | Estado del dispositivo de huellas |
| `GET` | `/fingerprint/capture` | **Capturar huella + imagen + info** |
| `GET` | `/fingerprint/latest` | Última huella capturada |
| `GET` | `/fingerprint/history` | Historial de capturas |
| `GET` | `/fingerprint/stats` | Estadísticas de la base de datos |
| `POST` | `/fingerprint/light/{color}` | Control de luces |

### Endpoint Principal: Captura de Huella

**`GET /fingerprint/capture`**

Devuelve:
```json
{
  "id": 1,
  "fingerprint_id": 5,
  "score": 85,
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "template_data": "base64_template_data...",
  "timestamp": "2024-01-15T10:30:00",
  "device_serial": "ABC123456",
  "image_width": 256,
  "image_height": 288
}
```

## 🧪 Pruebas

### Pruebas Manuales

1. **Documentación Interactiva:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

2. **Prueba con cURL:**
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Capturar huella
   curl http://localhost:8000/fingerprint/capture
   
   # Control de luz
   curl -X POST "http://localhost:8000/fingerprint/light/green?duration=1.0"
   ```

## 🗄️ Base de Datos

### Modelos SQLAlchemy

- **`fingerprints`** - Datos de captura (imagen, template, timestamp)
- **`device_info`** - Información del dispositivo
- **`fingerprint_templates`** - Templates registrados

### Comandos de Base de Datos

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1

# Ver historial de migraciones
alembic history
```

## 🔧 Configuración Avanzada

### Variables de Entorno

Crea un archivo `.env` basado en `env.example`:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///./fingerprints.db
DATABASE_PATH=fingerprints.db

# Device Configuration
DEVICE_INDEX=0
DEVICE_TIMEOUT=30

# Image Configuration
IMAGE_FORMAT=PNG
IMAGE_QUALITY=95

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs.log

# API Configuration
API_TITLE=Fingerprint API
API_DESCRIPTION=API for fingerprint capture and management using ZKTeco devices
API_VERSION=1.0.0
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

Importante revisar: https://github.com/aqasemi/pyzkfp