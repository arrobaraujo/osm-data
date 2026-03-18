# Descricao dos Codigos

Este projeto reune scripts em R para preparar dados geograficos do Data.Rio e de bases operacionais da SMTR para uso no OpenStreetMap (OSM). Em geral, os scripts leem arquivos geoespaciais brutos, renomeiam atributos para chaves compativeis com o OSM, ajustam geometria e exportam o resultado em GeoJSON.

## Visao Geral

- `ImportaçãoEdificiosOSM.R`: processa edificacoes e tenta identificar sobreposicoes para definir `layer`, `building` e `building:part`.
- `ImportacaoLotesOSM.R`: prepara lotes para exportacao em GeoJSON com atributos do IPP.
- `ImportacaoQuadrasOSM.R`: prepara quadras para exportacao em GeoJSON com codigo da quadra.
- `stops_sigmob_to_osm.R`: converte pontos de parada do SIGMOB para tags mais proximas do padrao OSM.

## Dependencias

Os scripts usam principalmente:

- `sf`
- `dplyr`

O script de pontos de parada tambem depende de uma funcao ou pacote que forneca `pegarDadoSIGMOB()`.

## Detalhamento Por Script

### `codigos_R/ImportaçãoEdificiosOSM.R`

Objetivo:
Preparar um arquivo de edificacoes para importacao no OSM, incluindo uma tentativa automatizada de separar edificio principal e partes de edificio sobrepostas.

O que o script faz:

1. Carrega um arquivo GeoPackage de edificacoes previamente recortado no QGIS.
2. Remove a dimensao Z da geometria.
3. Cria um identificador unico por feicao, porque o identificador original do IPP pode se repetir.
4. Converte as geometrias para `POLYGON`.
5. Cria e renomeia campos relevantes para o OSM, como:
   - `height`
   - `ele`
   - `IPP:CodEdificio`
   - `layer`
6. Calcula o centroide de cada edificacao para identificar quando uma feicao esta dentro de outra.
7. Monta uma tabela de relacoes de contencao entre edificios e compara alturas.
8. Usa essa relacao para definir camadas (`layer`) e marcar feicoes internas como `building:part = yes`.
9. Ajusta a tag `building` para evitar que uma mesma feicao fique marcada ao mesmo tempo como edificio inteiro e parte.
10. Simplifica a geometria, filtra edificacoes muito baixas (`height > 2.5`) e grava o resultado em GeoJSON.

Entrada esperada:

- Um arquivo `.gpkg` de edificacoes, com campos como `ALTURA`, `BASE` e `cod_unico`.

Saida gerada:

- `ed_selecionado_proc.geojson`

Observacoes:

- O caminho de trabalho esta fixado com `setwd()` e precisa ser ajustado para o ambiente local.
- A logica de `layer` e `building:part` e heuristica. O proprio codigo indica que alguns casos ainda exigem revisao manual no JOSM.

### `codigos_R/ImportacaoLotesOSM.R`

Objetivo:
Ler lotes brutos e exporta-los em um formato mais adequado para uso no OSM.

O que o script faz:

1. Le um GeoPackage de lotes.
2. Mantem apenas os campos principais de identificacao.
3. Renomeia os atributos para nomes padronizados com prefixo `IPP:`.
4. Reprojeta os dados para `EPSG:4326`.
5. Corrige geometrias invalidas com `st_make_valid()`.
6. Exporta o resultado em GeoJSON.

Entrada esperada:

- `lt_selecionado_bruto.gpkg`

Saida gerada:

- `lt_selecionado_processado.geojson`

Observacoes:

- O caminho de entrada e o caminho de saida precisam ser alterados manualmente antes da execucao.

### `codigos_R/ImportacaoQuadrasOSM.R`

Objetivo:
Preparar a camada de quadras para uso posterior em processos de importacao ou validacao no OSM.

O que o script faz:

1. Le um GeoPackage de quadras.
2. Mantem apenas o codigo da quadra e a geometria.
3. Renomeia o atributo principal para `IPP:CodQuadra`.
4. Reprojeta os dados para `EPSG:4326`.
5. Corrige geometrias invalidas.
6. Exporta o resultado em GeoJSON.

Entrada esperada:

- `qd_selecionada_bruto.gpkg`

Saida gerada:

- `qd_selecionada_processado.geojson`

Observacoes:

- Assim como no script de lotes, os caminhos estao fixados e exigem ajuste local.

### `codigos_R/stops_sigmob_to_osm.R`

Objetivo:
Transformar dados de pontos de parada oriundos do SIGMOB em um conjunto de tags proximo ao modelo usado no OSM.

O que o script faz:

1. Busca os dados de paradas com `pegarDadoSIGMOB("stops")`.
2. Filtra as paradas de um bairro especifico.
3. Filtra tambem por `idModalSmtr == "22"`.
4. Converte latitude e longitude em geometria espacial (`sf`).
5. Seleciona atributos operacionais da parada.
6. Renomeia campos para chaves mais aderentes ao OSM, como `name` e `gtfs:stop_id`.
7. Deriva tags OSM a partir de atributos do SIGMOB, incluindo:
   - `highway = bus_stop`
   - `public_transport = platform`
   - `shelter`
   - `bench`
   - `tactile_paving`
   - `wheelchair`
   - `bin`
   - `traffic_sign`
   - `advertising`
8. Exporta o resultado em GeoJSON para uma pasta do bairro.

Entrada esperada:

- Base SIGMOB de pontos de parada acessivel pela funcao `pegarDadoSIGMOB()`.

Saida gerada:

- Arquivo GeoJSON de pontos de parada por bairro.

Observacoes:

- O script depende de objetos e funcoes que nao estao definidos neste repositorio, entao ele pode fazer parte de um ambiente de trabalho maior.
- O nome do bairro e o diretorio de saida sao definidos manualmente no inicio e no final do script.

## Fluxo Geral Do Projeto

O fluxo sugerido pelo repositorio e:

1. Recortar ou preparar os dados brutos no QGIS ou em outra ferramenta GIS.
2. Executar os scripts R para padronizar atributos e geometrias.
3. Gerar arquivos GeoJSON intermediarios.
4. Revisar o resultado antes da importacao no OSM, especialmente no caso das edificacoes.

## Limitacoes Atuais

- Os caminhos de leitura e escrita estao hardcoded nos scripts.
- Nao ha parametrizacao via argumentos, funcoes ou arquivo de configuracao.
- Parte do fluxo depende de ajuste manual e revisao no JOSM.
- Nem todas as dependencias auxiliares aparecem declaradas no repositorio.

## Sugestao De Evolucao

Algumas melhorias naturais para este projeto seriam:

- transformar os scripts em funcoes reutilizaveis;
- centralizar caminhos e parametros em um arquivo de configuracao;
- documentar as dependencias externas e a origem exata dos dados;
- adicionar um exemplo de execucao para cada script.