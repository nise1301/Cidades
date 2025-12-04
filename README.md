# Projeto: Mapeamento e Otimização da Distribuição de Cafés em Fortaleza

## 📋 Descrição

Sabe aquela vontade de tomar um café e você se pergunta: "será que tem algum perto daqui?" 🤔☕ 

Este projeto nasceu dessa curiosidade! Analisei a distribuição espacial de cafés em Fortaleza usando dados do OpenStreetMap e do censo IBGE 2022. Utilizei **diagramas de Voronoi** para mapear as áreas de influência de cada café, calculei a acessibilidade com base na densidade populacional, e testei se a distribuição segue o modelo de **Gastner & Newman (2006)** — que prevê como facilidades urbanas deveriam estar distribuídas para minimizar nossos deslocamentos.

**A pergunta central:** Os cafés de Fortaleza estão distribuídos de forma eficiente, ou seguem apenas a lógica de mercado (mais gente = mais cafés)?

**Spoiler:** Descobrimos que o mercado prioriza igualdade per capita (α ≈ 1.0) em vez de eficiência de deslocamento (α ≈ 2/3). Ou seja: há mais cafés onde há mais pessoas, mas não necessariamente nos lugares que minimizariam suas caminhadas!

## 📁 Estrutura do Projeto

```
Cidades/
├── projeto_cidades_cafes.ipynb           # Notebook principal com análises completas
├── utils.py                               # Funções auxiliares modulares
├── README.md                              # Este arquivo
├── requirements.txt                       # Dependências do projeto
├── distribuição optima de facilidades cidades.pdf  # Referência teórica
│
├── data/                                  # Dados de entrada
│   ├── dados_cafe.geojson                # Dados de cafés (OpenStreetMap)
│   └── Setores_Censitários_2022.csv      # Dados censitários IBGE 2022
│
└── outputs/                               # Resultados processados (gitignored)
    ├── cafes_classificados.csv           # Cafés com classificação de confiança
    ├── cafes_classificados.geojson       # Versão geoespacial
    ├── cafes_com_setor.geojson           # Cafés com setor censitário associado
    ├── geo_pop_processed.csv             # Setores censitários processados
    ├── geo_pop_processed.geojson         # Versão geoespacial
    ├── voronoi_regions.geojson           # Polígonos de Voronoi
    ├── voronoi_com_populacao.geojson     # Voronoi com dados populacionais
    ├── acessibilidade_cafes_stats.csv    # Estatísticas de acessibilidade
    ├── distribuicao_confianca.png        # Gráfico de distribuição de confiança
    ├── cafes_por_bairro.png              # Distribuição espacial por bairro
    ├── scaling_law_analysis.png          # Análise de lei de escala
    └── inequality_analysis.png           # Curva de Lorenz e Gini
```

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Principais bibliotecas:**
- `pandas >= 2.0.0` e `numpy >= 1.24.0` - Manipulação de dados
- `geopandas >= 0.14.0` e `shapely >= 2.0.0` - Análise geoespacial
- `folium >= 0.15.0` - Mapas interativos
- `scipy >= 1.10.0` - Análise espacial (Voronoi)
- `matplotlib >= 3.7.0` e `seaborn >= 0.12.0` - Visualizações

### 2. Preparar Dados

#### 2.1. Dados Censitários
- `Setores_Censitários_2022.csv` - Dados censitários de Fortaleza (IBGE 2022)

#### 2.2. Dados de Cafés (OpenStreetMap)

Você pode obter os dados atualizados de cafés usando a **Overpass API** do OpenStreetMap:

**Opção 1: Usar o Overpass Turbo (Interface Web)**

