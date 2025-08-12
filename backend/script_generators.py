import time

class BaseGenerator:
    """
    Clase base con funcionalidades comunes para todos los generadores de scripts.
    """
    def __init__(self, sap_user: str , file_output: str):
        self.sap_user = sap_user
        self.file_output = file_output  # Ruta del archivo de salida, se puede definir en cada subclase
        self.today = time.strftime("%d.%m.%Y")
        # El script se construye en una lista de strings en memoria
        self.script_lines = []

    def _get_base_script_header(self):
        return '''If Not IsObject(application) Then
  Set SapGuiAuto  = GetObject("SAPGUI")
  Set application = SapGuiAuto.GetScriptingEngine
End If
If Not IsObject(connection) Then
  Set connection = application.Children(0)
End If
If Not IsObject(session) Then
  Set session    = connection.Children(0)
End If
If IsObject(WScript) Then
  WScript.ConnectObject session,     "on"
  WScript.ConnectObject application, "on"
End If
session.findById("wnd[0]").maximize'''

    def _select_check_sap(self, cant_mats: int) -> list:
        return [f'session.findById("wnd[0]/usr/sub:SAPMM07R:0521/chkRESB-XWAOK[{n},76]").selected = true' for n in range(cant_mats)]

    def _mats_and_cants(self, store: str, mats_cants: dict) -> list:
        lines = []
        for i, (mat, cant) in enumerate(mats_cants.items()):
            lines.append(f'session.findById("wnd[0]/usr/sub:SAPMM07R:0521/ctxtRESB-MATNR[{i},7]").text = "{mat}"')
            lines.append(f'session.findById("wnd[0]/usr/sub:SAPMM07R:0521/txtRESB-ERFMG[{i},26]").text = "{cant}"')
            lines.append(f'session.findById("wnd[0]/usr/sub:SAPMM07R:0521/ctxtRESB-LGORT[{i},53]").text = "{store}"')
        return lines

    def get_script(self) -> str:
        """Retorna el script completo como un string."""
        return "\n".join(self.script_lines)


