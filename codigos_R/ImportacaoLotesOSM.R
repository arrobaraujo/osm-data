library(sf)
library(dplyr)

### Ajuste a localizacao do seu arquivo bruto de lotes.

lotes <- st_read("D:/Edificacoes_2013/Tutorial/lt_selecionado_bruto.gpkg") %>%
  select(cod_quadra,cod_lote,cod_np,cod_trecho,geom) %>%
  rename(`IPP:CodQuadra` = cod_quadra) %>%
  rename(`IPP:CodLote` = cod_lote) %>%
  rename(`IPP:CodNP` = cod_np) %>%
  rename(`IPP:CodTrecho` = cod_trecho) %>%
  st_transform(4326) %>%
  st_make_valid()

### Ajuste o destino do seu arquivo ajustado de lotes.

endereco_lote <- c("D:/Edificacoes_2013/Tutorial/lt_selecionado_processado.geojson")
st_write(lotes,endereco_lote)

