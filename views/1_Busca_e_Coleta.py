import streamlit as st
from src.theme import page_header
from src.config import Config

# Na versão pública a coleta fica desativada (antes de importar as dependências pesadas)
if Config.is_public_mode():
    st.info("A coleta de dados está desativada na versão pública.")
    st.stop()

import pandas as pd
from datetime import datetime
import json
from src.youtube_client import YouTubeClient
from src.database import Database, Video, Comment
from src.nlp_processor import NLPProcessor

page_header(st, "Busca e Coleta de Dados", eyebrow="Coleta", accent="Coleta de Dados")

db = Database()
session = db.get_session()

# Processor compartilhado entre sessões; o modelo só é carregado na primeira análise
@st.cache_resource
def get_nlp_processor():
    return NLPProcessor()

# Interface de Busca
st.header("1. Pesquisar Vídeos")
col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("Termos de pesquisa", placeholder="Ex: Eleições 2026, Polarização política, Discurso de ódio política")
with col2:
    max_results = st.number_input("Máximo de vídeos na busca", min_value=1, max_value=50, value=10)

if st.button("Buscar Vídeos"):
    if not Config.is_api_key_configured():
        st.error("Configure a YOUTUBE_API_KEY no arquivo .env")
    elif query:
        with st.spinner("Buscando vídeos no YouTube..."):
            client = YouTubeClient()
            videos = client.search_videos(query, max_results=max_results)
            if videos:
                st.session_state.search_results = videos
                st.success(f"Encontrados {len(videos)} vídeos!")
            else:
                st.warning("Nenhum vídeo encontrado ou ocorreu um erro na API.")

# Seleção e Coleta
if "search_results" in st.session_state and st.session_state.search_results:
    st.header("2. Selecionar e Coletar")
    
    videos = st.session_state.search_results
    df_videos = pd.DataFrame(videos)
    
    # Adicionar checkbox de seleção (Simples usando multiselect de titles)
    video_titles = df_videos['title'].tolist()
    selected_titles = st.multiselect("Selecione os vídeos para coletar os comentários:", video_titles, default=video_titles[:3])
    
    max_comments = st.number_input("Máximo de comentários por vídeo", min_value=10, max_value=1000, value=200)
    
    if st.button("Iniciar Coleta e Análise"):
        selected_videos = [v for v in videos if v['title'] in selected_titles]
        
        if not selected_videos:
            st.warning("Selecione ao menos um vídeo.")
        else:
            client = YouTubeClient()
            nlp = get_nlp_processor()
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total = len(selected_videos)
            for i, video_data in enumerate(selected_videos):
                status_text.text(f"Processando vídeo {i+1}/{total}: {video_data['title'][:50]}... (o modelo de NLP pode demorar a carregar na primeira vez)")
                
                # Salvar vídeo no banco
                video = session.query(Video).filter_by(id=video_data['id']).first()
                if not video:
                    video = Video(
                        id=video_data['id'],
                        title=video_data['title'],
                        channel_title=video_data['channel_title'],
                        published_at=datetime.strptime(video_data['published_at'], "%Y-%m-%dT%H:%M:%SZ"),
                        description=video_data['description'],
                        search_term=query
                    )
                    session.add(video)
                    session.commit()
                
                # Coletar comentários
                comments_data = client.get_comments(video_data['id'], max_comments=max_comments)
                
                if comments_data:
                    # Ignora comentários já salvos (uma única consulta, não uma por comentário)
                    ids = [c['id'] for c in comments_data]
                    existing_ids = {row[0] for row in session.query(Comment.id).filter(Comment.id.in_(ids))}
                    new_comments = [c for c in comments_data if c['id'] not in existing_ids]

                    # NLP em lote
                    nlp_results = nlp.process_comments([c['text'] for c in new_comments])

                    # Analisar e salvar
                    for c_data, nlp_result in zip(new_comments, nlp_results):
                        pub_at = None
                        if c_data['published_at']:
                            try:
                                pub_at = datetime.strptime(c_data['published_at'], "%Y-%m-%dT%H:%M:%SZ")
                            except ValueError:
                                pass
                                
                        comment = Comment(
                            id=c_data['id'],
                            video_id=video_data['id'],
                            text_original=c_data['text'],
                            text_cleaned=nlp_result['cleaned_text'],
                            published_at=pub_at,
                            parent_id=c_data['parent_id'],
                            sentiment=nlp_result['sentiment'],
                            sentiment_score=nlp_result['sentiment_score'],
                            is_aggressive=nlp_result['is_aggressive'],
                            aggression_categories=json.dumps(nlp_result['aggression_categories'])
                        )
                        session.add(comment)
                    
                    try:
                        session.commit()
                    except Exception as e:
                        st.error(f"Erro ao salvar no banco: {e}")
                        session.rollback()
                        
                progress_bar.progress((i + 1) / total)
                
            status_text.text("Coleta e análise finalizadas com sucesso!")
            st.success("Dados salvos e prontos para visualização nas outras abas.")

session.close()
