import pandas as pd
from io import BytesIO

class DataProcessor:
    """
    Handles all data extraction and manipulation from Excel files.
    """
    #221
    def _clean_dataframe_generic(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica limpieza genérica de strings a las columnas requeridas."""
        df = df.copy()
        str_cols = ['Codigo Almacen', 'Codigo Material', 'Cantidad', 'ELEMENTO PEP']
        for col in str_cols:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        if 'Codigo Almacen' in df.columns:
            df['Codigo Almacen'] = df['Codigo Almacen'].apply(lambda x: x.zfill(4))
        
        return df
    
    #221
    def _clean_dataframe_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convierte columnas a tipos numéricos, manejando errores."""
        df = df.copy()
        
        # Columnas a convertir a numérico (entero)
        numeric_cols = ['VR', 'Cantidad', 'Codigo Material', 'Codigo Almacen', 'POS']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        # Manejo especial para ELEMENTO PEP que puede ser numérico o string
        if 'ELEMENTO PEP' in df.columns:
            pep_series = df['ELEMENTO PEP'].astype(str)
            # Deja como string los que no son puramente dígitos.
            df['ELEMENTO PEP'] = pep_series 
            
        return df
    
    #221
    def _load_and_filter_data(self, file_stream: BytesIO, sheet_name: str, headers: list, filter_column_index: int) -> pd.DataFrame:
        """Carga datos de un stream de archivo, los filtra y limpia."""
        # The sheet_name and headers are expected to be consistent with the Excel file structure.
        df = pd.read_excel(file_stream, sheet_name=sheet_name, header=None, names=headers, skiprows=1)
        
        df['Tipo Solicitud'] = df['Tipo Solicitud'].str.title()
        
        # Filtra por estado 'PENDIENTE'
        df_filtered = df[df.iloc[:, filter_column_index] == "PENDIENTE"].copy()
        
        # Limpieza y conversión de tipos
        df_cleaned_numeric = self._clean_dataframe_numeric(df_filtered)
        df_final = self._clean_dataframe_generic(df_cleaned_numeric)
        
        return df_final

    #221
    def process_emisiones_file(self, file_stream: BytesIO) -> pd.DataFrame:
        # Establece los headers esperados para el archivo de Emisiones
        """Procesa el archivo de Emisiones."""
        # headers = ['PO','EECC','Localidad','PROYECTO','Tipo Solicitud','Codigo Material','Descripcion','Cantidad','Codigo Almacen','ELEMENTO PEP','IP','VR','SOLICITUD','Codigo destino mercancías','Gestor','Numero de registro','ESTADO']
        headers = ['PO','EECC','Localidad','MOV_SAP','Tipo Solicitud','Codigo Material','Descripcion','Cantidad','Codigo Almacen','ELEMENTO PEP','IP','VR','SOLICITUD','Codigo destino mercancías','Gestor','Numero de registro','ESTADO']
        return self._load_and_filter_data(file_stream, "Sheet1", headers, 16)
    
    
    def process_solicitudes_file(self, file_stream: BytesIO) -> pd.DataFrame:
        """Procesa el archivo de Solicitudes."""
        # headers = ['SVR','PO','IP','EECC','PROYECTO','POS','Codigo Material','Descripcion','Cantidad','TIPO SOLICITUD REAL','Tipo Solicitud','VR','VD','Codigo Almacen','ELEMENTO PEP','Observacion','Codigo destino mercancías','ESTADO','FECHA DE ATENCION','GESTOR','N°']
        headers = ['SVR','PO','IP','EECC','MOV_SAP','POS','Codigo Material','Descripcion','Cantidad','TIPO SOLICITUD REAL','Tipo Solicitud','VR','VD','Codigo Almacen','ELEMENTO PEP','Observacion','Codigo destino mercancías','ESTADO','FECHA DE ATENCION','GESTOR','N°']
        
        # Carga y filtro inicial
        df_gsheet = pd.read_excel(file_stream, sheet_name="DETALLE", header=None, names=headers, skiprows=1)
        df_gsheet['Tipo Solicitud'] = df_gsheet['Tipo Solicitud'].str.title()
        df_filtered = df_gsheet[df_gsheet['ESTADO'] == "PENDIENTE"].copy()

        # Limpieza
        df_cleaned_numeric = self._clean_dataframe_numeric(df_filtered)
        df_final = self._clean_dataframe_generic(df_cleaned_numeric)
        
        return df_final


    def split_by_operation(self, df: pd.DataFrame) -> dict:
        """Divide el DataFrame en un diccionario de DataFrames por Tipo de Solicitud."""
        operations = {
            'Devolucion': df[df['Tipo Solicitud'] == 'Devolucion'],
            'Adicionar': df[df['Tipo Solicitud'] == 'Adicionar'],
            'Modificar': df[df['Tipo Solicitud'] == 'Modificar'],
            'Sfin': df[df['Tipo Solicitud'] == 'Sfin'],
            'Borrar': df[df['Tipo Solicitud'] == 'Borrar']
        }
        return operations

    #If users want to split by project type, use this method
    def split_by_project_type(self, df: pd.DataFrame) -> dict:
        """Divide el DataFrame para proyectos 201 y 221."""
        proyectos_201 = ['EDIFICIOS - BROWNFIELD', 'MERMAS 2025', 'DIFERENCIAS 2025', 'VENTAS']
        df_201 = df[df['PROYECTO'].isin(proyectos_201)]
        df_221 = df[~df['PROYECTO'].isin(proyectos_201)]
        return {'201': df_201, '221': df_221}
    
    #If users want to split by movement type, use this method
    def split_by_movement_type(self, df: pd.DataFrame) -> dict:
        """Divide el DataFrame para proyectos 201 y 221."""
        
        df_201 = df[df['MOV_SAP'] == 201]
        df_221 = df[df['MOV_SAP'] == 221]

        return {'201': df_201, '221': df_221}
