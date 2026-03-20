# Walkthrough - OSM Public Transport Data Downloader

Este projeto fornece um script Python para baixar dados de transporte e mobilidade do OpenStreetMap (OSM).

## Mudanças Realizadas

### [codigos_py](file:///c:/R_SMTR/projetos/import_osm/codigos_py)

#### [download_osm_transport_data.py](file:///c:/R_SMTR/projetos/import_osm/codigos_py/download_osm_transport_data.py)
Script atualizado para baixar **pontos de parada**, **rotas** (ônibus, trem, metrô, VLT), **corredores de ônibus/BRT** (`busway`, faixas exclusivas) e toda a **infraestrutura cicloviária** (ciclovias, ciclofaixas e ciclorotas).

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

O script aceita vários parâmetros para facilitar o download de diferentes tipos de dados e para diferentes locais.

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
