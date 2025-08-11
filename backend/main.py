import fastapi
from fastapi import File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
from io import BytesIO

# Importa las clases de los otros archivos
from data_processor import DataProcessor
from script_generators import MB21, MB22

app = fastapi.FastAPI(
    title="SAP Script Automation API",
    description="API para generar scripts VBS para automatización de SAP.",
    version="1.0.0"
)

@app.get("/", tags=["General"])
def read_root():
    return {"message": "Bienvenido al API de Automatización de Scripts de SAP"}

@app.post("/emisiones/", tags=["Generación de Scripts"])
async def create_emisiones_script(
    sap_user: str = Form(...),
    file_output: str = Form(...),  # Ruta de guardado del archivo VBS
    file: Optional[UploadFile] = File(None)
):
    """
    Sube un archivo Excel de Emisiones y genera un script VBS para el movimiento 221.
    """
    # VB - Corrigio la lectura del nombre del archivo y solo reconoce que se suba un archivo .xlsx
    if file:
        if not file.filename.endswith('.xlsx'):
            raise HTTPException(status_code=400, detail="Formato de archivo inválido. Por favor, suba un archivo .xlsx")
        
        try:
            # Lee el contenido del archivo subido
            content = await file.read() 
            # Crea un stream de bytes para procesar el archivo
            file_stream = BytesIO(content)
            # Procesa el archivo para extraer los datos necesarios
            processor = DataProcessor()
            df = processor.process_emisiones_file(file_stream)
            
            if df.empty:
                return JSONResponse(status_code=200, content={"message": "No se encontraron solicitudes pendientes en el archivo.", "script": ""})
            
            # Dividir el dataframe por tipo de proyecto (221 o 201)
            # project_dfs = processor.split_by_project_type(df)
            project_dfs = processor.split_by_movement_type(df)
            
            print(project_dfs.keys())  # Verifica las claves disponibles
            print(f"221 DataFrame shape: {project_dfs['221'].shape}")
            print(f"201 DataFrame shape: {project_dfs['201'].shape}")
            df['MOV_SAP'] = df['MOV_SAP'].astype(str)  # Asegura que MOV_SAP sea de tipo str
            

            # Generar script para 221
            generator_221 = MB21(sap_user=sap_user, file_output=file_output) # Cambia 'YP00118' por el usuario SAP real
            generator_221.generate_emission_script(project_dfs['221'], '221')
            
            # Generar script para 201
            generator_201 = MB21(sap_user=sap_user, file_output=file_output)
            generator_201.generate_emission_script(project_dfs['201'], '201')
            
            # Both 221 and 201 scripts are generated, now we need to return them individually
            if not generator_221.get_script() and not generator_201.get_script():
                return JSONResponse(status_code=200, content={"message": "No se generaron scripts para los tipos de movimiento especificados.", "script": ""})
            
            # # Combinar scripts
            # full_script = generator_221.get_script() + "\n" + generator_201.get_script()
            
            return JSONResponse(content={
                "message": "Script de emisiones generado exitosamente.",
                "script_221": generator_221.get_script(),
                "script_201": generator_201.get_script(),
                })

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ocurrió un error al procesar el archivo: {e}")
        
#In test        
@app.post("/solicitudes/", tags=["Generación de Scripts"])
async def create_solicitudes_script(
    sap_user: str = Form(...),
    file_output: str = Form(...),  # Ruta de guardado del archivo VBS
    file: UploadFile = File(...)  # Archivo de Solicitudes (XLSX
):
    """
    Sube un archivo de Solicitudes (con múltiples operaciones) y genera los scripts VBS correspondientes.
    """
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Formato de archivo inválido. Por favor, suba un archivo .xlsx")

    try:
        content = await file.read()
        file_stream = BytesIO(content)
        
        processor = DataProcessor()
        df = processor.process_solicitudes_file(file_stream)

        if df.empty:
            return JSONResponse(status_code=200, content={"message": "No se encontraron solicitudes pendientes en el archivo.", "script": ""})

        # Dividir el dataframe por tipo de operación
        op_dfs = processor.split_by_operation(df)
        
        gen_222_script = []
        gen_202_script = []
        gen_add_script = []
        gen_mod_script = []
        gen_del_script = []
        gen_sfin_script = []

        # 1. Devoluciones (MB21 - 222 y 202)
        if not op_dfs['Devolucion'].empty:
            project_dfs = processor.split_by_project_type(op_dfs['Devolucion'])
            gen_222 = MB21(sap_user=sap_user)
            gen_222.generate_emission_script(project_dfs['221'], '222')
            gen_222_script.append(gen_222.get_script())
            
            gen_202 = MB21(sap_user=sap_user)
            gen_202.generate_emission_script(project_dfs['201'], '202')
            gen_202_script.append(gen_202.get_script())

        # 2. Modificaciones (MB22)
        if not op_dfs['Modificar'].empty:
            gen_mod = MB22(sap_user=sap_user)
            gen_mod.generate_modification_script(op_dfs['Modificar'])
            gen_mod_script.append(gen_mod.get_script())
            
        # 3. Borrar Posiciones (MB22)
        if not op_dfs['Borrar'].empty:
            gen_del = MB22(sap_user=sap_user)
            gen_del.generate_deletion_script(op_dfs['Borrar'])
            gen_del_script.append(gen_del.get_script())
            
        # 4. SFIN (MB22)
        if not op_dfs['Sfin'].empty:
            gen_sfin = MB22(sap_user=sap_user)
            gen_sfin.generate_sfin_script(op_dfs['Sfin'])
            gen_sfin_script.append(gen_sfin.get_script())
        
        # Adiciones no está implementado en el script original de la misma forma, se omite por ahora
        # 5. Adiciones (MB22)
        if not op_dfs['Adicionar'].empty:
            gen_add = MB22(sap_user=sap_user)
            gen_add.generate_addition_script(op_dfs['Adicionar'])
            gen_add_script.append(gen_add.get_script())
        

        return JSONResponse(content={
                "message": "Script de solicitudes generado exitosamente.",
                "script_222": gen_222_script,
                "script_202": gen_202_script,
                "script_add": gen_add_script,
                "script_mod": gen_mod_script,
                "script_del": gen_del_script,
                "script_sfin": gen_sfin_script,
             })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al procesar el archivo: {e}")

if __name__ == "__main__":
    uvicorn.run("main_api:app", host="127.0.0.1", port=8000, reload=True)