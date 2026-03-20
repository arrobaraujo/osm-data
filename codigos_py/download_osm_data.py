import osmnx as ox
import geopandas as gpd
import pandas as pd
import argparse
import os
import json

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
        # Download features using osmnx
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
