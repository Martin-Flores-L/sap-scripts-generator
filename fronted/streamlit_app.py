import streamlit as st
import requests
import pandas as pd
from datetime import date
import random
import io
import zipfile
from typing import Dict, Optional, Tuple


# ========================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ========================================

st.set_page_config(
    page_title="Generador de Scripts SAP", 
    page_icon="📊", 
    layout="wide"
)

# ========================================
# FUNCIONES AUXILIARES
# ========================================

def create_vbs_from_json_data(data: dict) -> Optional[Dict[str, str]]:
    """
    Recibe un diccionario JSON, extrae el contenido del VBScript
    y lo retorna como diccionario con los scripts encontrados.

    Args:
        data (dict): Diccionario con las claves de scripts desde FastAPI

    Returns:
        dict: Diccionario con los scripts encontrados {tipo: contenido}
        None: Si no se encuentra ningún script válido
    """
    try:
        script_content = {}

        # Verificar scripts 221 y 201 (valores directos)
        if 'script_221' in data and len(data['script_221']) > 0:
            script_content['221'] = data['script_221']
            
        if 'script_201' in data and len(data['script_201']) > 0:
            script_content['201'] = data['script_201']

        # Verificar otros scripts (listas - tomar primer elemento)
        script_list_keys = {
            'script_222': '222',
            'script_202': '202', 
            'script_add': 'add',
            'script_mod': 'mod',
            'script_del': 'del',
            'script_sfin': 'sfin'
        }

        for json_key, script_key in script_list_keys.items():
            if json_key in data and len(data[json_key]) > 0:
                script_content[script_key] = data[json_key][0]

        if not script_content:
            st.warning("⚠️ No se encontraron scripts válidos en la respuesta del servidor.")
            return None

        st.success(f"✅ Scripts encontrados: {', '.join(script_content.keys())}")
        return script_content

    except Exception as e:
        st.error(f"❌ Error procesando el JSON: {e}")
        return None


def send_to_backend(files_data: dict, user_data: dict) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Envía datos al backend FastAPI y maneja la respuesta.

    Args:
        files_data (dict): Archivos para enviar
        user_data (dict): Datos del usuario (sap_user, file_output)

    Returns:
        tuple: (success: bool, json_response: dict, error_message: str)
    """
    try:
        with st.spinner("🔄 Enviando datos al servidor..."):
            response = requests.post(
                "http://127.0.0.1:8000/emisiones/",
                data=user_data,
                files=files_data,
                timeout=30  # Timeout de 30 segundos
            )
            
        if response.status_code == 200:
            return True, response.json(), None
        else:
            error_msg = f"Error {response.status_code}: {response.text}"
            return False, None, error_msg
            
    except requests.exceptions.Timeout:
        return False, None, "⏱️ Tiempo de espera agotado. El servidor tardó demasiado en responder."
    except requests.exceptions.ConnectionError:
        return False, None, "🔌 No se pudo conectar con el servidor. Verifica que esté ejecutándose."
    except Exception as e:
        return False, None, f"❌ Error inesperado: {str(e)}"


def create_zip_download(vbs_scripts: Dict[str, str], filename: str = "SAP_SCRIPTS.zip") -> bytes:
    """
    Crea un archivo ZIP en memoria con los scripts VBS.

    Args:
        vbs_scripts (dict): Diccionario con scripts {tipo: contenido}
        filename (str): Nombre del archivo ZIP

    Returns:
        bytes: Contenido del archivo ZIP
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for script_type, content in vbs_scripts.items():
            zip_file.writestr(f"script_{script_type}.vbs", content)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def process_and_download_scripts(json_data: dict) -> None:
    """
    Procesa la respuesta JSON y genera los botones de descarga.

    Args:
        json_data (dict): Respuesta JSON del backend
    """
    vbs_scripts = create_vbs_from_json_data(json_data)
    
    if vbs_scripts:
        # Crear columnas para los botones de descarga
        cols = st.columns([2, 2, 2])
        
        with cols[0]:
            # Descarga individual de scripts
            st.subheader("📄 Descargas Individuales")
            for script_type, content in vbs_scripts.items():
                st.download_button(
                    label=f"Descargar Script {script_type.upper()}",
                    data=content.encode('utf-8'),
                    file_name=f"script_{script_type}.vbs",
                    mime="text/plain",
                    use_container_width=True,
                    key=f"download_{script_type}"
                )
        
        with cols[1]:
            st.subheader("🗜️ Descarga Combinada")
            # Descarga ZIP con todos los scripts
            zip_content = create_zip_download(vbs_scripts)
            st.download_button(
                label="Descargar Todos (ZIP)",
                data=zip_content,
                file_name="SAP_SCRIPTS.zip",
                mime="application/zip",
                use_container_width=True
            )
        
        with cols[2]:
            st.subheader("📊 Información")
            st.info(f"Total de scripts: {len(vbs_scripts)}")
            st.text("Scripts generados:")
            for script_type in vbs_scripts.keys():
                st.text(f"• {script_type.upper()}")
    else:
        st.warning("⚠️ No se generó ningún script desde los datos proporcionados.")


