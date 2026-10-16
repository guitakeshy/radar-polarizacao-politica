import pytest
from src.nlp_processor import NLPProcessor
from src.metrics import MetricsCalculator
from src.lexicon import detect_aggression, detect_camp_targets
import pandas as pd

def test_clean_text():
    nlp = NLPProcessor()
    assert nlp.clean_text("Texto   com \n\n muitos   espaços") == "Texto com muitos espaços"
    assert nlp.clean_text(None) == ""

def test_processor_does_not_load_model_on_init():
    nlp = NLPProcessor()
    assert nlp._sentiment_pipeline is None

def test_analyze_aggression():
    nlp = NLPProcessor()

    # Teste de insulto
    is_agg, cats = nlp.analyze_aggression("Esse político é um ladrão e genocida.")
    assert is_agg is True
    assert "Insultos" in cats

    # Teste de ameaça
    is_agg, cats = nlp.analyze_aggression("Eu vou te matar se falar isso de novo.")
    assert is_agg is True
    assert "Ameaças" in cats

    # Teste sem agressividade
    is_agg, cats = nlp.analyze_aggression("Acho que as propostas econômicas não são as ideais para este momento.")
    assert is_agg is False
    assert len(cats) == 0

@pytest.mark.parametrize("text", [
    "O delegado e o advogado falaram com a imprensa.",   # gado
    "A bandeira vermelha tremulava na praça.",           # verme
    "Ele retirou a candidatura e tirou o time de campo.",  # tiro
    "Comprei uma bala no embalagem da balança.",         # bala
    "O suporte técnico da campanha respondeu.",          # porco/morte
    "Vou te apoiar nessa eleição.",                      # vou te
])
def test_no_substring_false_positives(text):
    is_agg, cats = detect_aggression(text)
    assert is_agg is False, cats

@pytest.mark.parametrize("text,category", [
    ("Esses bandidos roubaram tudo", "Insultos"),       # plural
    ("Que ladrao safado", "Insultos"),                   # sem acento
    ("CORRUPTOS!!!", "Insultos"),                        # caixa alta
    ("Bando de vermes", "Desumanização"),
    ("Tem que fuzilar esses caras", "Ameaças"),
    ("que merda de governo", "Hostilidade"),
    ("Pesquisas mentirosaaaas", "Insultos"),            # letras alongadas
    ("XÔ PETRALHAS!!", "Rótulos Partidários"),
])
def test_aggression_inflections(text, category):
    is_agg, cats = detect_aggression(text)
    assert is_agg is True
    assert category in cats

def test_camp_targets():
    assert detect_camp_targets("Esses petralhas não aprendem") == ["Esquerda"]
    assert detect_camp_targets("bolsominion é tudo igual") == ["Direita"]
    assert detect_camp_targets("O advogado do delegado falou") == []

def test_metrics_calculator():
    data = {
        'sentiment': ['Positivo', 'Negativo', 'Negativo', 'Neutro'],
        'is_aggressive': [False, True, False, False]
    }
    df = pd.DataFrame(data)

    # Test distribution
    dist = MetricsCalculator.calculate_sentiment_distribution(df)
    assert dist['Negativo'] == 50.0
    assert dist['Positivo'] == 25.0

    # Test aggression rate
    rate = MetricsCalculator.calculate_aggression_rate(df)
    assert rate == 25.0

@pytest.mark.parametrize("freq", ["D", "W", "M"])
def test_temporal_evolution_frequencies(freq):
    df = pd.DataFrame({
        'published_at': pd.to_datetime(['2024-01-01', '2024-01-15', '2024-02-10']),
        'sentiment': ['Negativo', 'Positivo', 'Negativo'],
        'is_aggressive': [True, False, False],
    })
    original = df.copy()
    temporal = MetricsCalculator.calculate_temporal_evolution(df, freq=freq)
    assert temporal['total_comments'].sum() == 3
    pd.testing.assert_frame_equal(df, original)  # não altera o DataFrame recebido

def test_camp_targets_by_group():
    df = pd.DataFrame({
        'video_title': ['A', 'A', 'B', 'B'],
        'text_cleaned': ['petralha', 'ok', 'bolsominion', 'gado marcado'],
    })
    out = MetricsCalculator.calculate_camp_targets(df, group_col='video_title').set_index('video_title')
    assert out.loc['A', 'esquerda_pct'] == 50.0
    assert out.loc['B', 'direita_pct'] == 100.0
    assert out.loc['A', 'balance'] == 1.0
    assert out.loc['B', 'balance'] == -1.0

def test_stored_results_without_text():
    # Banco público: sem texto, usa os resultados guardados
    df = pd.DataFrame({
        'video_title': ['A', 'A'],
        'text_cleaned': [None, None],
        'camp_targets': ['["Esquerda"]', '[]'],
        'text_length': [42, 10],
    })
    out = MetricsCalculator.calculate_camp_targets(df).iloc[0]
    assert out['esquerda_pct'] == 50.0
    assert MetricsCalculator.text_lengths(df).tolist() == [42.0, 10.0]

def test_proportion_ci():
    lo, hi = MetricsCalculator.proportion_ci(50, 100)
    assert lo < 50 < hi
    assert MetricsCalculator.proportion_ci(0, 0) == (0.0, 0.0)

def test_sentiment_aggression_test():
    df = pd.DataFrame({
        'sentiment': ['Negativo'] * 50 + ['Positivo'] * 50,
        'is_aggressive': [True] * 30 + [False] * 20 + [True] * 2 + [False] * 48,
    })
    result = MetricsCalculator.sentiment_aggression_test(df)
    assert result['p_value'] < 0.05
    assert result['cramers_v'] > 0.3
