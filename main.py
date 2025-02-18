import flet as ft
from nfecopier import NFeCopier

copier = NFeCopier("", "", "")  # Inicializa com strings vazias

def main(page: ft.Page):
    page.title = "Procurador de XMLs"
    page.theme_mode = ft.ThemeMode.LIGHT   

    def change_theme(e):
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
        else:
            page.theme_mode = ft.ThemeMode.DARK
        e.control.selected = not e.control.selected
        e.control.update()
        page.update()

    page.floating_action_button = ft.IconButton(
        icon=ft.icons.LIGHT_MODE, 
        selected_icon=ft.icons.DARK_MODE,  
        on_click=change_theme,
        tooltip="Mudar o tema do app",
        alignment=ft.Alignment(x=1, y=-1),
    )     

    def open_dlg_modal(e):
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def close_dlg(e):
        dlg_modal.open = False
        page.update()

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Processo finalizado"),
        content=ft.Text("Por favor, verifique no log as notas que não foram encontradas."),
        actions=[
            ft.TextButton("OK!", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Criando instâncias de FilePicker
    pick_files_dialog = ft.FilePicker()
    pick_source_directory_dialog = ft.FilePicker()
    pick_destination_directory_dialog = ft.FilePicker()

    # Definição dos métodos de resposta para cada FilePicker
    def pegar_path_arquivo(e: ft.FilePickerResultEvent):
        if e.files:
            copier.excel_path = e.files[0].path
            file_path_display.value = copier.excel_path
        else:
            file_path_display.value = "Cancelled!"
        file_path_display.update()

    def pegar_directory_source(e: ft.FilePickerResultEvent):
        copier.source_directory = e.path if e.path else "Cancelled!"
        source_directory_display.value = copier.source_directory
        source_directory_display.update()

    def pegar_directory_destination(e: ft.FilePickerResultEvent):
        copier.destination_directory = e.path if e.path else "Cancelled!"
        destination_directory_display.value = copier.destination_directory
        destination_directory_display.update()

    def executar_copia(_):
        copier.load_data()
        copier.copy_files()
        open_dlg_modal(None)

    file_path_display = ft.TextField(
        "Arquivo Excel com a listagem de notas",
        disabled=True,
    )
    source_directory_display = ft.TextField(
        "Onde que acha que estão os arquivos xmls?",
        disabled=True,
    )
    destination_directory_display = ft.TextField(
        "Onde você quer armazenar os xmls encontrados?",
        disabled=True,
    )

    # Definindo eventos de resultado
    pick_files_dialog.on_result = pegar_path_arquivo
    pick_source_directory_dialog.on_result = pegar_directory_source
    pick_destination_directory_dialog.on_result = pegar_directory_destination

    page.overlay.extend([
        pick_files_dialog,
        pick_source_directory_dialog,
        pick_destination_directory_dialog
    ])   

    page.add(ft.Row([
                    ft.ElevatedButton(
                        text="Arquivo Excel",
                        icon=ft.icons.FILE_UPLOAD,
                        on_click=lambda _: pick_files_dialog.pick_files(allow_multiple=False)
                    ),
                ]),
                file_path_display,
                ft.Row([
                    ft.ElevatedButton(
                        text="Diretório de origem dos xmls",
                        icon=ft.icons.FOLDER_COPY,
                        on_click=lambda _: pick_source_directory_dialog.get_directory_path()
                    ),
                ]),
                source_directory_display,
                ft.Row([
                    ft.ElevatedButton(
                        text="Diretório destino dos xmls encontrados",
                        icon=ft.icons.FOLDER_OPEN_SHARP,
                        on_click=lambda _: pick_destination_directory_dialog.get_directory_path()
                    ),
                ]),
                destination_directory_display,
                ft.Row([
                    ft.ElevatedButton(
                        text="Procurar os xmls!",
                        icon=ft.icons.SEARCH,
                        on_click=executar_copia
                    ),
                ]),)

ft.app(target=main, assets_dir='assets')
