"""
Reclassifica a agressividade de todos os comentários já salvos no banco
usando o léxico atual (src/lexicon.py). Não usa a API nem o modelo de NLP.

Uso:
    python reprocess_aggression.py            # mostra o impacto, sem alterar nada
    python reprocess_aggression.py --aplicar  # grava as novas classificações
"""
import sys
import json
from collections import Counter
from src.database import Database, Comment
from src.lexicon import detect_aggression

apply_changes = "--aplicar" in sys.argv

session = Database().get_session()
comments = session.query(Comment).all()

before = sum(1 for c in comments if c.is_aggressive)
became_aggressive = 0
stopped_aggressive = 0
categories_after = Counter()

for c in comments:
    is_aggressive, categories = detect_aggression(c.text_cleaned or c.text_original or "")
    categories_after.update(categories)
    if is_aggressive and not c.is_aggressive:
        became_aggressive += 1
    elif c.is_aggressive and not is_aggressive:
        stopped_aggressive += 1
    if apply_changes:
        c.is_aggressive = is_aggressive
        c.aggression_categories = json.dumps(categories)

after = before + became_aggressive - stopped_aggressive
total = len(comments) or 1

print(f"Comentários: {len(comments)}")
print(f"Agressivos antes:  {before} ({before / total * 100:.1f}%)")
print(f"Agressivos depois: {after} ({after / total * 100:.1f}%)")
print(f"  deixaram de ser agressivos: {stopped_aggressive}")
print(f"  passaram a ser agressivos:  {became_aggressive}")
print("Categorias (depois):", dict(categories_after.most_common()))

if apply_changes:
    session.commit()
    print("Alterações gravadas no banco.")
else:
    print("\nNada foi alterado. Rode com --aplicar para gravar.")

session.close()