class MB21(BaseGenerator):
    """
    Genera scripts para la transacción MB21 (Crear Reserva).
    Incluye movimientos 201, 202, 221, 222.
    """
    proyecto_201_map = {
        '200000703': "90010010", # EDIFICIOS - BROWNFIELD
        '200000702': "92030040", # DIFERENCIAS, MERMAS
    }

    def _base_mb21(self, mov_type: str):
        return f'''session.findById("wnd[0]/tbar[0]/okcd").text = "mb21"
session.findById("wnd[0]").sendVKey 0
session.findById("wnd[0]/usr/ctxtRM07M-BWART").text = "{mov_type}"
session.findById("wnd[0]/usr/ctxtRM07M-WERKS").text = "PE06"
session.findById("wnd[0]/usr/ctxtRM07M-WERKS").caretPosition = 2
session.findById("wnd[0]").sendVKey 0'''
    
    def get_details_xlsx_save_to_text(self, df, po: str):
        #This is designed to save the details of the DataFrame to a text file.
        # You can configure ur structure here.
        # """poCode = "2025-551300301"
        #    ipCode = "P-25-5592736918"
        #    proyCode = "MANTENIMIENTO 2025"
        #    ecCode = "COBRA""""
        lines = []
        ip_code = df[df['PO'] == po]['IP']
        proy_code = df[df['PO'] == po]['MOV_SAP']
        ec_code = df[df['PO'] == po]['EECC']
        lines.append(f'poCode = "{po}"')  # Add PO code
        lines.append(f'ipCode = "{ip_code.iloc[0]}"')  # Add IP code
        lines.append(f'movSAP = "{proy_code.iloc[0]}"')  # Add Project code
        lines.append(f'ecCode = "{ec_code.iloc[0]}"')  # Add EECC code

        return lines

    def _base_ini(self, pep: str, mov_type: str):
        if mov_type == '221':
            # The PEP is the code that identifies the project in SAP
            return f'''session.findById("wnd[0]/usr/txtRKPF-WEMPF").text = "{self.sap_user}"
session.findById("wnd[0]/usr/subBLOCK:SAPLKACB:9000/ctxtCOBL-PS_POSID").text = "{pep}"  
session.findById("wnd[0]/usr/subBLOCK:SAPLKACB:9000/ctxtCOBL-FKBER").text = "NO_PRESUP"'''
        
        elif mov_type == '201':
            # The PEP is the code that identifies what project will be used in SAP, for me this goes to the proyecto_201_map dictonary
            # it takes 2 codes to identify the area function and the pep
            area_func = self.proyecto_201_map.get(pep, "Default if not found")
            return f'''session.findById("wnd[0]/usr/txtRKPF-WEMPF").text = "{self.sap_user}"
session.findById("wnd[0]/usr/subBLOCK:SAPLKACB:1013/ctxtCOBL-KOSTL").text = "{pep}"
session.findById("wnd[0]/usr/subBLOCK:SAPLKACB:1013/ctxtCOBL-FKBER").text = "{area_func}"'''

        elif mov_type == '222': # Devolución
            return f'''session.findById("wnd[0]/usr/ctxtKM07R-SAKNR").text = "2303000000"
session.findById("wnd[0]/usr/txtRKPF-WEMPF").text = "{self.sap_user}"
session.findById("wnd[0]/usr/subBLOCK:SAPLKACB:9000/ctxtCOBL-PS_POSID").text = "{pep}"
session.findById("wnd[0]/usr/subBLOCK:SAPLKACB:9000/ctxtCOBL-FKBER").text = "NO_PRESUP"'''
        # Agrega el caso para 202 si es diferente de 222

        else: # Devolución 202
            area_func = self.proyecto_201_map.get(pep, "Default if not found")
            return f'''session.findById("wnd[0]/usr/txtRKPF-WEMPF").text = "{self.sap_user}"
session.findById("wnd[0]/usr/subBLOCK:SAPLKACB:1013/ctxtCOBL-KOSTL").text = "{pep}"
session.findById("wnd[0]/usr/subBLOCK:SAPLKACB:1013/ctxtCOBL-FKBER").text = "{area_func}"'''
            

    def _enter_mats(self, count_mats: int):
        lines = ['session.findById("wnd[0]").sendVKey 11']
        lines.extend(['session.findById("wnd[0]").sendVKey 0'] * count_mats)
        # Click the reservation number from the status bar
        lines.append('session.findById("wnd[0]/sbar").doubleClick')
        lines.append('reservationNumber = session.findById("wnd[0]/sbar").Text')
        lines.append('reservationNumber = Mid(reservationNumber, InStr(reservationNumber, "Reservation") + 14, 7)')
        # Close and go back
        lines.append('session.findById("wnd[0]/shellcont").close')
        lines.append('session.findById("wnd[0]/usr/ctxtRM07M-BWART").caretPosition = 3')
        lines.append('session.findById("wnd[0]").sendVKey 0')

        return lines
    

    def base_save_reservation(self, mov_type: str):
        if mov_type in ['221', '201']:
            file_path_vr = rf"{self.file_output}"  # Cambia esto por la ruta real del archivo VR
            # This is the base information for the VR file, adjust as needed 221 or 201
            vr_base_information = 'file.WriteLine reservationNumber & "," & poCode & "," & ipCode & "," & proyCode & "," & ecCode'
        else:  # 202 or 222
            file_path_vr = rf"{self.file_output}"  # Cambia esto por la ruta real del archivo VR
            vr_base_information = 'file.WriteLine reservationNumber & "," & poCode & "," & ipCode & "," & proyCode & "," & ecCode & "," & svrCode'

        return file_path_vr, vr_base_information
    

    def save_reservation(self, file_path, vr_base_information):
        """
        Save the reservation details and goes to after the enter materials.
        """
        lines = []
        lines.append(f'filePath = "{file_path}"')
        lines.append('Set fso = CreateObject("Scripting.FileSystemObject")')
        lines.append("Set file = fso.OpenTextFile(filePath, 8, True) ' 8 = Append mode")
        lines.append(vr_base_information)
        lines.append('file.Close')

        return lines

    def generate_emission_script(self, df, mov_type: str):
        """Genera un script de emisión (221) o (201)."""
        if df.empty:
            return "No data to generate script."
            
        self.script_lines.append(self._get_base_script_header())
        self.script_lines.append(self._base_mb21(mov_type))

        group_by_col = 'PO' if 'PO' in df.columns else 'SVR'

        
        # Get the path and the vr_base_information for saving the reservation
        file_path_vr, vr_base_information = self.base_save_reservation(mov_type)

        for po in df[group_by_col].unique():
            filtered_df = df[df[group_by_col] == po]
            materials_cants = {}
            storage_pep = []

            # Collect the details for the request of reservation
            self.script_lines.extend(self.get_details_xlsx_save_to_text(filtered_df, po))
            
            for _, row in filtered_df.iterrows():
                # Asegurarse que la cantidad es un string para el script
                materials_cants[str(row['Codigo Material'])] = str(row['Cantidad'])
                storage_pep.append(str(row['Codigo Almacen']))
                storage_pep.append(str(row['ELEMENTO PEP']))
            
            storage_pep = sorted(list(set(storage_pep)))
            # If storage_pep is empty, continue to the next iteration
            if not storage_pep:
                continue 
            else:
                almacen = storage_pep[0]
                pep = storage_pep[1]
                
                self.script_lines.extend(self._select_check_sap(len(materials_cants)))
                self.script_lines.append(self._base_ini(pep, mov_type))
                self.script_lines.extend(self._mats_and_cants(almacen, materials_cants))
                self.script_lines.extend(self._enter_mats(len(materials_cants)))
                self.script_lines.extend(self.save_reservation(file_path_vr, vr_base_information))  
        
        # End Script
        self.script_lines.append('session.findById("wnd[0]/tbar[0]/btn[15]").press') # Back


