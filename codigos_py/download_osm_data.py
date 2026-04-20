import osmnx as ox
import geopandas as gpd
import pandas as pd
import argparse
import os
import json
import requests
from shapely.geometry import LineString, MultiLineString, Point, shape

def get_predefined_tags(category):
    """
    Retorna um dicionário de tags OSM para uma categoria específica.
    Categorias: 'stops', 'routes', 'cycling', 'corridors', 'all'.
    """
    categories = {
        "stops": {
            "highway": "bus_stop",
            "amenity": ["bus_station", "ferry_terminal"],
            "public_transport": ["platform", "stop_position", "station"],
            "railway": ["station", "stop", "tram_stop"],
        },
        "routes": {
            "route": ["bus", "train", "subway", "light_rail", "tram", "ferry"],
            "route_master": ["bus", "train", "subway", "light_rail", "tram", "ferry"],
            "type": ["route", "route_master"],
        },
        "cycling": {
            "highway": ["cycleway"],
            "route": ["bicycle"],
            "cycleway": True,
            "cycleway:both": True,
            "cycleway:left": True,
            "cycleway:right": True,
            "bicycle": ["yes", "designated"],
        },
        "corridors": {
            "highway": ["busway"],
            "busway": True,
        }
    }
    
    if category == "all":
        # Mescla todas as categorias
        all_tags = {}
        for cat in categories.values():
            for k, v in cat.items():
                if k in all_tags:
                    if isinstance(all_tags[k], list) and isinstance(v, list):
                        all_tags[k] = list(set(all_tags[k] + v))
                    elif all_tags[k] is True or v is True:
                        all_tags[k] = True
                else:
                    all_tags[k] = v
        return all_tags
    
    return categories.get(category, {})

