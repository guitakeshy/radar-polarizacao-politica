"""
Gera o banco da versão pública (data/radar_publico.db) a partir do banco da pesquisa.

O banco público mantém apenas os RESULTADOS por comentário (sentimento, agressividade,
categorias, campos políticos atacados, tamanho do texto, data e vídeo) e remove
o texto de todos os comentários. Assim, publicar o arquivo não expõe frases de ninguém.

Uso (rode sempre depois de uma nova coleta, antes de publicar):
    python export_public_db.py
"""
import os
import json
import sqlite3
from src.config import Config
from src.database import Database
from src.lexicon import detect_camp_targets


def sqlite_path(url):
    return url.replace("sqlite:///", "")


src_path = sqlite_path(Config.DATABASE_URL)
dst_path = sqlite_path(Config.PUBLIC_DATABASE_URL)

# Garante que o banco de origem tenha as colunas novas
Database(Config.DATABASE_URL)

if os.path.exists(dst_path):
    os.remove(dst_path)

# Cópia consistente do banco de origem
with sqlite3.connect(src_path) as src, sqlite3.connect(dst_path) as dst:
    src.backup(dst)

conn = sqlite3.connect(dst_path)
rows = conn.execute("SELECT id, COALESCE(text_cleaned, text_original, '') FROM comments").fetchall()
conn.executemany(
    "UPDATE comments SET camp_targets = ?, text_length = ? WHERE id = ?",
    [(json.dumps(detect_camp_targets(t)), len(t), cid) for cid, t in rows],
)
# Remove todo texto de comentários e as descrições dos vídeos
conn.execute("UPDATE comments SET text_original = '', text_cleaned = NULL")
conn.execute("UPDATE videos SET description = NULL")
conn.commit()
# VACUUM reescreve o arquivo: sem isso, o texto apagado continuaria nas páginas livres do SQLite
conn.execute("VACUUM")
conn.close()

# Verificação: nenhum texto pode ter sobrado no arquivo
with open(dst_path, "rb") as f:
    raw = f.read()
sample = [t for _, t in rows if len(t) >= 25][:200]
leaks = sum(1 for t in sample if t.encode("utf-8") in raw)
if leaks:
    raise SystemExit(f"ERRO: {leaks} textos de comentários ainda encontrados em {dst_path}. Não publique.")

print(f"Banco público gerado: {dst_path}")
print(f"  comentários: {len(rows)} (sem texto)")
print(f"  tamanho: {os.path.getsize(dst_path) / 1024:.0f} KB")
print(f"  verificação: nenhum texto de comentário encontrado no arquivo ({len(sample)} amostras)")
