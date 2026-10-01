# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('dados/enderecos_duque_de_caxias_v2.db')
c = conn.cursor()

print("=== TESTE 1: Equipamentos por Distrito via VIEW ===")
for row in c.execute("SELECT distrito, COUNT(*) FROM vw_equipamentos_consolidada GROUP BY distrito ORDER BY distrito;").fetchall():
    print(f"Distrito {row[0]}: {row[1]} equipamentos")

print("\n=== TESTE 2: Amostra da Tabela de Auditoria ===")
for row in c.execute("SELECT id, tabela_afetada, registro_id, operacao, usuario, criado_em FROM auditoria LIMIT 3;").fetchall():
    print(row)

print("\n=== TESTE 3: Equipamentos que oferecem Vacinação ===")
query_vac = """
    SELECT e.nome, b.nome, s.nome 
    FROM equipamentos e
    JOIN equipamento_servicos es ON e.id = es.equipamento_id
    JOIN servicos s ON es.servico_id = s.id
    JOIN enderecos en ON e.endereco_id = en.id
    JOIN bairros b ON en.bairro_id = b.id
    WHERE s.nome LIKE '%Vacinação%'
    LIMIT 3;
"""
for row in c.execute(query_vac).fetchall():
    print(f" - {row[0]} | Bairro: {row[1]}")

print("\n=== TESTE 4: Órgãos dentro do Hub Centro Cívico ===")
query_hub = """
    SELECT e.nome, e.predio_sala, sec.sigla
    FROM equipamentos e
    JOIN hubs_predios h ON e.hub_id = h.id
    JOIN equipamento_secretarias es ON e.id = es.equipamento_id AND es.principal = 1
    JOIN secretarias sec ON es.secretaria_id = sec.id
    WHERE h.nome LIKE '%Centro Cívico%'
    LIMIT 4;
"""
for row in c.execute(query_hub).fetchall():
    print(f" - {row[0]} | Sala: {row[1]} | Sec: {row[2]}")

print("\n=== TESTE 5: Telefones e WhatsApps estruturados ===")
query_tel = """
    SELECT e.nome, t.numero, t.tipo, t.whatsapp
    FROM equipamento_telefones t
    JOIN equipamentos e ON t.equipamento_id = e.id
    WHERE t.tipo = 'PLANTÃO_24H'
    LIMIT 3;
"""
for row in c.execute(query_tel).fetchall():
    print(f" - {row[0]} | Tel: {row[1]} | Tipo: {row[2]}")

conn.close()