def download_osm_transport_data(place_name, output_base, category="all", custom_tags=None):
    """
    Baixa dados de transporte do OpenStreetMap.
    """
    # Define as tags
    if custom_tags:
        try:
            tags = json.loads(custom_tags)
        except json.JSONDecodeError:
            print("Erro: tags customizadas devem estar em formato JSON (ex: '{\"highway\":\"bus_stop\"}')")
            return
    else:
        tags = get_predefined_tags(category)
    
    print(f"Buscando dados ({category}) para: {place_name}...")
    try:
        # Verifica se estamos baixando rotas para usar uma query mais robusta que pegue relações
        if category == "routes" or (isinstance(tags, dict) and tags.get("type") == ["route", "route_master"]):
            print(f"Utilizando modo de recuperação de relações para rotas...")
            
            # Obtém a geometria da área para filtrar a query
            area_gdf = ox.geocode_to_gdf(place_name)
            if area_gdf.empty:
                raise ValueError(f"Não foi possível geocodificar o local: {place_name}")
            
            # Constrói query Overpass customizada com 'out geom' para pegar geometrias de relações
            # Filtramos por rotas de transporte público (route ou route_master)
            tag_values = "|".join(tags.get("route", ["bus", "train", "subway", "light_rail", "tram", "ferry"]))
            
            # Obtém os limites da área (bounding box)
            bounds = area_gdf.total_bounds # [minx, miny, maxx, maxy]
            
            # Query que busca tanto 'route' quanto 'route_master'
            overpass_query = f"""
            [out:json][timeout:90];
            (
              relation["route"~"{tag_values}"]({bounds[1]},{bounds[0]},{bounds[3]},{bounds[2]});
              relation["route_master"~"{tag_values}"]({bounds[1]},{bounds[0]},{bounds[3]},{bounds[2]});
            );
            out geom;
            """
            
            # Faz a requisição bruta usando requests
            # Usamos o endpoint de ox.settings.overpass_url ou o padrão
            url = f"{ox.settings.overpass_url.rstrip('/')}/interpreter"
            print(f"Enviando consulta para {url}...")
            
            headers = {'User-Agent': ox.settings.http_user_agent}
            response = requests.post(url, data={'data': overpass_query}, headers=headers, timeout=120)
            
            data = response.json()
            elements = data.get('elements', [])
            print(f"Overpass retornou {len(elements)} elementos.")
            
            features = []
            for el in elements:
                tags = el.get('tags', {})
                geom = None
                
                if el.get('type') == 'relation' and 'members' in el:
                    # Reconstrói a rota a partir dos membros que tenham geometria (out geom)
                    lines = []
                    for member in el['members']:
                        if 'geometry' in member and len(member['geometry']) >= 2:
                            coords = [(m['lon'], m['lat']) for m in member['geometry']]
                            lines.append(LineString(coords))
                    
                    if lines:
                        geom = MultiLineString(lines)
                
                elif el.get('type') == 'way' and 'geometry' in el:
                    coords = [(m['lon'], m['lat']) for m in el['geometry']]
                    if len(coords) >= 2:
                        geom = LineString(coords)
                
                elif el.get('type') == 'node' and 'lat' in el and 'lon' in el:
                    geom = Point(el['lon'], el['lat'])
                
                if geom:
                    feat_data = {
                        'osmid': el.get('id'),
                        'element_type': el.get('type'),
                        'geometry': geom
                    }
                    feat_data.update(tags)
                    features.append(feat_data)
            
            if not features:
                print("Nenhum elemento com geometria foi encontrado nos dados retornados.")
                return
                
            gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")
            
            # Filtro espacial manual para garantir que estamos dentro da área (opcional, mas recomendado)
            # gdf = gdf[gdf.intersects(area_gdf.geometry.iloc[0])]
            
        else:
            # Download features usando o método padrão do osmnx
            gdf = ox.features_from_place(place_name, tags=tags)
        
        if gdf.empty:
            print(f"Nenhum dado encontrado para '{place_name}' com os filtros fornecidos.")
            return

        print(f"Encontrados {len(gdf)} elementos.")

        # Garante que o diretório de saída existe
        output_dir = os.path.dirname(output_base)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 1. Salva como GeoJSON
        geojson_path = f"{output_base}.geojson"
        gdf.to_file(geojson_path, driver="GeoJSON")
        print(f"Salvo: {geojson_path}")

        # 2. Salva como Geopackage
        gpkg_path = f"{output_base}.gpkg"
        gdf.to_file(gpkg_path, driver="GPKG")
        print(f"Salvo: {gpkg_path}")

        # 3. Salva como CSV (com tratamento de geometria)
        csv_path = f"{output_base}.csv"
        df_csv = gdf.copy()
        df_csv['geometry_type'] = df_csv.geometry.type
        
        if 'geometry' in df_csv.columns:
            # Extrai lat/lon apenas para pontos
            is_point = df_csv.geometry.type == 'Point'
            if is_point.any():
                df_csv.loc[is_point, 'latitude'] = df_csv.loc[is_point].geometry.y
                df_csv.loc[is_point, 'longitude'] = df_csv.loc[is_point].geometry.x
            
            # Adiciona WKT para geometrias não-pontuais
            is_not_point = ~is_point
            if is_not_point.any():
                df_csv.loc[is_not_point, 'wkt_geometry'] = df_csv.loc[is_not_point].geometry.apply(lambda g: g.wkt)
            
            # Remove coluna geometry para o CSV básico
            df_csv = pd.DataFrame(df_csv.drop(columns='geometry'))
            
        df_csv.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"Salvo: {csv_path}")

    except Exception as e:
        print(f"Erro ao processar dados: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Baixa dados de transporte e mobilidade do OpenStreetMap.")
    parser.add_argument("--place", type=str, default="Rio de Janeiro", help="Nome do local")
    parser.add_argument("--output", type=str, default="osm_data", help="Caminho base para salvar arquivos (ex: 'pasta/nome_arquivo')")
    parser.add_argument("--category", type=str, default="all", choices=["stops", "routes", "cycling", "corridors", "all"], help="Categoria de dados")
    parser.add_argument("--tags", type=str, default=None, help="Tags customizadas em formato JSON (ex: '{\"highway\":\"path\"}')")
    
    args = parser.parse_args()
    
    download_osm_transport_data(args.place, args.output, args.category, args.tags)
