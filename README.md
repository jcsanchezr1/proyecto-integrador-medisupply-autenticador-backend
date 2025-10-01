# MediSupply Authenticator Backend

Sistema de autenticación backend para el proyecto integrador MediSupply - Versión simplificada.

## Arquitectura

Estructura básica preparada para escalar:

```
├── app/
│   ├── config/          # Configuración
│   ├── controllers/     # Controladores REST
│   │   └── health_controller.py  # Healthcheck funcional
│   ├── services/        # Lógica de negocio (estructura)
│   ├── repositories/    # Acceso a datos (estructura)
│   ├── models/          # Modelos de datos (estructura)
│   ├── exceptions/      # Excepciones (estructura)
│   └── utils/           # Utilidades (estructura)
├── tests/               # Tests (estructura)
├── app.py              # Punto de entrada
├── requirements.txt    # Mismas versiones del proyecto sample
├── Dockerfile         # Containerización
├── docker-compose.yml # Orquestación
└── README.md          # Documentación
```

## Características

- **Health Check**: Endpoint de monitoreo del servicio
- **Docker**: Containerización para local y Cloud Run
- **Flask**: Framework web minimalista
- **CORS**: Habilitado para desarrollo

## Tecnologías

- Python 3.9
- Flask 3.0.3
- Gunicorn 21.2.0
- Docker

## Instalación

### Desarrollo Local

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecutar la aplicación:
   ```bash
   python app.py
   ```

### Con Docker

1. Construir y ejecutar:
   ```bash
   docker-compose up --build
   ```

2. La aplicación estará disponible en `http://localhost:8080`

## Endpoints

### Health Check
- `GET /health` - Estado del servicio
- `GET /ping` - Ping simple

## Respuesta del Health Check

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "service": "MediSupply Authenticator Backend",
  "version": "1.0.0",
  "environment": "development"
}
```

## Cloud Run

Para desplegar en Google Cloud Run:

1. Construir imagen:
   ```bash
   docker build -t gcr.io/PROJECT_ID/medisupply-auth .
   ```

2. Subir imagen:
   ```bash
   docker push gcr.io/PROJECT_ID/medisupply-auth
   ```

3. Desplegar:
   ```bash
   gcloud run deploy medisupply-auth \
     --image gcr.io/PROJECT_ID/medisupply-auth \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## Variables de Entorno

- `FLASK_ENV`: Entorno (development/production)
- `PORT`: Puerto del servicio (default: 8080)
- `HOST`: Host del servicio (default: 0.0.0.0)
- `DEBUG`: Modo debug (default: True)

## Próximos Pasos

1. Implementar autenticación 
2. Agregar base de datos
3. Implementar endpoints de creaciòn de usuarios
4. Agregar validaciones en e proyecto 3.