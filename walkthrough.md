# Walkthrough - OSM Public Transport Data Downloader

Este projeto fornece um script Python para baixar dados de transporte e mobilidade do OpenStreetMap (OSM).

## Mudanças Realizadas

### [codigos_py](file:///c:/R_SMTR/projetos/import_osm/codigos_py)

#### [gui_download_osm.py](file:///c:/R_SMTR/projetos/import_osm/codigos_py/gui_download_osm.py)
Interface visual (GUI) construída com `tkinter`. Ela permite configurar o local, escolher a pasta de salvamento via botão **"Procurar..."** e selecionar a categoria de dados através de uma janela amigável.

Exporta os dados em três formatos:
1. **GeoJSON**: Formato padrão para sistemas web e GIS, preserva todas as geometrias (Pontos e Linhas).
2. **Geopackage (.gpkg)**: Banco de dados espacial moderno e eficiente, ideal para lidar com rotas e malhas cicloviárias.
3. **CSV**: Formato tabular simples. Inclui coluna `geometry_type` e latitude/longitude para elementos do tipo `Point`.

### [Root Directory](file:///c:/R_SMTR/projetos/import_osm)

#### [requirements.txt](file:///c:/R_SMTR/projetos/import_osm/requirements.txt)
Arquivo de dependências. Para rodar o script, você precisa instalar as bibliotecas:
```bash
pip install -r requirements.txt
```

## Como utilizar

O projeto agora oferece duas maneiras de baixar os dados: via **Interface Visual (GUI)** ou via **Linheiro de Comando (Terminal)**.

### 1. Utilizando a Interface Visual (Mais fácil)
Para abrir a janela do programa, execute:
```bash
python codigos_py/gui_download_osm.py
```
Preencha o local, o nome do arquivo, escolha a categoria e clique em "BAIXAR DADOS OSM".

### 2. Utilizando o Terminal (Avançado)
O script aceita vários parâmetros para facilitar o download automatizado.

### 1. Especificando o Local
Use `--place` para definir a cidade ou bairro (padrão: "Rio de Janeiro"):
```bash
python codigos_py/download_osm_transport_data.py --place "Rio de Janeiro, Brazil"
```

### 2. Escolhendo o que baixar (Categorias)
Use `--category` para filtrar os dados:
- `stops`: Apenas pontos de parada e estações.
- `routes`: Apenas rotas de ônibus, trem, metrô, etc.
- `cycling`: Ciclovias, ciclofaixas e rotas de bicicleta.
- `corridors`: Corredores de BRT e faixas exclusivas.
- `all`: Tudo o que está acima (padrão).

Exemplo (baixar apenas ciclovias):
```bash
python codigos_py/download_osm_transport_data.py --category cycling
```

### 3. Alterando o Diretório de Saída
Use o argumento `--output` para definir a pasta e o nome base do arquivo (padrão: "osm_data"):
```bash
python codigos_py/download_osm_transport_data.py --output "dados/rj/mobilidade_rj"
```
Isso criará os arquivos `dados/rj/mobilidade_rj.geojson`, `.csv` e `.gpkg`.

### 4. Filtros Customizados (Avançado)
Você pode passar tags OSM customizadas em formato JSON via `--tags`:
```bash
python codigos_py/download_osm_transport_data.py --tags "{\"amenity\":\"bicycle_parking\"}"
```
