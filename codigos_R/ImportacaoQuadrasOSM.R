library(sf)
library(dplyr)

### Ajuste a localizacao do seu arquivo bruto de quadras.

quadras <- st_read("D:/Edificacoes_2013/Tutorial/qd_selecionada_bruto.gpkg") %>%
  select(COD_QUADRA,geom) %>%
  rename(`IPP:CodQuadra` = COD_QUADRA) %>%
  st_transform(4326) %>%
  st_make_valid()

### Ajuste o destino do seu arquivo ajustado de quadras.

endereco_quadras <- c("D:/Edificacoes_2013/Tutorial/qd_selecionada_processado.geojson")
st_write(quadras,endereco_quadras)
