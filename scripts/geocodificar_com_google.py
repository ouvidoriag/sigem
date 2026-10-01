# -*- coding: utf-8 -*-
"""
=============================================================================
🏛️ PREFEITURA MUNICIPAL DE DUQUE DE CAXIAS — RJ
Script de Geocodificação de Alta Precisão via Google Geocoding API
=============================================================================
Este script permite auditar e recalibrar as coordenadas dos 442 equipamentos
municipais utilizando a Google Geocoding API com foco no location_type 'ROOFTOP'.

Uso:
  python scripts/geocodificar_com_google.py --api-key "SUA_CHAVE_GOOGLE" --preview
  python scripts/geocodificar_com_google.py --api-key "SUA_CHAVE_GOOGLE" --executar
  python scripts/geocodificar_com_google.py --testar-endereco "Rua General Dionísio, 764, 25 de Agosto"
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.parse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'dados', 'todos_os_enderecos_duque_de_caxias.json')

def consultar_google_geocoding(endereco_completo, api_key, restrito_caxias=True):
    """
    Consulta a Google Geocoding API restringindo a Duque de Caxias / RJ / Brasil.
    Retorna (lat, lon, location_type, formatted_address, place_id) ou None.
    """
    params = {
        'address': endereco_completo,
        'key': api_key
    }
    if restrito_caxias:
        params['components'] = 'locality:Duque de Caxias|administrative_area:RJ|country:BR'

    url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urllib.parse.urlencode(params)

    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'PrefeituraDuqueDeCaxias-SIGEM/1.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            if data.get('status') == 'OK' and data.get('results'):
                res = data['results'][0]
                geometry = res.get('geometry', {})
                loc = geometry.get('location', {})
                lat = loc.get('lat')
                lon = loc.get('lng')
                location_type = geometry.get('location_type', 'UNKNOWN')
                formatted = res.get('formatted_address', '')
                place_id = res.get('place_id', '')
                return {
                    'lat': lat,
                    'lon': lon,
                    'location_type': location_type,
                    'formatted_address': formatted,
                    'place_id': place_id,
                    'raw': res
                }
            else:
                return {'error': data.get('status'), 'error_message': data.get('error_message', '')}
    except Exception as e:
        return {'error': 'EXCEPTION', 'error_message': str(e)}

def main():
    parser = argparse.ArgumentParser(description="Google Geocoding API para Duque de Caxias")
    parser.add_argument('--api-key', type=str, help="Chave de API da Google Maps Platform (Google Cloud)")
    parser.add_argument('--testar-endereco', type=str, help="Testa a geocodificação de um endereço avulso")
    parser.add_argument('--preview', action='store_true', help="Analisa a base sem salvar alterações")
    parser.add_argument('--executar', action='store_true', help="Executa e salva alterações na base JSON")
    parser.add_argument('--limite', type=int, default=10, help="Limite de registros para testar (padrão: 10)")
    args = parser.parse_args()

    print("=" * 70)
    print("🏛️ SIGEM — PREFEITURA DE DUQUE DE CAXIAS | GOOGLE GEOCODING API")
    print("=" * 70)

    if args.testar_endereco:
        if not args.api_key:
            print("❌ Erro: Forneça a --api-key para realizar a consulta.")
            sys.exit(1)
        
        print(f"\n🔍 Testando endereço: {args.testar_endereco}")
        res = consultar_google_geocoding(args.testar_endereco, args.api_key)
        if 'error' in res:
            print(f"❌ Resposta de Erro do Google: {res['error']} - {res.get('error_message')}")
        else:
            print(f"✅ Sucesso:")
            print(f"   • Latitude:  {res['lat']}")
            print(f"   • Longitude: {res['lon']}")
            print(f"   • Precisão (location_type): {res['location_type']}")
            print(f"   • Endereço Oficial Formatado: {res['formatted_address']}")
            print(f"   • Place ID: {res['place_id']}")
            if res['location_type'] == 'ROOFTOP':
                print("   🎯 CLASSIFICAÇÃO: ROOFTOP (Lote Exato / Fachada do Imóvel)")
            elif res['location_type'] == 'RANGE_INTERPOLATED':
                print("   📐 CLASSIFICAÇÃO: RANGE_INTERPOLATED (Interpolação de número na via)")
            else:
                print(f"   ⚠️ CLASSIFICAÇÃO: {res['location_type']} (Recomenda-se ajuste visual)")
        return

    print("\nEste script está pronto para auditar e calibrar as coordenadas com precisão ROOFTOP.")
    print("Para testar um endereço específico, utilize:")
    print("  python scripts/geocodificar_com_google.py --api-key YOUR_KEY --testar-endereco \"Rua General Dionísio, 764, Duque de Caxias\"")

if __name__ == '__main__':
    main()
