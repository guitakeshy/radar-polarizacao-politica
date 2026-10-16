import streamlit as st
from src.theme import page_header
import pandas as pd
from src.database import Database, Comment
from src.metrics import MetricsCalculator
from src.visualizations import Visualizations

page_header(st, "Análise Estatística e Correlações", eyebrow="Estatística", accent="Correlações")

db = Database()
session = db.get_session()

query = session.query(Comment.sentiment, Comment.is_aggressive, Comment.text_cleaned, Comment.text_length).all()
session.close()

df = pd.DataFrame(query, columns=['sentiment', 'is_aggressive', 'text_cleaned', 'text_length'])
df['text_length'] = MetricsCalculator.text_lengths(df)
df = df.dropna(subset=['text_length'])

if df.empty or len(df) < 50:
    st.warning("É recomendado ter pelo menos 50 comentários coletados para análises estatísticas significativas.")
else:
    # --- Taxas com intervalo de confiança ---
    st.markdown("### Taxas com Intervalo de Confiança (95%)")
    n = len(df)
    neg = int((df['sentiment'] == 'Negativo').sum())
    aggr = int(df['is_aggressive'].sum())
    neg_lo, neg_hi = MetricsCalculator.proportion_ci(neg, n)
    aggr_lo, aggr_hi = MetricsCalculator.proportion_ci(aggr, n)
    col1, col2 = st.columns(2)
    col1.metric("Sentimento Negativo", f"{neg / n * 100:.1f}%", help=f"IC 95%: {neg_lo:.1f}% – {neg_hi:.1f}%")
    col1.caption(f"IC 95%: {neg_lo:.1f}% – {neg_hi:.1f}%")
    col2.metric("Agressividade", f"{aggr / n * 100:.1f}%", help=f"IC 95%: {aggr_lo:.1f}% – {aggr_hi:.1f}%")
    col2.caption(f"IC 95%: {aggr_lo:.1f}% – {aggr_hi:.1f}%")
    st.caption("Intervalos de Wilson. Assumem comentários independentes; como comentários do mesmo vídeo se parecem entre si, a incerteza real é maior.")

    # --- Qui-quadrado ---
    st.markdown("### Sentimento × Agressividade (Qui-quadrado)")
    test = MetricsCalculator.sentiment_aggression_test(df)
    if test is None:
        st.info("Não há variação suficiente para o teste.")
    else:
        if test["aggression_rate_by_sentiment"] is not None:
            rates = test["aggression_rate_by_sentiment"].rename("% agressivos").to_frame()
            st.dataframe(rates.style.format("{:.1f}%"))
        significant = test["p_value"] < 0.05
        effect = MetricsCalculator.interpret_effect_size(test["cramers_v"])
        st.markdown(
            f"- χ² = {test['chi2']:.2f} (gl = {test['dof']}, n = {test['n']})\n"
            f"- p-valor = {test['p_value']:.2g} → "
            f"{'associação **estatisticamente significativa**' if significant else 'sem evidência de associação'} (α = 0,05)\n"
            f"- V de Cramér = {test['cramers_v']:.3f} → efeito **{effect}**"
        )

    # --- Matriz de correlação ---
    st.markdown("""
    ### Matriz de Correlação (Spearman)
    A matriz abaixo investiga as correlações de postos entre características dos comentários.
    - **Sentimento Numérico:** 1 (Positivo), 0 (Neutro), -1 (Negativo).
    - **Agressivo:** 1 (Sim), 0 (Não).
    - **Tamanho do Texto:** Quantidade de caracteres.
    """)

    fig = Visualizations.plot_correlation_matrix(df)
    st.plotly_chart(fig, width='stretch')

    df_num = pd.DataFrame({
        'sentimento_num': df['sentiment'].map({"Positivo": 1, "Neutro": 0, "Negativo": -1}),
        'agressivo': df['is_aggressive'].astype(int),
        'tamanho_texto': df['text_length'],
    })
    corr_table = MetricsCalculator.correlation_with_pvalues(df_num)
    if not corr_table.empty:
        corr_table['Efeito'] = corr_table['rho (Spearman)'].map(MetricsCalculator.interpret_effect_size)
        st.dataframe(
            corr_table.style.format({"rho (Spearman)": "{:.3f}", "p-valor": "{:.2g}"}),
            hide_index=True
        )

    st.markdown("""
    **Diferenciando significância estatística de relevância prática:**
    Com milhares de comentários, até correlações minúsculas ficam "significativas" (p < 0,05).
    Por isso olhe sempre o **tamanho do efeito** (rho ou V de Cramér): abaixo de 0,1 é desprezível na prática.
    E correlação **não comprova causalidade** (escrever muito não causa negatividade, nem a negatividade obriga a escrever muito).
    """)
