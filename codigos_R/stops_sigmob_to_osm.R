pegarDadoSIGMOB("stops")

bairro <- "Botafogo"

stops_sppo <- stops %>%
  filter(idModalSmtr == "22") %>%
  filter(Bairro == bairro)

stops_sppo <- st_as_sf(stops_sppo,coords=c("stop_lon","stop_lat"),crs = 4326, na.fail = T)


stops_sppo_osm <- stops_sppo %>%
  select(stop_name,stop_id,IDTipoSinalizacao,IDTipoAbrigo,IDTipoAssento,
         IDLixeiras,PontoExistente,piso_tatil,IDRampa) %>%
  rename(name = stop_name,
         `gtfs:stop_id` = stop_id) %>%
  mutate(highway = "bus_stop",
         public_transport = "platform",
         shelter = ifelse(IDTipoAbrigo==0,"no","yes"),
         bench = ifelse(IDTipoAssento==0,"no","yes"),
         tactile_paving = ifelse(piso_tatil==3|piso_tatil==4,"yes","no"),
         wheelchair = ifelse(IDRampa==2|piso_tatil==3,"yes","no"),
         bin = ifelse(IDLixeiras==1,"no","yes"),
         traffic_sign = ifelse(IDTipoSinalizacao==2|IDTipoSinalizacao==3,"BR:SAU-26",""),
         advertising = ifelse(IDTipoAbrigo==1|IDTipoAbrigo==2,"yes","no")) %>%
  select(name,`gtfs:stop_id`,highway,public_transport,shelter,bench,tactile_paving,
         wheelchair,bin,traffic_sign,advertising)

st_write(stops_sppo_osm,"D:/Edificacoes_2013/bairros/",bairro,"/paradas_onibus_",bairro,"_PODE-SUBIR.geojson")
