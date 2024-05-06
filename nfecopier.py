import os
import shutil
import pandas as pd

class NFeCopier:
    def __init__(self, excel_path, source_directory, destination_directory):
        self.excel_path = excel_path
        self.source_directory = source_directory
        self.destination_directory = destination_directory
        

    def load_data(self):
        self.df = pd.read_excel(self.excel_path)

    def copy_files(self):        
        not_found_keys = {}  # Dicionário para armazenar chaves não encontradas, agrupadas por local

        for row in self.df.itertuples():
            local = getattr(row, 'LOCAL')
            chave_nfe = getattr(row, 'CHAVENFE')
            found = False

            folder_name = f"LOCAL_{local}"
            full_dest_path = os.path.join(self.destination_directory, folder_name)            
            os.makedirs(full_dest_path, exist_ok=True)

            for root, dirs, files in os.walk(self.source_directory):                
                for file in files:
                    if chave_nfe in file and file.endswith('.xml'):
                        found = True
                        src_file_path = os.path.join(root, file)
                        dest_file_path = os.path.join(full_dest_path, file)
                        shutil.copy2(src_file_path, dest_file_path)
                        break
                if found:
                    break

            if not found:
                if local not in not_found_keys:
                    not_found_keys[local] = []  # Inicializa uma lista se ainda não existe
                not_found_keys[local].append(chave_nfe)  # Adiciona a chave à lista do local específico

        if not_found_keys:
            log_directory = os.path.join(self.destination_directory, "LOG_CHAVES_N_ENCONTRADAS")
            os.makedirs(log_directory, exist_ok=True)
            for local, chaves in not_found_keys.items():
                log_file_path = os.path.join(log_directory, f'LOCAL_{local}_CHAVES_NAO_ENCONTRADAS.txt')
                with open(log_file_path, 'w') as log_file:
                    for chave in chaves:
                        log_file.write(f"{chave}\n")

        print("Processo concluído. Verifique o log para notas não encontradas.")
        


        
