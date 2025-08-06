# Projeto Flet - Gerenciamento de XMLs

Este é um projeto Python que utiliza o Flet para construir uma interface gráfica que gerencia XMLs de notas fiscais eletrônicas (NF-e). Este projeto facilita a seleção, a cópia e o gerenciamento de arquivos XML de notas fiscais.

## Preparação

### 1. Instalar Dependências

Antes de começar, é importante garantir que todas as dependências do projeto estejam instaladas. Para instalar as dependências, execute o seguinte comando:

```bash

pip freeze | Out-File -FilePath requirements.txt -Encoding UTF8

pip install -r requirements.txt

```
### 2. Gerar o EXE

```bash

pyinstaller --onefile --noconsole --icon=icone.ico --add-data "assets;assets" main.py

```
