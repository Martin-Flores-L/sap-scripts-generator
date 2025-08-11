# 🎯 ¿Qué hace este proyecto?

Este sistema automatiza la generación de scripts VBS para operaciones SAP MB21, eliminando el proceso manual tedioso y reduciendo errores. Los usuarios pueden cargar archivos Excel o crear datos interactivamente desde la web.

---

## ✨ Características Principales

- **🖥️ Interfaz Web Intuitiva:** Streamlit frontend con pestañas organizadas.
- **📁 Carga de Archivos Excel:** Procesa archivos existentes automáticamente.
- **✏️ Editor Interactivo:** Crea y edita datos directamente en el navegador.
- **🗜️ Descargas Flexibles:** Scripts individuales o paquete ZIP completo.
- **🛡️ Manejo Robusto de Errores:** Feedback claro para cualquier problema.
- **🔧 API RESTful:** Backend FastAPI escalable y bien documentado.

---

## 🚀 Inicio Rápido

### Prerequisitos

- Python 3.8 o superior
- [UV](https://github.com/astral-sh/uv) (gestor de paquetes ultrarrápido)

### Instalación

1. **Clona el repositorio**

   ```bash
   git clone https://github.com/Martin-Flores-L/sap-scripts-generator.git
   cd sap-scripts-generator
   ```

2. **Instala todas las dependencias con UV**

   ```bash
   uv sync --all-extras
   ```

3. **Ejecuta los servicios**

   - **Por separado**

     **Terminal 1 - Backend:**
     ```bash
     uv run uvicorn backend.main:app --reload --port 8000
     ```

     **Terminal 2 - Frontend:**
     ```bash
     uv run streamlit run frontend/streamlit_app.py
     ```

4. **Accede a la aplicación**

   - **Frontend:** [http://localhost:8501](http://localhost:8501)
   - **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💡 Casos de Uso

### Emisión de Vales de Reserva (221/201)
- Carga archivos Excel con datos de materiales
- Personaliza los datos necesarios para la generación de scripts
- Genera scripts VBS para crear vales en SAP MB21
- Soporte para movimientos 201 (entrada) y 221 (salida)

### Modificaciones de Vales (Próximamente)
- Adición, modificación y eliminación de líneas
- Finalización y devolución de vales
- Scripts para SAP MB22

### Reportes personalizados (MB25 - MB52)
- Convertidos en Excel dependiendo a la necesidad, podrás configurarlo

---

## 🔧 Tecnologías Utilizadas

- **Frontend:** Streamlit, Pandas, Requests
- **Backend:** FastAPI, Pydantic, Python-multipart
- **Procesamiento:** Pandas, OpenPyXL
- **Gestión de Dependencias:** UV - Gestor de paquetes ultrarrápido
- **Otros:** Zipfile, IO, Datetime

---

## 📁 Estructura del Proyecto

```
sap-scripts-generator/
├── frontend/                   # Aplicación Streamlit
│   └── streamlit_app.py        # Interfaz web principal
├── backend/                    # API FastAPI  
│   ├── main.py                 # Servidor API
│   ├── data_processor.py       # Procesamiento de datos
│   └── script_generators.py    # Generación de scripts VBS
├── docs/                       # Documentación
├── examples/                   # Archivos de ejemplo
├── pyproject.toml              # Configuración UV unificada
├── uv.lock                     # Lock file de dependencias
└── README.md                   # Este archivo
```

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature  
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. Commit tus cambios  
   ```bash
   git commit -m 'Agregar nueva funcionalidad'
   ```
4. Push a la rama  
   ```bash
   git push origin feature/nueva-funcionalidad
   ```
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

**Martin Flores**  
Email: martinfloreslaynes@gmail.com  
GitHub: [@Martin-Flores-L](https://github.com/Martin-Flores-L)

---

## 🙏 Reconocimientos

- Comunidad de Streamlit por la excelente documentación
- FastAPI por crear un framework tan intuitivo
- Pandas por hacer el procesamiento de datos tan simple

⭐ Si este proyecto te fue útil, ¡no olvides darle una estrella en GitHub!