1. Acesse [https://overpass-turbo.eu/](https://overpass-turbo.eu/)
2. Cole a seguinte consulta Overpass QL:

```overpass
[out:json][timeout:25];
{{geocodeArea:Fortaleza}}->.searchArea;
(
  node["amenity"~"cafe|restaurant"](area.searchArea);
  way["amenity"~"cafe|restaurant"](area.searchArea);
  relation["amenity"~"cafe|restaurant"](area.searchArea);
  
  node["shop"~"coffee|bakery|confectionery"](area.searchArea);
  way["shop"~"coffee|bakery|confectionery"](area.searchArea);
  relation["shop"~"coffee|bakery|confectionery"](area.searchArea);
  
  node["cuisine"~"cafe|coffee_shop|bakery|breakfast|dessert|confectionery"](area.searchArea);
  way["cuisine"~"cafe|coffee_shop|bakery|breakfast|dessert|confectionery"](area.searchArea);
  relation["cuisine"~"cafe|coffee_shop|bakery|breakfast|dessert|confectionery"](area.searchArea);
  
  node[name~"cafe|coffee|cafeteria|expresso"](area.searchArea);
  way[name~"cafe|coffee|cafeteria|expresso"](area.searchArea);
  relation[name~"cafe|coffee|cafeteria|expresso"](area.searchArea);
);
out center;
```

3. Clique em "Executar" (Run)
4. Exporte como GeoJSON: Menu "Exportar" → "GeoJSON"
5. Salve como `data/dados_cafe.geojson`

**Opção 2: Usar arquivo fornecido**
- Use o arquivo `dados_cafe.geojson` já incluído na pasta `data/`

> **Nota**: A consulta busca estabelecimentos com tags relacionadas a cafés, padarias, confeitarias e restaurantes que possam servir café. O sistema de classificação do projeto (`utils.py`) filtra e categoriza esses estabelecimentos por nível de confiança.

### 3. Executar o Notebook

Abra `projeto_cidades_cafes.ipynb` no Jupyter e execute as células sequencialmente.

### 4. Visualizar Resultados

- **Mapas interativos**: Exibidos diretamente no notebook (inline)
- **Dados processados**: Arquivos CSV/GeoJSON na pasta `outputs/`
- **Gráficos**: Imagens PNG na pasta `outputs/`

## 📊 Análises Realizadas

### 1. Classificação de Cafés
Classificação automática baseada em tags OSM:
- **Alta confiança**: `amenity=cafe`, `shop=coffee`, `cuisine=cafe/coffee_shop`
- **Média confiança**: `shop=bakery`, nome contém "café/coffee"
- **Baixa confiança**: outros casos

### 2. Análise Espacial com Voronoi
- Geração de polígonos de Voronoi para cada café
- Agregação de população por região de influência
- Cálculo de pessoas por café em cada região

### 3. Análise de Acessibilidade
- Estatísticas de cobertura populacional
- Identificação de áreas com baixa acessibilidade
- Visualização de desigualdade na distribuição

### 4. Análise de Desigualdade
- Curva de Lorenz para distribuição de cafés
- Cálculo do coeficiente de Gini
- Comparação com distribuição igualitária

### 6. Visualizações Interativas
Mapa Folium com múltiplas camadas:
- Marcadores de cafés (coloridos por confiança)
- Polígonos de Voronoi
- Choropleth de densidade populacional
- Controle de camadas interativo

## 🔧 Funções Principais (utils.py)

### Grupo 1: Classificação e Processamento
- **`classifica_cafe(row)`**: Classifica estabelecimentos por nível de confiança
- **`geojson_to_csv(gdf, output_csv_path)`**: Converte GeoDataFrame para CSV

### Grupo 2: Análise Espacial
- **`calcular_voronoi(cafe_coords, boundary_gdf)`**: Gera polígonos de Voronoi recortados

### Grupo 3: Visualização
- **`criar_mapa_base(center_lat, center_lon)`**: Cria mapas Folium base
- **`adicionar_marcadores_cafes(mapa, cafes_gdf)`**: Adiciona marcadores coloridos ao mapa

## 🔍 Principais Achados

### Distribuição de Cafés
- **Total de estabelecimentos analisados**: ~600 pontos do OpenStreetMap
- **Distribuição por confiança** (baseado em tags OSM):
  - **Baixa confiança: 77.51%** - Estabelecimentos com tags genéricas ou ambíguas. Estão presentes nesse estudo por que, embora não sejam serviços especializados em cafés, muitos deles possuem esse produto e indexaram no OpenStreetMap por essa razão.
  - **Média/Alta confiança: 22.49%** - Estabelecimentos com tags específicas de café.
- **Concentração espacial**: Forte concentração em áreas centrais e bairros nobres

### Acessibilidade
- **Desigualdade na distribuição**: Coeficiente de Gini indica distribuição desigual
- **Áreas carentes**: Periferias com baixa densidade de cafés
- **Pessoas por café**: Variação significativa entre regiões de Voronoi.

### O Problema da Localização Ótiman e a Lei de Potência 2/3: O Padrão de Eficiência

O modelo teórico de **Gastner & Newman (2006)** estabelece que a distribuição ótima de facilidades segue:

$$D(r) \propto \rho(r)^{2/3}$$

Onde o expoente **α = 2/3** representa o ótimo que minimiza deslocamentos. Este valor sugere uma distribuição mais concentrada em áreas densas, mas garantindo serviço razoável a todos.

### Metodologia Aplicada

**A. Tesselação de Voronoi**
- Particionamento do espaço em células de influência
- Quantificação da densidade local de facilidades
- Associação entre população (demanda) e cafés (oferta)

**B. Regressão Log-log**
- Plotagem de densidade de cafés vs. densidade populacional
- Cálculo do expoente α através do *slope* da regressão
- Comparação com o ótimo teórico (α = 2/3)

### Resultados: Fortaleza vs. Modelo Teórico

**Expoente encontrado: α = 0.964**

Este valor, próximo de **α = 1.0**, indica que a distribuição de cafés em Fortaleza segue um padrão de **proporcionalidade linear** à população, diferente do ótimo teórico:

| Cenário | Expoente α | Interpretação |
|---------|-----------|---------------|
| **Otimização (Gastner & Newman)** | ~0.667 | Minimiza deslocamento médio |
| **Fortaleza (observado)** | **0.964** | Proporcional à população local |
| **Proporcionalidade pura** | 1.0 | Igualdade per capita |

### Interpretação

A distribuição observada sugere que o mercado de cafés em Fortaleza prioriza:
- **Igualdade per capita**: Mais cafés onde há mais pessoas
- **Demanda local**: Distribuição proporcional à população
- **Não otimização de deslocamento**: Diferente do modelo de eficiência espacial

Isso indica que forças de mercado favorecem a "justeza" de servir proporcionalmente à população (α ≈ 1.0), em vez da minimização de distâncias de viagem (α ≈ 2/3).

### Implicações

- A distribuição atual atende à demanda local, mas pode não ser ótima para minimizar deslocamentos
- Áreas com alta densidade populacional têm proporcionalmente mais cafés
- O padrão difere do observado por Gastner e Newman para facilidades públicas nos EUA (α = 0.663 ± 0.002). Pode ser um reflexo de questões regionais, mas também pode estar associado a um desconhecimento do problema de localização ótima e de como isso afeta a distribuição de serviços e consequentemente, a qualidade de vida das pessoas. Seria o caso de disseminar a palavra de Gastner e Newman para a cidade de Fortaleza? Não percam os próximos capitulos!

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **Jupyter Notebook**
- **Bibliotecas principais**: pandas, geopandas, folium, scipy, matplotlib, seaborn

## 👤 Denise Ramos Soares

Projeto desenvolvido para a disciplina de Ciência de Dados Aplicada a Cidades, ministrada pelo professor Hygor Piaget, no curso de Mestrado em Informática Aplicada Unifor

## 📝 Licença

- Dados do OpenStreetMap sob licença **ODbL**
- Dados censitários IBGE de domínio público
- Código do projeto: uso acadêmico
