"""
Módulo de Utilidades para Análise de Cafeterias em Fortaleza

Este módulo contém funções auxiliares organizadas em grupos funcionais:
- Classificação e processamento de dados
- Análise espacial (Voronoi)
- Visualização de mapas interativos

Autor: Projeto Mestrado Unifor - Análise Urbana de Fortaleza
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import folium
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, Point, MultiPolygon
from shapely.ops import unary_union
import os


# ============================================================================
# GRUPO 1: CLASSIFICAÇÃO E PROCESSAMENTO DE DADOS
# ============================================================================

def classifica_cafe(row):
    """
    Classifica um estabelecimento como café com base em suas tags OSM.
    
    Parâmetros:
    -----------
    row : pd.Series
        Linha do DataFrame com dados do estabelecimento
        
    Retorna:
    --------
    str : 'alta', 'media' ou 'baixa' confiança
    
    Critérios:
    ----------
    - Alta: amenity=cafe, shop=coffee, cuisine=cafe/coffee_shop
    - Média: shop=bakery, cuisine=bakery/breakfast, nome contém 'cafe'/'coffee'
    - Baixa: outros casos
    """
    # Alta confiança: tag muito específica
    if (row.get('amenity') == 'cafe' or 
        row.get('shop') == 'coffee' or 
        row.get('cuisine') in ['cafe', 'coffee_shop']):
        return 'alta'
    
    # Média confiança: tags relacionadas ou nome sugestivo
    nome = str(row.get('name', '')).lower()
    if (row.get('shop') in ['bakery', 'confectionery'] or
        row.get('cuisine') in ['bakery', 'breakfast', 'dessert'] or
        any(termo in nome for termo in ['cafe', 'coffee', 'cafeteria', 'espresso', 'café'])):
        return 'media'
    
    # Baixa confiança
    return 'baixa'


def geojson_to_csv(gdf, output_csv_path, include_geometry=True):
    """
    Converte um GeoDataFrame em arquivo CSV.
    
    Parâmetros:
    -----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame a ser convertido
    output_csv_path : str
        Caminho do arquivo CSV de saída
    include_geometry : bool, default=True
        Se True, inclui geometria como WKT
        
    Retorna:
    --------
    None
    """
    df = gdf.copy()
    
    if include_geometry and 'geometry' in df.columns:
        # Converter geometria para WKT (Well-Known Text)
        df['geometry_wkt'] = df['geometry'].apply(lambda geom: geom.wkt if geom else None)
        df = df.drop(columns=['geometry'])
    
    # Criar diretório de saída se não existir
    output_dir = os.path.dirname(output_csv_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Salvar como CSV
    df.to_csv(output_csv_path, index=False, encoding='utf-8')
    print(f"✓ CSV salvo em: {output_csv_path}")


# ============================================================================
# GRUPO 2: ANÁLISE ESPACIAL
# ============================================================================

def calcular_voronoi(cafe_coords, boundary_gdf):
    """
    Calcula polígonos de Voronoi para as coordenadas dos cafés.
    
    Parâmetros:
    -----------
    cafe_coords : np.ndarray
        Array (N, 2) com coordenadas [lon, lat] dos cafés
    boundary_gdf : gpd.GeoDataFrame
        GeoDataFrame com a geometria de limite da área de estudo
        
    Retorna:
    --------
    gpd.GeoDataFrame
        GeoDataFrame com polígonos de Voronoi recortados ao limite
    """
    # Calcular Voronoi
    vor = Voronoi(cafe_coords)
    
    # Criar união dos polígonos de limite
    boundary = unary_union(boundary_gdf.geometry)
    
    # Converter regiões de Voronoi em polígonos
    voronoi_polygons = []
    
    for region_index in vor.point_region:
        region = vor.regions[region_index]
        
        if not region or -1 in region:
            # Região infinita ou inválida
            continue
        
        # Criar polígono a partir dos vértices
        polygon_coords = [vor.vertices[i] for i in region]
        polygon = Polygon(polygon_coords)
        
        # Recortar ao limite da área de estudo
        clipped_polygon = polygon.intersection(boundary)
        
        if not clipped_polygon.is_empty:
            voronoi_polygons.append(clipped_polygon)
    
    # Criar GeoDataFrame
    geo_voronoi = gpd.GeoDataFrame(
        geometry=voronoi_polygons,
        crs=boundary_gdf.crs
    )
    
    return geo_voronoi


# ============================================================================
# GRUPO 3: VISUALIZAÇÃO
# ============================================================================

def criar_mapa_base(center_lat, center_lon, zoom_start=12, tiles='OpenStreetMap'):
    """
    Cria um mapa Folium base.
    
    Parâmetros:
    -----------
    center_lat : float
        Latitude do centro do mapa
    center_lon : float
        Longitude do centro do mapa
    zoom_start : int, default=12
        Nível de zoom inicial
    tiles : str, default='OpenStreetMap'
        Estilo de tiles do mapa
        
    Retorna:
    --------
    folium.Map
        Objeto de mapa Folium (pode ser exibido inline em notebooks)
    """
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles=tiles
    )
    return m


def adicionar_marcadores_cafes(mapa, cafes_gdf, popup_cols=None):
    """
    Adiciona marcadores de cafés ao mapa.
    
    Parâmetros:
    -----------
    mapa : folium.Map
        Mapa Folium
    cafes_gdf : gpd.GeoDataFrame
        GeoDataFrame com dados dos cafés
    popup_cols : list, optional
        Colunas a exibir no popup (padrão: ['name', 'confianca_cafe'])
        
    Retorna:
    --------
    folium.Map
        Mapa com marcadores adicionados (modificado in-place)
    """
    if popup_cols is None:
        popup_cols = ['name', 'confianca_cafe']
    
    for idx, row in cafes_gdf.iterrows():
        if row.geometry and row.geometry.geom_type == 'Point':
            # Criar popup com informações
            popup_text = "<br>".join([
                f"<b>{col}:</b> {row.get(col, 'N/A')}" 
                for col in popup_cols if col in row.index
            ])
            
            # Definir cor por confiança
            cor = {
                'alta': 'green',
                'media': 'orange',
                'baixa': 'red'
            }.get(row.get('confianca_cafe', 'baixa'), 'gray')
            
            folium.Marker(
                location=[row.geometry.y, row.geometry.x],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=row.get('name', 'Café'),
                icon=folium.Icon(color=cor, icon='coffee', prefix='fa')
            ).add_to(mapa)
    
    return mapa
