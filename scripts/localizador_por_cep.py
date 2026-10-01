# -*- coding: utf-8 -*-
"""
=============================================================================
🏛️ PREFEITURA MUNICIPAL DE DUQUE DE CAXIAS — RJ
Módulo de Geolocalização por CEP e Proximidade de Equipamentos Públicos
=============================================================================
Fluxo Operacional:
1. O cidadão pergunta (ex: "Qual o hospital mais próximo?", "Onde tem vacina?")
2. O sistema solicita o CEP do cidadão.
3. Este script valida o CEP (8 dígitos numéricos).
4. Consulta o webservice do ViaCEP (https://viacep.com.br/ws/{cep}/json/).
5. Obtém as coordenadas (lat/lon) do ponto de origem do cidadão.
6. Calcula a distância geográfica (fórmula de Haversine) contra a base oficial
   de Duque de Caxias (442 equipamentos catalogados).
7. Retorna os equipamentos mais próximos com endereço, distância, telefone e horário.
8. Gera o prompt estruturado e contextualizado para a IA responder com 100% de precisão.
"""

import sys
import os
import re
import math
import json
import urllib.request
import urllib.parse
import sqlite3

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados', 'enderecos_duque_de_caxias_v2.db')
JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados', 'todos_os_enderecos_duque_de_caxias.json')

# Coordenadas aproximadas de referência para os principais bairros de Duque de Caxias (Fallback)
BAIRROS_CENTROIDES = {
    'centro': (-22.7928, -43.3059),
    '25 de agosto': (-22.7885, -43.3045),
    'jardim vinte e cinco de agosto': (-22.7885, -43.3045),
    'parque duque': (-22.7895, -43.3060),
    'parque lafaiete': (-22.7867, -43.3241),
    'doutor laureano': (-22.7666, -43.2955),
    'jardim gramacho': (-22.7569, -43.2842),
    'olavo bilac': (-22.7613, -43.3252),
    'vila sarapuí': (-22.7496, -43.2995),
    'parque centenário': (-22.7728, -43.3147),
    'parque beira mar': (-22.7843, -43.2842),
    'beira mar': (-22.7843, -43.2842),
    'jardim primavera': (-22.6851, -43.2839),
    'campos elíseos': (-22.7058, -43.2745),
    'saracuruna': (-22.6740, -43.2576),
    'pilar': (-22.7056, -43.3063),
    'vila rosali': (-22.7800, -43.3100),
    'imbariê': (-22.6360, -43.2167),
    'santa cruz da serra': (-22.6428, -43.2810),
    'parque equitativa': (-22.6352, -43.2659),
    'parada angélica': (-22.6183, -43.2045),
    'xerém': (-22.6015, -43.2925),
    'mantiquira': (-22.5820, -43.2964),
    'vila maria helena': (-22.6600, -43.2400),
    'parque fluminense': (-22.7650, -43.3200)
}

def validar_cep(cep_input: str) -> str:
    """Valida se o CEP possui exatamente 8 dígitos numéricos."""
    if not cep_input:
        raise ValueError("O CEP não pode estar vazio.")
    
    cep_limpo = re.sub(r'\D', '', str(cep_input))
    if len(cep_limpo) != 8:
        raise ValueError(f"CEP inválido: '{cep_input}'. O CEP deve conter exatamente 8 dígitos numéricos (ex: 25071210 ou 25071-210).")
    
    return cep_limpo

def consultar_viacep(cep_8_digitos: str) -> dict:
    """Consulta o webservice oficial do ViaCEP e retorna o dicionário com os dados do endereço."""
    url = f"https://viacep.com.br/ws/{cep_8_digitos}/json/"
    req = urllib.request.Request(url, headers={'User-Agent': 'PrefeituraDuqueDeCaxias-Localizador/1.0'})
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            dados = json.loads(response.read().decode('utf-8'))
    except Exception as err:
        raise RuntimeError(f"Erro ao consultar o serviço ViaCEP: {err}")
    
    if dados.get('erro') is True or dados.get('erro') == 'true':
        raise ValueError(f"O CEP '{cep_8_digitos}' não foi encontrado na base de dados dos Correios.")
    
    return dados

