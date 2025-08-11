🎯 ¿Qué hace este proyecto?
Este sistema automatiza la generación de scripts VBS para operaciones SAP mb21, eliminando el proceso manual tedioso y reduciendo errores. Los usuarios pueden cargar archivos Excel o crear datos interactivamente para generar scripts listos para usar en SAP.
✨ Características Principales

🖥️ Interfaz Web Intuitiva - Streamlit frontend con pestañas organizadas
📁 Carga de Archivos Excel - Procesa archivos existentes automáticamente
✏️ Editor Interactivo - Crea y edita datos directamente en el navegador
🗜️ Descargas Flexibles - Scripts individuales o paquete ZIP completo
🛡️ Manejo Robusto de Errores - Feedback claro para cualquier problema
🔧 API RESTful - Backend FastAPI escalable y bien documentado

🚀 Inicio Rápido
Prerequisitos

Python 3.8 o superior
UV (gestor de paquetes ultrarrápido)

Instalación

Clona el repositorio

bashgit clone https://github.com/tu-usuario/sap-scripts-generator.git
cd sap-scripts-generator

Instala todas las dependencias con UV

bash
uv sync --all-extras

Ejecuta los servicios

Por separado
bash# Terminal 1 - Backend
uv run uvicorn backend.main:app --reload --port 8000

bash# Terminal 2 - Frontend  
uv run streamlit run frontend/streamlit_app.py

Accede a la aplicación


Frontend: http://localhost:8501
API Docs: http://localhost:8000/docs


💡 Casos de Uso
Emisión de Vales de Reserva (221/201)

Carga archivos Excel con datos de materiales
Personaliza los datos necesarios para la generación de scripts
Genera scripts VBS para crear vales en SAP MB21
Soporte para movimientos 201 (entrada) y 221 (salida)

Modificaciones de Vales (Próximamente)

Adición, modificación y eliminación de líneas
Finalización y devolución de vales
Scripts para SAP MB22

Reportes personalizados (MB25 - MB52)
convertidos en excel dependiendo a la necesidad podras configurarlo

🔧 Tecnologías Utilizadas

Frontend: Streamlit, Pandas, Requests
Backend: FastAPI, Pydantic, Python-multipart
Procesamiento: Pandas, OpenPyXL
Gestión de Dependencias: UV - Gestor de paquetes ultrarrápido
Otros: Zipfile, IO, Datetime

📁 Estructura del Proyecto
sap-scripts-generator/
├── frontend/                   # Aplicación Streamlit
│   └── streamlit_app.py       # Interfaz web principal
├── backend/                    # API FastAPI  
│   ├── main.py               # Servidor API
│   ├── data_processor.py     # Procesamiento de datos
│   └── script_generators.py  # Generación de scripts VBS
├── docs/                      # Documentación
├── examples/                  # Archivos de ejemplo
├── pyproject.toml            # Configuración UV unificada
├── uv.lock                   # Lock file de dependencias
└── README.md                 # Este archivo

🤝 Contribuciones
Las contribuciones son bienvenidas! Por favor:

Haz fork del proyecto
Crea una rama para tu feature (git checkout -b feature/nueva-funcionalidad)
Commit tus cambios (git commit -m 'Agregar nueva funcionalidad')
Push a la rama (git push origin feature/nueva-funcionalidad)
Abre un Pull Request

📝 Licencia
Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

👤 Autor
Martin Flores - martinfloreslaynes@gmail.com

GitHub: @Martin-Flores-L
🙏 Reconocimientos
Comunidad de Streamlit por la excelente documentación
FastAPI por crear un framework tan intuitivo
Pandas por hacer el procesamiento de datos tan simple
⭐ Si este proyecto te fue útil, ¡no olvides darle una estrella en GitHub!