def create_interactive_dataframe(num_rows: int, mov_sap: str) -> pd.DataFrame:
    """
    Crea un DataFrame interactivo con datos por defecto para el modo manual.

    Args:
        num_rows (int): Número de filas a crear
        mov_sap (str): Tipo de movimiento SAP (201 o 221)

    Returns:
        pd.DataFrame: DataFrame con datos por defecto
    """
    hoy = date.today().strftime("%Y-%m-%d")
    
    df = pd.DataFrame({
        "PO": ["PO_TEST"] * num_rows,
        "EECC": ["EECC_TEST"] * num_rows,
        "Localidad": ["LOCALIDAD_TEST"] * num_rows,
        "Movimiento_SAP": [mov_sap] * num_rows,
        "Tipo Solicitud": ["Emision"] * num_rows,
        "Codigo Material": [str(random.randint(1004731546, 1004732000)) for _ in range(num_rows)],
        "Descripcion": [f"Material_{i+1}" for i in range(num_rows)],
        "Cantidad": [str(random.randint(1, 100)) for _ in range(num_rows)],
        "Codigo Almacen": ["0002"] * num_rows,
        "Elemento PEP": ["P-00005-0002-0001"] * num_rows,
        "IP": ["IP_TEST"] * num_rows,
        "VR": [""] * num_rows,
        "Solicitud": [hoy] * num_rows,
        "Codigo destino mercancías": ["YP00118"] * num_rows,  # Usuario por defecto
        "Gestor": ["GESTOR_TEST"] * num_rows,
        "Numero de registro": [1] * num_rows,
        "Estado": ["PENDIENTE"] * num_rows
    })
    
    return df