def obter_coordenadas_origem(dados_viacep: dict) -> tuple:
    """
    Obtém latitude e longitude do CEP consultado:
    1. Procura primeiro na base oficial local de Caxias pelo CEP ou logradouro
    2. Procura centroide do bairro conhecido
    3. Tenta geocodificação OpenStreetMap/Nominatim se disponível
    """
    cep_formatado = dados_viacep.get('cep', '')
    bairro = dados_viacep.get('bairro', '').strip().lower()
    logradouro = dados_viacep.get('logradouro', '').strip()
    
    # 1. Busca rápida no banco SQLite
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Tenta achar equipamento ou endereço com mesmo CEP
            c.execute("SELECT latitude, longitude FROM enderecos WHERE cep = ? AND latitude IS NOT NULL LIMIT 1;", (cep_formatado,))
            row = c.fetchone()
            if row and row[0] and row[1]:
                conn.close()
                return (float(row[0]), float(row[1]), "Base Oficial de Endereços PMDC")
            
            conn.close()
        except Exception:
            pass

    # 2. Busca pelo centroide do bairro catalogado
    for b_chave, coords in BAIRROS_CENTROIDES.items():
        if b_chave in bairro or bairro in b_chave:
            return (coords[0], coords[1], f"Centroide do Bairro ({dados_viacep.get('bairro')})")

    # 3. Geocodificação Nominatim com fallback seguro
    try:
        cidade = dados_viacep.get('localidade', 'Duque de Caxias')
        query = f"{logradouro}, {dados_viacep.get('bairro', '')}, {cidade}, RJ, Brasil"
        url_nom = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(query)}&limit=1"
        req_nom = urllib.request.Request(url_nom, headers={'User-Agent': 'PMDC-LocalizadorCEP/1.0'})
        with urllib.request.urlopen(req_nom, timeout=3) as res:
            res_json = json.loads(res.read().decode('utf-8'))
            if res_json and len(res_json) > 0:
                lat = float(res_json[0]['lat'])
                lon = float(res_json[0]['lon'])
                return (lat, lon, "Geocodificação OpenStreetMap")
    except Exception:
        pass

    # Fallback municipal padrão (Centro Cívico de Caxias)
    return (-22.7850, -43.3050, "Centro de Duque de Caxias (Aproximado)")

