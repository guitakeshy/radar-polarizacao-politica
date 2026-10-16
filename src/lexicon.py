"""
Léxicos e regras heurísticas para o contexto político brasileiro.

As regras casam palavras inteiras (com flexões de gênero/número), após remover
acentos e caixa. Isso evita falsos positivos de busca por substring, como
"advogado"/"delegado" (gado), "vermelho" (verme) ou "retirou" (tiro).
"""
import re
import unicodedata


def normalize(text):
    """Minúsculas e sem acentos, para casar 'ladrão' e 'ladrao' da mesma forma."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    # Reduz letras alongadas ("mentirosaaaas" -> "mentirosas")
    return re.sub(r"([a-z])\1{2,}", r"\1", text)


def _compile(patterns):
    # \b no início e no fim: casa apenas palavras/expressões inteiras
    return re.compile(r"\b(?:" + "|".join(patterns) + r")\b")


# Categorias de agressividade. Padrões escritos sem acento (ver normalize()).
AGGRESSION_PATTERNS = {
    "Insultos": _compile([
        r"idiotas?", r"imbecil", r"imbecis", r"burr[oa]s?", r"estupid[oa]s?",
        r"otari[oa]s?", r"canalhas?", r"safad[oa]s?", r"cretin[oa]s?", r"babacas?",
        r"ladr(?:ao|oes|ona|onas)", r"corrupt[oa]s?", r"vagabund[oa]s?",
        r"bandid[oa]s?", r"genocidas?", r"desgracad[oa]s?", r"mentiros[oa]s?",
        r"palhac[oa]s?",
    ]),
    "Ameaças": _compile([
        r"vou te (?:matar|pegar|quebrar|arrebentar|encher|achar)",
        r"(?:vamos|vou|tem que|tinha que|deviam|deveriam) (?:matar|fuzilar|enforcar|linchar)",
        r"matar (?:ele|ela|eles|elas|esse|essa|esses|essas|todos|voce|vcs?)",
        r"morr(?:a|am)", r"fuzil(?:ar|em|ado|ados)", r"enforc(?:ar|ado|ados)",
        r"linch(?:ar|ado|ados)", r"tiro na (?:cara|cabeca|testa|nuca)",
        r"bala (?:neles?|nelas?|nesse|nessa|nesses|nessas)",
        r"quebrar a cara", r"vai apanhar", r"merece apanhar", r"porrada",
    ]),
    "Desumanização": _compile([
        r"lixos?", r"vermes?", r"porc[oa]s?", r"parasitas?", r"escoria",
        r"pragas?", r"ratos?", r"ratazanas?", r"baratas?", r"gado", r"gados",
        r"vira-?latas?", r"sub-?humanos?",
    ]),
    "Hostilidade": _compile([
        r"porra", r"caralho", r"merdas?", r"fdp", r"pqp", r"vsf", r"vtnc",
        r"puta que pariu", r"filh[oa]s? da puta", r"vai se f\w*", r"vai tomar no \w+",
    ]),
}

# Rótulos pejorativos usados para atacar cada campo político.
# Servem para estimar polarização afetiva: quem é alvo de hostilidade.
CAMP_TARGET_PATTERNS = {
    "Esquerda": _compile([
        r"petralhas?", r"mortadelas?", r"esquerdopatas?", r"esquerdalha",
        r"esquerdistas? (?:burr|idiot|lixo|vagabund)\w*", r"comunas?",
        r"lula ladrao", r"lularapio", r"nove dedos", r"cachaceiro",
        r"descondenado", r"ex-?presidiario",
    ]),
    "Direita": _compile([
        r"bolsominions?", r"minions?", r"gado", r"gados", r"gado marcado",
        r"bolsonarent[oa]s?", r"bozo", r"bozonaro", r"bolsolixo",
        r"genocida", r"miliciano", r"fascistas?",
    ]),
}


def detect_aggression(text):
    """Retorna (is_aggressive, [categorias]) a partir do texto bruto."""
    norm = normalize(text)
    categories = [name for name, rx in AGGRESSION_PATTERNS.items() if rx.search(norm)]
    # Rótulos pejorativos contra um campo político também são linguagem agressiva
    if any(rx.search(norm) for rx in CAMP_TARGET_PATTERNS.values()):
        categories.append("Rótulos Partidários")
    return len(categories) > 0, categories


def detect_camp_targets(text):
    """Retorna a lista de campos políticos ('Esquerda', 'Direita') atacados com rótulos pejorativos."""
    norm = normalize(text)
    return [camp for camp, rx in CAMP_TARGET_PATTERNS.items() if rx.search(norm)]
