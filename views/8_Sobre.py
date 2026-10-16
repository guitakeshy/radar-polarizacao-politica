import streamlit as st
from src.theme import page_header
import pandas as pd
from sqlalchemy import func
from src.database import Database, Video, Comment

page_header(st, "Sobre o Projeto", eyebrow="Metodologia", accent="Projeto")

session = Database().get_session()
n_videos = session.query(Video).count()
n_comments = session.query(Comment).count()
first, last = session.query(func.min(Comment.published_at), func.max(Comment.published_at)).one()
terms = [t for (t,) in session.query(Video.search_term).distinct() if t]
session.close()

st.markdown("""
O **Radar da Polarização Política Brasileira** investiga como as pessoas discutem política
nos comentários do YouTube: quanto do debate é apenas discordância (sentimento negativo)
e quanto vira hostilidade, com insultos, desumanização e rótulos contra o "outro lado".
""")

st.markdown("### A amostra")
col1, col2, col3 = st.columns(3)
col1.metric("Vídeos", n_videos)
col2.metric("Comentários", f"{n_comments:,}".replace(",", "."))
if first and last:
    col3.metric("Período", f"{pd.Timestamp(first):%m/%Y} – {pd.Timestamp(last):%m/%Y}")
if terms:
    st.caption("Termos de busca usados na coleta: " + ", ".join(f"“{t}”" for t in sorted(terms)))

st.markdown("""
### Como funciona

**1. Coleta.** Vídeos encontrados por termos de busca na API oficial do YouTube (YouTube Data API v3)
e seus comentários públicos. Nenhum nome de usuário é armazenado, apenas o texto.

**2. Sentimento.** Cada comentário passa por um modelo de linguagem multilíngue
(`nlptown/bert-base-multilingual-uncased-sentiment`), que dá uma nota de 1 a 5:
notas 1–2 viram *Negativo*, 3 *Neutro* e 4–5 *Positivo*.

**3. Agressividade.** Um dicionário de expressões do contexto político brasileiro identifica
quatro tipos de agressividade, além dos rótulos partidários:
- **Insultos:** "ladrão", "vagabundo", "corrupto"…
- **Ameaças:** "vou te pegar", "tem que fuzilar"…
- **Desumanização:** "lixo", "verme", "gado"…
- **Hostilidade:** palavrões dirigidos ao debate
- **Rótulos partidários:** "petralha", "bolsominion"…

O dicionário considera palavras inteiras, plurais, ausência de acentos e letras alongadas
("mentirosaaaas"), para evitar confusões como "delegado" ↔ "gado".

**4. Polarização afetiva.** Os rótulos pejorativos são separados conforme o campo político
atacado (esquerda ou direita), mostrando quem é alvo da hostilidade em cada vídeo.

**5. Estatística.** Intervalos de confiança de 95%, teste qui-quadrado e correlações de Spearman,
sempre com o tamanho do efeito, para separar o que é estatisticamente significativo do que é relevante.
""")

st.markdown("""
### Limitações: leia antes de citar os números
- **A amostra não representa o Brasil.** Quem comenta no YouTube é um recorte específico, e os vídeos
  dependem dos termos de busca escolhidos.
- **Classificação automática erra.** Ironia, sarcasmo, citações ("ele me chamou de ladrão") e gírias
  podem gerar falsos positivos ou negativos. O modelo de sentimento foi treinado com avaliações de
  produtos, não com debate político.
- **Dicionários são incompletos.** Novas gírias e ofensas surgem o tempo todo.
- **Correlação não é causalidade.** Associações encontradas não explicam por que elas acontecem.
- Os números descrevem **padrões coletivos**, nunca o comportamento de pessoas específicas.
""")

st.markdown("""
### Ética e privacidade
Apenas comentários públicos foram analisados, sem nomes de usuário. Esta versão pública não
contém nem exibe o texto dos comentários: apenas os resultados agregados da classificação.
""")
