import os
import shutil
import threading
import flet as ft
from nfecopier import NFeCopier

copier = NFeCopier("", "", "")

def main(page: ft.Page):
    page.title = "Procurador de XMLs"
    page.theme_mode = ft.ThemeMode.LIGHT

    # Widgets de status e progresso
    progress = ft.ProgressBar(width=400, value=0)
    status_text = ft.Text("Aguardando seleção de arquivos e diretórios...")

    # Campos de exibição dos paths
    file_path_display = ft.TextField(label="Arquivo Excel com listagem de notas", disabled=True)
    source_directory_display = ft.TextField(label="Diretório onde estão os XMLs", disabled=True)
    destination_directory_display = ft.TextField(label="Diretório destino para XMLs", disabled=True)

    # --- Alternar tema ---
    def change_theme(e):
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            fab.icon = ft.Icons.DARK_MODE
        else:
            page.theme_mode = ft.ThemeMode.DARK
            fab.icon = ft.Icons.LIGHT_MODE
        page.update()

    fab = ft.FloatingActionButton(
        icon=ft.Icons.LIGHT_MODE,
        on_click=change_theme,
        tooltip="Mudar o tema do app"
    )
    page.floating_action_button = fab

    # --- Dialog de conclusão ---
    def abrir_dialog(_=None):
        page.open(dlg_modal)  # abre o dialog

    def fechar_dialog(_=None):
        page.close(dlg_modal)  # fecha o dialog

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Processo finalizado"),
        content=ft.Text("Verifique o log para notas que não foram encontradas."),
        actions=[
            ft.TextButton("OK!", on_click=fechar_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
)


    # --- File Pickers ---
    def on_pick_file(e: ft.FilePickerResultEvent):
        copier.excel_path = e.files[0].path if e.files else ""
        file_path_display.value = copier.excel_path or "Cancelado!"
        file_path_display.update()

    pick_files_dialog = ft.FilePicker(on_result=on_pick_file)

    def on_pick_source(e: ft.FilePickerResultEvent):
        copier.source_directory = e.path or ""
        source_directory_display.value = copier.source_directory or "Cancelado!"
        source_directory_display.update()

    pick_source_directory_dialog = ft.FilePicker(on_result=on_pick_source)


    def on_pick_destination(e: ft.FilePickerResultEvent):
        copier.destination_directory = e.path or ""
        destination_directory_display.value = copier.destination_directory or "Cancelado!"
        destination_directory_display.update()

    pick_destination_directory_dialog = ft.FilePicker(on_result=on_pick_destination)

    
    page.overlay.extend([
        pick_files_dialog,
        pick_source_directory_dialog,
        pick_destination_directory_dialog
    ])

    # --- Execução em thread para não travar a UI ---
    def executar_copia(_):
        if not copier.excel_path or not copier.source_directory or not copier.destination_directory:
            status_text.value = "Por favor, selecione todos os caminhos antes de continuar!"
            page.update()
            return

        def processar():
            status_text.value = "Carregando planilha..."
            page.update()
            copier.load_data()
            total = len(copier.df)
            progresso = 0

            not_found_keys = {}

            for idx, row in enumerate(copier.df.itertuples(), start=1):
                local = getattr(row, 'LOCAL')
                chave_nfe = getattr(row, 'CHAVENFE')
                encontrado = False

                folder_name = f"LOCAL_{local}"
                dest_folder = os.path.join(copier.destination_directory, folder_name)
                os.makedirs(dest_folder, exist_ok=True)

                for root, _, files in os.walk(copier.source_directory):
                    for file in files:
                        if chave_nfe in file and file.endswith('.xml'):
                            encontrado = True
                            src_file = os.path.join(root, file)
                            dest_file = os.path.join(dest_folder, file)
                            shutil.copy2(src_file, dest_file)
                            break
                    if encontrado:
                        break

                if not encontrado:
                    not_found_keys.setdefault(local, []).append(chave_nfe)

                progresso = idx / total
                progress.value = progresso
                status_text.value = f"Copiando {idx}/{total} ({progresso:.0%})"
                page.update()

            # Criação do log
            if not_found_keys:
                log_dir = os.path.join(copier.destination_directory, "LOG_CHAVES_N_ENCONTRADAS")
                os.makedirs(log_dir, exist_ok=True)
                for local, chaves in not_found_keys.items():
                    log_file = os.path.join(log_dir, f'LOCAL_{local}_CHAVES_NAO_ENCONTRADAS.txt')
                    with open(log_file, 'w') as f:
                        for chave in chaves:
                            f.write(f"{chave}\n")

            status_text.value = "Processo concluído!"
            progress.value = 1
            page.update()
            abrir_dialog()

        threading.Thread(target=processar).start()

    # Layout principal
    page.add(
        ft.Column([
            ft.Row([
                ft.ElevatedButton(
                    text="Selecionar Excel",
                    icon=ft.Icons.FILE_UPLOAD,
                    on_click=lambda _: pick_files_dialog.pick_files(allow_multiple=False)
                ),
            ]),
            file_path_display,
            ft.Row([
                ft.ElevatedButton(
                    text="Diretório origem XMLs",
                    icon=ft.Icons.FOLDER_COPY,
                    on_click=lambda _: pick_source_directory_dialog.get_directory_path()
                ),
            ]),
            source_directory_display,
            ft.Row([
                ft.ElevatedButton(
                    text="Diretório destino XMLs",
                    icon=ft.Icons.FOLDER_OPEN_SHARP,
                    on_click=lambda _: pick_destination_directory_dialog.get_directory_path()
                ),
            ]),
            destination_directory_display,
            ft.Row([
                ft.ElevatedButton(
                    text="Procurar XMLs!",
                    icon=ft.Icons.SEARCH,
                    on_click=executar_copia
                ),
            ]),
            progress,
            status_text
        ])
    )

ft.app(target=main, assets_dir='assets')