def dataframe_to_excel_buffer(df: pd.DataFrame, filename: str = "datos_interactivos.xlsx") -> io.BytesIO:
    """
    Convierte un DataFrame a un buffer de Excel en memoria.

    Args:
        df (pd.DataFrame): DataFrame a convertir
        filename (str): Nombre del archivo

    Returns:
        io.BytesIO: Buffer con el archivo Excel
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output


# ========================================
# FUNCIONES DE INTERFAZ
# ========================================

def render_user_config_sidebar():
    """Renderiza la configuración de usuario en la sidebar."""
    with st.sidebar:
        st.header("⚙️ Configuración de Usuario")
        
        sap_user = st.text_input(
            "Usuario SAP", 
            value="YP00118",
            help="Usuario que se utilizará en los scripts SAP"
        )
        
        save_dir = st.text_input(
            "Ruta de guardado", 
            value=r"C:\Scripts",
            help="Directorio donde se guardarán los archivos VBS"
        )
        
        st.info("💡 Asegúrate de que el servidor FastAPI esté ejecutándose en http://127.0.0.1:8000")
        
        return sap_user, save_dir


def render_excel_upload_tab(sap_user: str, save_dir: str):
    """
    Renderiza la pestaña de carga de archivos Excel.
    
    Args:
        sap_user (str): Usuario SAP configurado
        save_dir (str): Directorio de guardado configurado
    """
    st.subheader("📁 Subir Archivo Excel")
    st.info("Sube un archivo Excel con los datos de emisiones para generar los scripts SAP automáticamente.")
    
    upload_file = st.file_uploader(
        "Selecciona el archivo Excel de Emisiones", 
        type=["xlsx"],
        help="El archivo debe contener las columnas necesarias para generar los vales SAP"
    )
    
    if upload_file is not None:
        # Mostrar información del archivo
        st.success(f"✅ Archivo cargado: {upload_file.name}")
        st.text(f"Tamaño: {upload_file.size / 1024:.2f} KB")
        
        # Botón para procesar
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Generar Scripts desde Excel", use_container_width=True, type="primary"):
                # Preparar datos para enviar
                files_data = {
                    "file": (upload_file.name, upload_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                }
                user_data = {
                    "sap_user": sap_user,
                    "file_output": save_dir
                }
                
                # Enviar al backend
                success, json_data, error = send_to_backend(files_data, user_data)
                
                if success:
                    st.success("✅ Archivo procesado exitosamente!")
                    process_and_download_scripts(json_data)
                else:
                    st.error(error)


def render_interactive_tab(sap_user: str, save_dir: str):
    """
    Renderiza la pestaña de modo interactivo.
    
    Args:
        sap_user (str): Usuario SAP configurado
        save_dir (str): Directorio de guardado configurado
    """
    st.subheader("✏️ Modo Interactivo")
    st.info("Crea y edita los datos directamente en la interfaz para generar scripts personalizados.")
    
    # Configuración inicial
    col1, col2 = st.columns(2)
    
    with col1:
        mov_sap = st.selectbox(
            "Tipo de Movimiento SAP",
            options=["201", "221"],
            help="Selecciona el tipo de movimiento para los vales SAP"
        )
    
    with col2:
        num_rows = st.number_input(
            "Cantidad de materiales", 
            min_value=1, 
            max_value=50, 
            value=1, 
            step=1,
            help="Número de líneas de materiales a procesar"
        )
    
    # Inicializar DataFrame en session_state si no existe
    if "interactive_df" not in st.session_state:
        st.session_state.interactive_df = None
    
    # Botón para crear/recrear tabla
    if st.button("🔄 Crear/Actualizar Tabla", use_container_width=True):
        st.session_state.interactive_df = create_interactive_dataframe(num_rows, mov_sap)
        st.success(f"✅ Tabla creada con {num_rows} filas")
    
    # Editor de datos si existe el DataFrame
    if st.session_state.interactive_df is not None:
        st.subheader("📊 Editor de Datos")
        
        # Columnas editables
        editable_columns = [
            "Movimiento_SAP",
            "Codigo Material",
            "Descripcion", 
            "Cantidad",
            "Codigo Almacen",
            "Elemento PEP"
        ]
        
        st.info(f"💡 Puedes editar las siguientes columnas: {', '.join(editable_columns)}")
        
        # Editor de datos
        df_editable = st.session_state.interactive_df[editable_columns]
        df_edited = st.data_editor(
            df_editable, 
            num_rows="dynamic",
            use_container_width=True,
            key="data_editor"
        )
        
        # Actualizar el DataFrame completo con los cambios
        for col in editable_columns:
            st.session_state.interactive_df[col] = df_edited[col]
        
        st.subheader("🚀 Generar Scripts")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📋 Vista Previa de Datos", use_container_width=True):
                with st.expander("👁️ Ver datos completos", expanded=True):
                    st.dataframe(st.session_state.interactive_df, use_container_width=True)
        
        with col2:
            if st.button("🚀 Enviar al Servidor", use_container_width=True, type="primary"):
                # Convertir DataFrame a Excel en memoria
                excel_buffer = dataframe_to_excel_buffer(st.session_state.interactive_df)
                
                # Preparar datos para envío
                files_data = {
                    "file": ("datos_interactivos.xlsx", excel_buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                }
                user_data = {
                    "sap_user": sap_user,
                    "file_output": save_dir
                }
                
                # Enviar al backend
                success, json_data, error = send_to_backend(files_data, user_data)
                
                if success:
                    st.success("✅ Datos procesados exitosamente!")
                    process_and_download_scripts(json_data)
                else:
                    st.error(error)


# ========================================
# APLICACIÓN PRINCIPAL
# ========================================

def main():
    """Función principal de la aplicación Streamlit."""
    
    # Título principal
    st.title("📊 Generador de Scripts SAP")
    st.markdown("---")
    
    # Configuración de usuario en sidebar
    sap_user, save_dir = render_user_config_sidebar()
    
    # Selector de modo principal
    mode_initial = st.radio(
        "🔧 Selecciona la funcionalidad",
        [
            "Emisión Vales de Reserva - 221 / 201",
            "Modificaciones de Vales de Reserva - Add/Mod/Del/SFin/Dev"
        ],
        help="Selecciona el tipo de operación que deseas realizar"
    )
    
    if mode_initial == "Emisión Vales de Reserva - 221 / 201":
        st.header("📝 Emisión de Vales de Reserva SAP - 221 / 201")
        
        # Pestañas para diferentes modos
        tab1, tab2 = st.tabs(["📁 Subir Excel", "✏️ Modo Interactivo"])
        
        with tab1:
            render_excel_upload_tab(sap_user, save_dir)
        
        with tab2:
            render_interactive_tab(sap_user, save_dir)
    
    elif mode_initial == "Modificaciones de Vales de Reserva - Add/Mod/Del/SFin/Dev":
        st.header("🔧 Modificaciones de Vales SAP MB22")
        
        # Placeholder para funcionalidad futura
        st.info("🚧 Esta funcionalidad está en desarrollo.")
        st.markdown("""
        **Funcionalidades planeadas:**
        - ✅ Adición de líneas (Add)
        - ✅ Modificación de líneas (Mod)  
        - ✅ Eliminación de líneas (Del)
        - ✅ Finalización de vales (SFin)
        - ✅ Devolución de materiales (Dev)
        """)
        
        st.warning("⏱️ Por favor, vuelve más tarde para usar estas funcionalidades.")


# ========================================
# EJECUCIÓN DE LA APLICACIÓN
# ========================================

if __name__ == "__main__":
    main()