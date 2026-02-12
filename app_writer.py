import streamlit as st
import os
import io
import zipfile
from google import genai
from google.genai import types
from supabase import create_client, Client

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Fábrica 21.0 - Automação Total", layout="wide", page_icon="🎬")
st.title("🎬 Fábrica 21.0 - O Renascimento")
st.markdown("*Automação de Roteiro: Legendas, Flux Prompts e Grok Animação.*")

# --- CONEXÃO SEGURA (SUPABASE + GEMINI) ---
try:
    # Busca nos Secrets do Streamlit Cloud
    api_key = st.secrets["GEMINI_API_KEY"]
    supa_url = st.secrets["supabase"]["url"]
    supa_key = st.secrets["supabase"]["key"]
    
    client_gemini = genai.Client(api_key=api_key)
    supabase: Client = create_client(supa_url, supa_key)
except Exception as e:
    st.error("Erro nas chaves! Verifique os Secrets no painel do Streamlit.")
    st.stop()

# --- ABA DE PRODUÇÃO ---
tab_roteiro, tab_automacao = st.tabs(["✍️ Criar Roteiro", "⚙️ Linha de Montagem"])

with tab_roteiro:
    st.header("1. Crie a História (Contexto Persistente)")
    # Aqui usamos o Supabase para salvar a ideia central e não perder o contexto
    ideia_base = st.text_area("Sobre o que é a história de hoje?", placeholder="Ex: O Príncipe Julian descobre a traição de Ayla na chuva.")
    
    if st.button("📓 Gerar Roteiro para Storybook"):
        with st.spinner("Escrevendo narrativa envolvente..."):
            prompt_story = f"Escreva uma história curta e impactante com plot twists baseada em: {ideia_base}. Foco em romance e drama visual."
            res = client_gemini.models.generate_content(model="gemini-2.0-flash", contents=prompt_story)
            st.session_state['roteiro_final'] = res.text
            st.success("Roteiro Criado! Vá para a aba 'Linha de Montagem'.")
            st.write(res.text)

with tab_automacao:
    st.header("2. Automação para CapCut/Grok/Flux")
    
    texto_para_processar = st.text_area("Roteiro Final:", value=st.session_state.get('roteiro_final', ''), height=200)
    
    if st.button("🚀 Gerar Kit Completo"):
        if not texto_para_processar:
            st.warning("Gere ou cole um roteiro primeiro.")
        else:
            with st.spinner("Desmembrando em cenas de 6 segundos..."):
                # O PROMPT MESTRE QUE VOCÊ PEDIU
                prompt_automacao = f"""
                Divida este roteiro em cenas de no máximo 6 segundos de narração.
                Para cada cena, extraia:
                1. Legenda: (Frase curta para o CapCut)
                2. Prompt Flux: (Prompt visual detalhado em Inglês para o Google Flow)
                3. Prompt Grok: (Instrução de movimento em Inglês para animar a imagem por 6s)

                ROTEIRO: {texto_para_processar}
                
                Retorne no formato:
                [CENA X]
                Legenda: "..."
                Flux: "..."
                Grok: "..."
                """
                
                resultado = client_gemini.models.generate_content(model="gemini-2.0-flash", contents=prompt_automacao)
                
                st.subheader("📋 Sua Linha de Produção")
                st.text_area("Resultado Final (Copie para o CapCut):", value=resultado.text, height=400)
                
                # ZIP de Segurança
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zf:
                    zf.writestr("producao_capcut.txt", resultado.text)
                
                st.download_button("📦 Baixar Kit (.txt)", zip_buffer.getvalue(), "producao_capcut.zip")