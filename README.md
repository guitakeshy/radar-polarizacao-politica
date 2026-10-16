# Radar da Polarização Política Brasileira 🇧🇷

Aplicação completa para análise de discussões políticas no YouTube, desenvolvida em Python e Streamlit, com foco na investigação de padrões de polarização e agressividade.

## Tecnologias Utilizadas
- **Python 3**
- **Streamlit**: Interface gráfica interativa.
- **YouTube Data API v3**: Coleta automatizada de vídeos e comentários.
- **SQLAlchemy & SQLite**: Armazenamento e gerenciamento dos dados coletados.
- **HuggingFace Transformers**: Análise de sentimentos utilizando modelo multilíngue (`nlptown/bert-base-multilingual-uncased-sentiment`).
- **Plotly**: Visualização de dados interativa.
- **Pandas & Scikit-learn**: Processamento e análise de métricas estatísticas.
- **Pytest**: Testes automatizados.

## Instalação e Execução (Windows)

1. **Abra o terminal (PowerShell ou CMD) e navegue até a pasta do projeto.**

2. **Crie um ambiente virtual:**
```powershell
python -m venv venv
```

3. **Ative o ambiente virtual:**
```powershell
.\venv\Scripts\activate
```

4. **Instale as dependências completas (coleta + análise):**
```powershell
pip install -r requirements-coleta.txt
```
> `requirements.txt` contém apenas o necessário para *visualizar* os dados (usado na versão pública).

5. **Configuração da API:**
- Faça uma cópia do arquivo `.env.example` e renomeie para `.env`.
- Obtenha uma chave no Google Cloud Console (YouTube Data API v3).
- Cole a chave no arquivo `.env`.

6. **Execute a aplicação:**
```powershell
python -m streamlit run app.py
```

## Como usar
1. Na interface do Streamlit, acesse a aba **Busca e Coleta**.
2. Pesquise por termos como "Eleições 2026", "Polarização Política", etc.
3. Selecione os vídeos desejados e inicie a coleta.
4. Navegue pelas demais abas para visualizar os gráficos, indicadores e correlações.
5. Acesse a aba **Relatório Analítico** para exportar as conclusões da pesquisa.

## Metodologia de Agressividade e Polarização
- Os léxicos ficam em `src/lexicon.py`. As regras casam **palavras inteiras** (com plural/feminino), ignorando acentos, caixa e letras alongadas. Assim, "delegado" não é confundido com "gado", nem "vermelho" com "verme".
- **Polarização afetiva:** a página *Polarização e Agressividade* mostra qual campo político (esquerda/direita) é alvo de rótulos pejorativos, por vídeo e no total.
- **Análise Estatística:** intervalos de confiança (Wilson), teste qui-quadrado com V de Cramér e correlações de Spearman com p-valores.

Depois de alterar os léxicos, reclassifique os comentários já coletados (não usa a API nem o modelo):
```powershell
python reprocess_aggression.py            # apenas mostra o impacto
python reprocess_aggression.py --aplicar  # grava no banco
```

> `generate_images.py` gera gráficos com **dados simulados** (marcados com marca d'água). Para gráficos reais, use `export_real_data.py`.

## Versão Pública (somente leitura)
Quando não há chave da API configurada (ou com `PUBLIC_MODE=1`), a aplicação entra em **modo público**:
a página de coleta some do menu, os exemplos de comentários ficam ocultos e os dados vêm de `data/radar_publico.db`.

Esse banco público **não contém o texto dos comentários**, apenas os resultados (sentimento, agressividade, alvos políticos, tamanho do texto). Gere-o sempre depois de uma coleta:
```powershell
python export_public_db.py
```
O banco completo (`data/radar_politico.db`) fica só no seu computador e está no `.gitignore`.
Para testar localmente:
```powershell
$env:PUBLIC_MODE="1"; python -m streamlit run app.py
```

### Publicar no Streamlit Community Cloud (grátis)
1. Crie um repositório **público** no GitHub e envie os arquivos do projeto (sem `venv/` e **sem `.env`**).
2. Em [share.streamlit.io](https://share.streamlit.io), clique em *Create app*, escolha o repositório e o arquivo `app.py`.
3. Para incorporar em outro site:
```html
<iframe src="https://SEU-APP.streamlit.app/?embed=true" style="width:100%;height:900px;border:none;"></iframe>
```
Para atualizar os dados publicados, faça uma nova coleta localmente, rode `python export_public_db.py` e envie o novo `data/radar_publico.db` ao GitHub.

## Testes
Para rodar os testes automatizados, certifique-se de estar com o ambiente virtual ativado e execute:
```powershell
pytest tests/
```
