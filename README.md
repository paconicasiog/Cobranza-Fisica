# Cobranza Física Automática

## Visión General
Este proyecto es una herramienta automatizada diseñada para agilizar el proceso de cobranza física y extrajudicial (Notificaciones Extrajudiciales) para mecánicas con pagos atrasados o morosidad.

El pipeline cruza la información de los clientes desde un archivo CSV con las bases de datos (Redshift y Postgres) para identificar a los clientes morosos, genera de manera automática los documentos PDF de notificación de cobranza y, finalmente, crea carpetas organizadas por cliente en Google Drive donde sube cada documento generado.

## Estructura del Proyecto

```text
Cobranza-Fisica/
├── main.py                     # Script principal orquestador
├── app/                        # Módulos del sistema
│   ├── db.py                   # Conexiones y consultas a Redshift y Postgres
│   ├── pdf_generator.py        # Lógica de generación del PDF
│   ├── drive_integration.py    # Integración con Google Drive API
│   └── utils.py                # Utilidades generales
├── credentials/                # Credenciales de acceso (Bases de datos, Google API)
├── images/                     # Imágenes y logos para los PDFs
├── base_oficinas.csv           # Lista base (CSV) de UID de las oficinas a analizar
├── Seguimento_Cobranza_Offline.csv # Log de seguimiento de cobranza con links de Drive
└── requirements.txt            # Dependencias del proyecto
```

## ¿Cómo Funciona?
1. **Lectura Base:** `main.py` lee los `UID` desde `base_oficinas.csv`.
2. **Consulta a BD:** Se conecta a Redshift para verificar la deuda actual (`get_overdue_mechanics`) y a Postgres para obtener los detalles específicos de cada factura atrasada (`get_mechanic_details`).
3. **Generación del Documento:** Usa los datos obtenidos para construir un PDF de "Notificación Extrajudicial" personalizado.
4. **Respaldo en la Nube:** Mediante la API de Google Drive, crea una carpeta específica para el cliente y sube el PDF generado.
5. **Log de Seguimiento:** Registra el proceso en un nuevo archivo `Seguimento_Cobranza_Offline.csv` que incluye los enlaces directos a Google Drive para control.

## ¿Cómo Usarlo? (Base para futuros proyectos)
Este código es excelente como plantilla para cualquier proyecto que requiera generación automática de PDFs y su sincronización directa con carpetas en Google Drive.

### Requisitos Previos:
- Python 3.x
- Dependencias incluidas en `requirements.txt` (instalar con `pip install -r requirements.txt`).
- Archivos de credenciales válidos dentro de la carpeta `credentials/` para el acceso a las bases de datos y la API de Google Drive.

### Ejecución:
Simplemente ejecuta el script principal:
```bash
python3 main.py
```

### Configuración:
- **Directorio de Google Drive:** Para cambiar la ubicación principal donde se crearán las carpetas, actualiza la variable `ROOT_DRIVE_FOLDER_ID` dentro de `main.py`.
- **Base de clientes:** Modifica `base_oficinas.csv` con los UIDs actualizados que se deseen evaluar.