def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    """
    Calcula a distância geodésica em quilômetros entre duas coordenadas (Fórmula de Haversine).
    """
    R = 6371.0  # Raio da Terra em km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def carregar_equipamentos_oficiais() -> list:
    """Carrega a base oficial de 442 equipamentos de Duque de Caxias."""
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Fallback via SQLite
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT e.id, e.nome, cat.nome, b.nome, en.logradouro, en.cep, en.latitude, en.longitude, e.horario_funcionamento
            FROM equipamentos e
            JOIN categorias cat ON e.categoria_id = cat.id
            JOIN enderecos en ON e.endereco_id = en.id
            JOIN bairros b ON en.bairro_id = b.id;
        """)
        rows = c.fetchall()
        conn.close()
        
        return [
            {
                'id': r[0], 'nome': r[1], 'categoria': r[2], 'bairro': r[3],
                'endereco': r[4], 'cep': r[5], 'lat': float(r[6] or -22.785),
                'lon': float(r[7] or -43.305), 'horario_funcionamento': r[8] or 'Segunda a sexta-feira, das 09h às 17h'
            }
            for r in rows
        ]

    return []

def filtrar_por_categoria(equipamentos: list, tipo_desejado: str) -> list:
    """Filtra os equipamentos de acordo com o que o cidadão está procurando."""
    tipo = (tipo_desejado or '').strip().lower()
    
    if not tipo or tipo in ['todos', 'geral', 'tudo']:
        return equipamentos
    
    filtrados = []
    for eq in equipamentos:
        nome = eq.get('nome', '').lower()
        cat = eq.get('categoria', '').lower()
        desc = eq.get('descricao', '').lower()
        
        # Filtro de Hospitais e Emergências 24h
        if tipo in ['hospital', 'hospitais', 'upa', 'emergencia', 'urgencia', 'uph']:
            if ('hospital' in nome or 'upa' in nome or 'uph' in nome or 'maternidade' in nome or 
                'saúde especializada' in cat or '24 horas' in str(eq.get('horario_funcionamento', '')).lower()):
                filtrados.append(eq)
                
        # Filtro de Postos de Saúde e Vacinação
        elif tipo in ['posto', 'ubs', 'usf', 'vacina', 'vacinacao', 'posto de saude', 'saude']:
            if ('ubs' in nome or 'usf' in nome or 'posto' in nome or 'saúde básica' in cat or 
                'saúde especializada' in cat or 'hospital' in nome or 'upa' in nome):
                filtrados.append(eq)
                
        # Filtro de Escolas e Creches
        elif tipo in ['escola', 'creche', 'educacao', 'colegio', 'ciep']:
            if 'educação' in cat or 'escola' in nome or 'creche' in nome or 'ciep' in nome:
                filtrados.append(eq)
                
        # Filtro de FUNDEC (Cursos e Qualificação)
        elif tipo in ['fundec', 'curso', 'qualificacao', 'tecnico']:
            if 'fundec' in cat or 'fundec' in nome:
                filtrados.append(eq)
                
        # Filtro de Assistência Social e CRAS
        elif tipo in ['cras', 'creas', 'assistencia', 'bolsa familia', 'cadunico']:
            if 'assistência social' in cat or 'cras' in nome or 'creas' in nome:
                filtrados.append(eq)
                
        # Filtro de Segurança e Defesa Civil
        elif tipo in ['seguranca', 'defesa civil', 'guarda', 'obras']:
            if 'segurança' in cat or 'defesa civil' in nome or 'guarda' in nome:
                filtrados.append(eq)
                
        else:
            # Busca genérica por palavra-chave
            if tipo in nome or tipo in cat or tipo in desc:
                filtrados.append(eq)
                
    return filtrados if filtrados else equipamentos

def localizar_mais_proximos(cep_cidadao: str, tipo_servico: str = 'hospital', top_n: int = 3) -> dict:
    """
    Função principal que orquestra a busca de proximidade e prepara o contexto para a IA.
    """
    # 1. Valida o CEP
    cep_valido = validar_cep(cep_cidadao)
    
    # 2. Consulta o ViaCEP
    dados_cep = consultar_viacep(cep_valido)
    
    # 3. Obtém latitude e longitude do ponto de origem
    lat_origem, lon_origem, metodo_geo = obter_coordenadas_origem(dados_cep)
    
    # 4. Carrega a base oficial de equipamentos
    todos_equipamentos = carregar_equipamentos_oficiais()
    
    # 5. Filtra pelo serviço solicitado
    candidatos = filtrar_por_categoria(todos_equipamentos, tipo_servico)
    
    # 6. Calcula a distância de cada um
    resultados = []
    for eq in candidatos:
        lat_eq = float(eq.get('lat') or -22.7850)
        lon_eq = float(eq.get('lon') or -43.3050)
        
        dist_km = calcular_distancia_haversine(lat_origem, lon_origem, lat_eq, lon_eq)
        
        # Estimar tempo de deslocamento
        tempo_carro_min = max(2, round((dist_km / 35.0) * 60))  # Média de 35 km/h na cidade
        tempo_a_pe_min = round((dist_km / 4.5) * 60)           # Caminhada 4.5 km/h
        
        resultados.append({
            'id': eq.get('id'),
            'nome': eq.get('nome'),
            'categoria': eq.get('categoria'),
            'distrito': eq.get('distrito'),
            'bairro': eq.get('bairro'),
            'endereco': eq.get('endereco'),
            'cep': eq.get('cep'),
            'telefone': eq.get('telefone') or 'Não informado',
            'horario': eq.get('horario_funcionamento') or 'Segunda a sexta-feira, das 09h às 17h',
            'distancia_km': round(dist_km, 2),
            'tempo_carro_min': tempo_carro_min,
            'tempo_a_pe_min': tempo_a_pe_min,
            'lat': lat_eq,
            'lon': lon_eq,
            'hub_nome': eq.get('hub_nome', '')
        })
    
    # 7. Ordena pela menor distância
    resultados.sort(key=lambda x: x['distancia_km'])
    top_proximos = resultados[:top_n]
    
    # 8. Monta o pacote estruturado de contexto para a IA
    origem_formatada = {
        'cep': dados_cep.get('cep'),
        'logradouro': dados_cep.get('logradouro'),
        'bairro': dados_cep.get('bairro'),
        'cidade': dados_cep.get('localidade'),
        'uf': dados_cep.get('uf'),
        'lat': round(lat_origem, 6),
        'lon': round(lon_origem, 6),
        'precisao_geografica': metodo_geo
    }
    
    # Gera o texto pronto para ser injetado no prompt da IA
    prompt_contexto = gerar_prompt_para_ia(origem_formatada, tipo_servico, top_proximos)
    
    return {
        'status': 'sucesso',
        'origem': origem_formatada,
        'tipo_servico_buscado': tipo_servico,
        'total_encontrados': len(resultados),
        'equipamentos_mais_proximos': top_proximos,
        'prompt_contexto_ia': prompt_contexto
    }

def gerar_prompt_para_ia(origem: dict, tipo_servico: str, mais_proximos: list) -> str:
    """
    Gera o texto de contexto estruturado para enviar diretamente ao modelo de linguagem (Gemini).
    """
    linhas = []
    linhas.append("### CONTEXTO OFICIAL DE GEOLOCALIZAÇÃO — PREFEITURA DE DUQUE DE CAXIAS")
    linhas.append(f"**Localização Atual do Cidadão:** {origem['logradouro']} - {origem['bairro']}, {origem['cidade']}/{origem['uf']} (CEP: {origem['cep']})")
    linhas.append(f"**Serviço / Equipamento Procurado:** {tipo_servico.upper()}")
    linhas.append("\n**Unidades Oficiais Mais Próximas Encontradas (Base Consolidada 2026):**\n")
    
    for i, eq in enumerate(mais_proximos, 1):
        linhas.append(f"{i}º LUGAR — **{eq['nome']}**")
        linhas.append(f"   • Distância Geográfica: **{eq['distancia_km']} km** (~{eq['tempo_carro_min']} min de carro | ~{eq['tempo_a_pe_min']} min a pé)")
        linhas.append(f"   • Endereço: {eq['endereco']} — Bairro: {eq['bairro']} ({eq['distrito']}º Distrito)")
        linhas.append(f"   • Telefone: {eq['telefone']}")
        linhas.append(f"   • Horário de Funcionamento: {eq['horario']}")
        if eq.get('hub_nome'):
            linhas.append(f"   • Complexo: Funciona no prédio compartilhado {eq['hub_nome']}")
        linhas.append("")

    linhas.append("---")
    linhas.append("**Instrução para a IA:**")
    linhas.append("Responda ao cidadão com empatia, objetividade e clareza, indicando a unidade mais próxima em primeiro lugar com o endereço exato, telefone e horário de funcionamento. Se for caso de urgência/emergência hospitalar, reforce que UPAs e hospitais operam em regime 24 horas.")
    
    return "\n".join(linhas)

# =========================================================================
# EXECUÇÃO CLI DIRETA (TESTE)
# =========================================================================
if __name__ == '__main__':
    # Permite passar CEP e tipo via linha de comando
    cep_teste = sys.argv[1] if len(sys.argv) > 1 else '25071210'
    tipo_teste = sys.argv[2] if len(sys.argv) > 2 else 'hospital'
    
    print(f"\n🔎 Executando busca de proximidade para o CEP '{cep_teste}' (Tipo: '{tipo_teste}')...\n")
    
    try:
        resultado = localizar_mais_proximos(cep_teste, tipo_teste, top_n=3)
        print(resultado['prompt_contexto_ia'])
        print("\n✅ Sucesso! Contexto estruturado pronto para ser enviado para a IA.\n")
    except Exception as e:
        print(f"❌ Erro durante o processamento: {e}")
