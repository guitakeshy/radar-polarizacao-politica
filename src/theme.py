"""
Identidade visual alinhada a guilhermetakeshy.com: fonte Lato, azul #1038c8,
laranja #ff4a00, cartões cinza-claros com cantos arredondados.
"""
import plotly.graph_objects as go
import plotly.io as pio

BLUE = "#1038c8"
BLUE_DARK = "#0a2390"
ORANGE = "#ff4a00"
NAVY = "#071448"
SKY = "#8fa8ff"
INK = "#111318"
TEXT_2 = "#2b3040"
MUTED = "#5a6070"
MUTED_LIGHT = "#a9b4dc"
GREY = "#f3f2f1"
LINE = "#e3e5ee"

SITE_URL = "https://www.guilhermetakeshy.com/"
FONT = "Lato, 'Segoe UI', system-ui, -apple-system, Roboto, Helvetica, Arial, sans-serif"

# Cores semânticas usadas pelos gráficos
SENTIMENT_COLORS = {
    "Positivo": BLUE,
    "Neutro": MUTED_LIGHT,
    "Negativo": ORANGE,
    "Inconclusivo": LINE,
}
CATEGORY_SEQUENCE = [BLUE, ORANGE, NAVY, SKY, MUTED, BLUE_DARK]
DIVERGING_SCALE = [[0.0, ORANGE], [0.5, "#ffffff"], [1.0, BLUE]]

# Template Plotly aplicado a todos os gráficos
pio.templates["takeshy"] = go.layout.Template(
    layout=dict(
        font=dict(family=FONT, color=TEXT_2, size=14),
        title=dict(font=dict(family=FONT, color=INK, size=18), x=0, xanchor="left"),
        colorway=CATEGORY_SEQUENCE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor=LINE, linecolor=LINE, zerolinecolor=LINE, tickfont=dict(color=MUTED)),
        yaxis=dict(gridcolor=LINE, linecolor=LINE, zerolinecolor=LINE, tickfont=dict(color=MUTED)),
        legend=dict(font=dict(color=TEXT_2)),
        hoverlabel=dict(font=dict(family=FONT), bgcolor="#ffffff", bordercolor=LINE),
        colorscale=dict(diverging=DIVERGING_SCALE),
        margin=dict(t=64, l=8, r=8, b=8),
    )
)
pio.templates.default = "plotly_white+takeshy"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap');

html, body, [class*="st-"], .stMarkdown, button, input, textarea, select {{
    font-family: {FONT};
}}
/* Ícones do Streamlit usam fonte própria: não sobrescrever */
[data-testid="stIconMaterial"], .material-symbols-rounded {{ font-family: 'Material Symbols Rounded' !important; }}

h1, h2, h3, h4 {{
    font-family: {FONT} !important;
    font-weight: 900 !important;
    color: {INK};
    letter-spacing: -0.035em;
    line-height: 1.1;
}}
h1 {{ font-size: clamp(2rem, 4vw, 2.75rem) !important; }}
h3 {{ letter-spacing: -0.02em; }}

p, li {{ color: {TEXT_2}; line-height: 1.6; }}
a {{ color: {BLUE}; font-weight: 700; text-decoration: none; }}
a:hover {{ color: {BLUE_DARK}; }}

/* Destaque azul dentro de títulos */
.tk-accent {{ color: {BLUE}; }}

/* Sobretítulo: azul, maiúsculas e espaçado */
.tk-eyebrow {{
    color: {BLUE};
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}}
.tk-lead {{ color: {MUTED}; font-size: 1.1rem; line-height: 1.6; max-width: 46rem; margin: 0.75rem 0 0.5rem; }}
.tk-header {{ margin-bottom: 0.5rem; }}
.tk-header h1 {{ margin: 0; padding: 0.25rem 0 0; }}

/* Métricas como cartões cinza arredondados */
[data-testid="stMetric"] {{
    background: {GREY};
    border-radius: 20px;
    padding: 1.1rem 1.25rem;
}}
[data-testid="stMetricLabel"] p {{ color: {MUTED}; font-weight: 700; font-size: 0.85rem; }}
[data-testid="stMetricValue"] {{ font-weight: 900; color: {INK}; letter-spacing: -0.03em; }}

/* Caixas de aviso e gráficos com cantos do site */
[data-testid="stAlert"] {{ border-radius: 16px; }}
[data-testid="stPlotlyChart"] {{
    border: 1px solid {LINE};
    border-radius: 20px;
    padding: 0.75rem;
}}

/* Botões no laranja do site */
.stButton > button, .stDownloadButton > button {{
    background: {ORANGE};
    color: #ffffff;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    letter-spacing: 0.02em;
    padding: 0.6rem 1.4rem;
    box-shadow: 0 10px 24px -10px rgba(255, 74, 0, 0.6);
}}
.stButton > button:hover, .stDownloadButton > button:hover {{ background: #e03f00; color: #ffffff; }}

/* Barra lateral */
[data-testid="stSidebar"] {{ background: {GREY}; border-right: 1px solid {LINE}; }}
[data-testid="stSidebarNav"] a span {{ color: {TEXT_2}; font-weight: 700; }}
[data-testid="stSidebarNav"] a[aria-current="page"] {{ background: #ffffff; border-radius: 10px; }}
[data-testid="stSidebarNav"] a[aria-current="page"] span {{ color: {BLUE}; }}

.tk-credit {{ font-size: 0.85rem; color: {MUTED}; line-height: 1.5; }}
.tk-credit a {{ color: {BLUE}; }}
</style>
"""


def apply_theme(st):
    """Injeta o CSS do site e o crédito na barra lateral."""
    st.html(CSS)
    st.sidebar.html(
        f'<div class="tk-credit">Um projeto de<br>'
        f'<a href="{SITE_URL}" target="_blank" rel="noopener">Guilherme Takeshy ↗</a></div>'
    )


def page_header(st, title, eyebrow=None, lead=None, accent=None):
    """
    Cabeçalho no estilo do site: sobretítulo azul, título forte e
    (opcionalmente) a parte `accent` do título destacada em azul.
    """
    if accent and accent in title:
        title = title.replace(accent, f'<span class="tk-accent">{accent}</span>')
    html = '<div class="tk-header">'
    if eyebrow:
        html += f'<div class="tk-eyebrow">{eyebrow}</div>'
    html += f'<h1>{title}</h1>'
    if lead:
        html += f'<p class="tk-lead">{lead}</p>'
    st.html(html + '</div>')