class MB22(BaseGenerator):
    """
    Genera scripts para la transacción MB22 (Modificar Reserva).
    """
    proyecto_201_map = {
        '200000703': "90010010", # EDIFICIOS - BROWNFIELD
        '200000702': "92030040", # DIFERENCIAS, MERMAS
    }

    # Base for the MB22 script
    def _base_mb22(self):
        return '''session.findById("wnd[0]/tbar[0]/okcd").text = "mb22"
session.findById("wnd[0]").sendVKey 0'''
    
    # Base for joining the VR
    def join_vr(self, vr_number: str):
        return f'''session.findById("wnd[0]/usr/ctxtRM07M-RSNUM").text = "{vr_number}"
session.findById("wnd[0]/usr/ctxtRM07M-RSNUM").caretPosition = 7
session.findById("wnd[0]").sendVKey 0'''

    # Base for the modification of the reservation  
    def _modify_pos(self, mod_storage: dict):
        lines = []
        for pos, cant in mod_storage.items():
            lines.append(f'session.findById("wnd[0]/usr/sub:SAPMM07R:0521/txtRESB-ERFMG[{pos-1},26]").text = "{cant}"')
        return lines

    # Base for deleting positions 
    def _delete_pos(self, positions_to_delete: list):
        lines = []
        for pos in positions_to_delete:
            lines.append(f'session.findById("wnd[0]/usr/sub:SAPMM07R:0521/chkRESB-XLOEK[{pos-1},83]").selected = true')
            lines.append(f'session.findById("wnd[0]/usr/sub:SAPMM07R:0521/txtRESB-ERFMG[{pos-1},26]").text = "0"')
        return lines
    
    # Base for addition, this is the base for the addition of materials (Addition )
    def _base_addition(self):
        # This is the base for addition, it can be modified to fit your needs
        # mine goes to get the date by dd.mm.yyyy
        return '''session.findById("wnd[0]/tbar[1]/btn[7]").press
session.findById("wnd[1]/usr/ctxtRM07M-BDTER").text = "{}"
session.findById("wnd[1]/usr/ctxtRM07M-WERKS").text = "PE06"
session.findById("wnd[1]/usr/ctxtRM07M-WERKS").setFocus
session.findById("wnd[1]/usr/ctxtRM07M-WERKS").caretPosition = 4
session.findById("wnd[1]").sendVKey 0'''.format(self.today)

    # Base for adding positions (Addition )
    def _add_pos(self, add_storage: dict):
        lines = []
        num_items = len(add_storage['Codigo Material'])
        for i in range(num_items):
            lines.append(f'session.findById("wnd[0]/usr/sub:SAPMM07R:0521/ctxtRESB-MATNR[{i},7]").text = "{add_storage["Codigo Material"][i]}"')
            lines.append(f'session.findById("wnd[0]/usr/sub:SAPMM07R:0521/txtRESB-ERFMG[{i},26]").text = "{add_storage["Cantidad"][i]}"')
            lines.append(f'session.findById("wnd[0]/usr/sub:SAPMM07R:0521/ctxtRESB-LGORT[{i},53]").text = "{add_storage["Codigo Almacen"][i]}"')
        return lines
    
    # Base for entering materials in MB22 (Addition )
    def _enter_mats_mb22(self, count_mats: int, mov_type:str, pep: str):
        lines = []

        if mov_type in ['201'] and pep is not None:
            lines.append('session.findById("wnd[0]/usr/sub:SAPMM07R:0521/chkRESB-XWAOK[0,76]").setFocus')
            lines.append('session.findById("wnd[0]").sendVKey 11')
            lines.append('session.findById("wnd[0]").sendVKey 0')
            lines.append(f'session.findById("wnd[0]/usr/subBLOCK:SAPLKACB:1013/ctxtCOBL-FKBER").text = "{pep}"')
            lines.append('session.findById("wnd[0]/usr/subBLOCK:SAPLKACB:1013/ctxtCOBL-FKBER").caretPosition = 8')

        elif mov_type in ['221'] and pep is None:
            lines.append('session.findById("wnd[0]/usr/sub:SAPMM07R:0521/chkRESB-XWAOK[1,76]").setFocus')
            lines.append('session.findById("wnd[0]/tbar[0]/btn[11]").press')
            lines.append('session.findById("wnd[0]").sendVKey 0')
            lines.append('session.findById("wnd[0]/usr/subBLOCK:SAPLKACB:9000/ctxtCOBL-FKBER").text = "NO_PRESUP"')
            lines.append('session.findById("wnd[0]/usr/subBLOCK:SAPLKACB:9000/ctxtCOBL-FKBER").caretPosition = 9')

        lines.extend(['session.findById("wnd[0]").sendVKey 0'] * count_mats)

        return lines

        # Additional condition when adding materiales but no using.
        # ['''session.findById("wnd[0]/usr/sub:SAPMM07R:0521/chkRESB-XWAOK[1,76]").setFocus
        # session.findById("wnd[0]/tbar[0]/btn[11]").press''']

    def _sfin_pos(self, positions_to_sfin: list):
        lines = []
        for pos in positions_to_sfin:
             lines.append(f'session.findById("wnd[0]/usr/sub:SAPMM07R:0521/chkRESB-KZEAR[{pos-1},78]").selected = true')
        return lines
        

    def generate_modification_script(self, df):
        if df.empty: 
            return
        else:
            self.script_lines.append(self._get_base_script_header())
            self.script_lines.append(self._base_mb22())  # No VR needed for modification
        for vr in df['VR'].unique():
            self.script_lines.append(self.join_vr(str(vr)))            
            filtered_df = df[df['VR'] == vr]
            mod_storage = {row['POS']: row['Cantidad'] for _, row in filtered_df.iterrows()}
            
            self.script_lines.extend(self._modify_pos(mod_storage))
            self.script_lines.append('session.findById("wnd[0]/tbar[0]/btn[11]").press') # Save
        self.script_lines.append('session.findById("wnd[0]/tbar[0]/btn[15]").press') # Back
    

    def generate_deletion_script(self, df):
        if df.empty:
            return
        else:
            self.script_lines.append(self._get_base_script_header())
            self.script_lines.append(self._base_mb22())  # No VR needed for deletion
        for vr in df['VR'].unique():
            self.script_lines.append(self.join_vr(str(vr)))
            positions = df[df['VR'] == vr]['POS'].tolist()
            self.script_lines.extend(self._delete_pos(positions))
            self.script_lines.append('session.findById("wnd[0]/tbar[0]/btn[11]").press') # Save
        self.script_lines.append('session.findById("wnd[0]/tbar[0]/btn[15]").press') # Back


    def generate_sfin_script(self, df):
        if df.empty: 
            return
        else:
            self.script_lines.append(self._get_base_script_header())
            self.script_lines.append(self._base_mb22())  # No VR needed for SFIN
        for vr in df['VR'].unique():
            self.script_lines.append(self.join_vr(str(vr)))
            
            positions = df[df['VR'] == vr]['POS'].tolist()

            self.script_lines.extend(self._sfin_pos(positions))
            self.script_lines.append('session.findById("wnd[0]/tbar[0]/btn[11]").press') # Save
        self.script_lines.append('session.findById("wnd[0]/tbar[0]/btn[15]").press') # Back


    # Generate script for addition
    # Pending, to add a verification for the move type
    def generate_addition_script(self, df):
        if df.empty:
            return
        else:
            self.script_lines.append(self._get_base_script_header())
            self.script_lines.append(self._base_mb22())  # No VR needed for addition

        for vr in df['VR'].unique():
            self.script_lines.append(self.join_vr(str(vr)))
            
            filtered_df = df[df['VR'] == vr]
            # Working with Codigo Material and Cantidad because is based on my structure
            # Pendent, add verification of stock for the material

            # Confirm the move type and proyect
            if self.proyecto_201_map.get(filtered_df['ELEMENTO PEP'].unique()[0]) is not None:
                ele_pep = filtered_df['ELEMENTO PEP'].unique()[0]
                mov_type = '201'
            else:
                ele_pep = None
                mov_type = '221'

            #Create a dic for the addition
            add_storage = {
                'Codigo Material': [],
                'Cantidad': [],
                'Codigo Almacen': [],
                'ELEMENTO PEP': []
            }

            for _, row in filtered_df.iterrows():
                add_storage['Codigo Material'].append(row['Codigo Material'])
                add_storage['Cantidad'].append(row['Cantidad'])
                add_storage['Codigo Almacen'].append(row['Codigo Almacen'])
                add_storage['ELEMENTO PEP'].append(row['ELEMENTO PEP'])
            
            self.script_lines.append(self._base_addition())
            self.script_lines.extend(self._select_check_sap(len(add_storage['Codigo Material'])))
            self.script_lines.extend(self._add_pos(add_storage))
            self.script_lines.extend(self._enter_mats_mb22(len(add_storage['Codigo Material']), mov_type,ele_pep))
            self.script_lines.append('session.findById("wnd[0]/tbar[0]/btn[11]").press') # Save

        self.script_lines.append('session.findById("wnd[0]/tbar[0]/btn[15]").press')

