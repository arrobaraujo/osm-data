# Inicializacao ----

## Carrega bibliotecas necessarias.

library(sf)
library(dplyr)

## Define pasta onde esta o arquivo previamente recortado no QGIS.

setwd("D:/Edificacoes_2013/Tutorial")

## Define nome do arquivo que sera carregado.

nome_arq <- "ed_selecionado_bruto"

Edific <- st_read(paste0("./",nome_arq,".gpkg"), stringsAsFactors = F)

## Remove dimensao Z, mantendo arquivo de duas dimensoes (X,Y).

Edific <- st_zm(Edific, drop=T, what='ZM')

## Cria um id para cada objeto. O id do IPP se repete em objetos e nao pode
## ser usado para essa finalidade.

Edific$id <- as.integer(row.names(Edific))

Edific <- st_cast(Edific,"POLYGON")

## Renomeia campos, cria campo layer.

Edific$height <- round(Edific$ALTURA,2)
Edific$ele <- round(Edific$BASE,2)
Edific$`IPP:CodEdificio` <- Edific$cod_unico
Edific$layer <- 0

## Extrai centroide de cada edificio. 
## (Maneira mais facil de identificar sobreposicao.)

edific_centr <- st_centroid(Edific)

## Seleciona colunas.

Edific <- Edific %>% 
  select(id,height,ele,layer,`IPP:CodEdificio`)

## Cria matriz de sobreposicao e converte em data.frame.

a <- st_within(edific_centr,Edific,sparse = TRUE)

b <- as.data.frame(a)

## Renomeia colunas.

colnames(b) <- c('Contem','Contido')

## Remove registros onde contem e contido sao iguais.

c <- b[b$Contem != b$Contido,]

## Pega altura dos edificios.

c <- merge(x = c,
y = unique(Edific[,c("id", "height")]),
by.x = "Contem",
by.y = "id",
all.x=TRUE) 

c <- c[,1:3]

colnames(c) <- c("Contem","Contido","AltContem")

c <- merge(x = c,
           y = unique(Edific[,c("id", "height")]),
           by.x = "Contido",
           by.y = "id",
           all.x=TRUE) 

c <- c[,1:4]

## Renomeia colunas.

colnames(c) <- c("Contem","Contido","AltContem","AltContido")

## Define a frequencia que cada objeto esta contido.
## Quanto mais contido esta um objeto, 
## a tendencia eh que ele esteja sobreposto a mais objetos.
## Define a diferenca de altura entre o objeto contido e o obj que o contem.
## Define a ordem considerando a frequencia com que o objeto esta contido
## (objetos menos contidos estao sobrepostos a menos objetos, 
## logo layer deve ser menor).
## Define a ordem tambem considerando a dif de altura entre contido e contem.
## Quanto maior a diferenca de altura, mais provavel que haja outro objeto 
## entre contido e contem. Definindo a ordem considerando a diferenca de altura,
## tende-se a acrescentar os layers de maneira mais correta.

c <- c %>% 
  group_by(Contido) %>% 
  mutate(FreqContido = n()) %>% 
  mutate(DifAltura = AltContido-AltContem) %>% 
  arrange(FreqContido,DifAltura)

## Define todos como building = yes. Eh revertido posteriormente no codigo.

Edific$building <- "yes"

## Inicializa variavel building:part.

Edific$`building:part` <- NULL

## Cria variavel altura, pois ha diferencas considerando altura e elevacao.

Edific$altura <- Edific$ele + Edific$height

## Se altura do contido for maior que altura do contem, e layer do contido
## for menor ou igual a layer do contem, layer do contido recebe layer 
## do contem mais um.
## Se edificio esta contido, ele deve ser um building part.

## (Em alguns casos, o edificio esta sobre uma base baixa (ex.: edificio de 
## 40 metros de altura sobre uma laje de 5 metros de altura). Nestes casos,
## o edificio deve ser considerado building tambem. Enquanto nao for encontrada
## solucao para implementar isto via codigo, ajustar manualmente no JOSM.)

for (j in 1:10){
  for (i in 1:nrow(c)){
    f <- c$Contido[i]
    g <- c$Contem[i]
    if (Edific$altura[Edific$id==f]>Edific$altura[Edific$id ==g]){
      if (Edific$layer[Edific$id==f]<=Edific$layer[Edific$id==g]){
        Edific$layer[Edific$id==f] <- Edific$layer[Edific$id==g]+1
        Edific$`building:part`[Edific$id==f] <- "yes"
      }
    }
  }
}  

## Se buiding:part = sim, building = n?o.
## Se layer = 0, remover layer.

Edific <- Edific %>% 
  rowwise() %>% 
  mutate(building = case_when(`building:part` == "yes" ~ "",
                              is.na(`building:part`) ~ "yes")) %>% 
  mutate(layer = ifelse(layer == 0,NA,layer))

## Transforma layer em numero inteiro.

Edific$layer <- as.integer(Edific$layer)
Edific$source <- "data.rio"

## Seleciona colunas utilizadas no OSM.

Edific <- subset(Edific, select=c(height,ele,layer,`IPP:CodEdificio`,
                                  building,`building:part`, source))

Edific <- st_simplify(Edific, preserveTopology = TRUE, 
                      dTolerance = 0.1)

Edific <- Edific %>% 
  filter(height>2.5)

## Salva como geojson. Se salvar como shp perde o nome das colunas, que tem 
## limite de caracteres.

st_write(Edific, paste0("./ed_selecionado_proc.geojson"), append = F)

