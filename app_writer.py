import streamlit as st
import io
import zipfile
from google import genai
from google.genai import types
from supabase import create_client, Client

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Fábrica 23.0 - Sequencial", layout="wide", page_icon="🧬")
st.title("🧬 Fábrica 23.0 - Gerador Evolutivo de Histórias")
st.markdown("*Crie sua história parte por parte com automação total de prompts.*")

# --- CONEXÃO SEGURA ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    supa_url = st.secrets["supabase"]["url"]
    supa_key = st.secrets["supabase"]["key"]
    client_gemini = genai.Client(api_key=api_key)
    supabase: Client = create_client(supa_url, supa_key)
except Exception as e:
    st.error("Erro nas chaves! Verifique os Secrets.")
    st.stop()

# --- ESTADO DA SESSÃO (MEMÓRIA TEMPORÁRIA) ---
if 'historia_partes' not in st.session_state:
    st.session_state['historia_partes'] = []
if 'contexto_acumulado' not in st.session_state:
    st.session_state['contexto_acumulado'] = ""

# --- INTERFACE ---
with st.sidebar:
    st.header("🎬 O Plot")
    ideia_geral = st.text_area("Ideia Geral (Início, Meio e Fim):", height=150)
    dna_visual = st.text_area("🧬 DNA Visual:", placeholder="Descrição dos personagens para os prompts...")
    
    if st.button("🗑️ Resetar História"):
        st.session_state['historia_partes'] = []
        st.session_state['contexto_acumulado'] = ""
        st.rerun()

# --- FLUXO DE GERAÇÃO ---
st.header("🚀 Linha de Produção")

if not ideia_geral:
    st.info("👈 Comece descrevendo sua ideia geral na barra lateral.")
else:
    # Botão para gerar a PRÓXIMA parte
    num_parte = len(st.session_state['historia_partes']) + 1
    
    if st.button(f"✨ Gerar Parte {num_parte}"):
        with st.spinner(f"Escrevendo e processando a Parte {num_parte}..."):
            
            # PROMPT EVOLUTIVO
            prompt_evolutivo = f"""
            VOCÊ É UM ESCRITOR E DIRETOR.
            ESTA É A IDEIA GERAL: {ideia_geral}
            ESTE É O CONTEXTO DO QUE JÁ FOI ESCRITO: {st.session_state['contexto_acumulado']}
            
            SUA TAREFA:
            1. Escreva a PARTE {num_parte} da história. Ela deve ser focada em romance e drama, preparando o terreno para o que vem depois.
            2. Pegue essa Parte {num_parte} e transforme em um kit de produção:
               - Divida em cenas (legendas de no máximo 15 palavras).
               - Para cada cena: 2 Prompts Flux (Inglês) + 1 Prompt Grok (Movimento em Inglês).
            
            DNA VISUAL: {dna_visual}
            
            FORMATO DE SAÍDA:
            [TEXTO NARRATIVO DA PARTE {num_parte}]
            (Escreva aqui o texto da história em parágrafos)

            [KIT DE PRODUÇÃO]
            Cena 1 | Legenda: "..." | Flux 1: "..." | Flux 2: "..." | Grok: "..."
            Cena 2 | Legenda: "..." | Flux 1: "..." | Flux 2: "..." | Grok: "..."
            """
            
            response = client_gemini.models.generate_content(model="gemini-2.0-flash", contents=prompt_evolutivo)
            output = response.text
            
            # Adiciona ao histórico
            st.session_state['historia_partes'].append(output)
            st.session_state['contexto_acumulado'] += f"\n\nPARTE {num_parte}:\n{output}"

    # EXIBIÇÃO DAS PARTES GERADAS
    for i, conteudo in enumerate(st.session_state['historia_partes']):
        with st.expander(f"📦 CONTEÚDO DA PARTE {i+1}", expanded=True):
            st.markdown(conteudo)
            
            # Botão de Download para esta parte específica
            st.download_button(
                label=f"📥 Baixar Kit Parte {i+1}",
                data=conteudo,
                file_name=f"parte_{i+1}_producao.txt",
                key=f"btn_{i}"
            )

if st.session_state['historia_partes']:
    st.divider()
    st.success(f"✅ {len(st.session_state['historia_partes'])} partes prontas para produção!")
