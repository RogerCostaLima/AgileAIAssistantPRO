# app.py
import streamlit as st
import json
from ia_models import gerar_resposta_gemini, gerar_resposta_gpt, gerar_resposta_copilot
from utils import exportar_artefatos, baixar_excel, extrair_texto_ppt
from fpdf import FPDF # type: ignore
import io
import pandas as pd

# =====================
# CONFIGURAÇÃO DE ESTILO E CORES PREMIUM
# =====================

# Paleta de Cores Premium (Harmonizada)
CORES = {
    "epic": "#4A70A7",    # Azul Sóbrio - Visão
    "feature": "#FF9800", # Laranja de Ação - Bloco
    "user_story": "#2196F3", # Azul Claro Profissional - Detalhe
    "task": "#4CAF50"    # Verde de Conclusão - Execução
}
EMOJIS = {
    "epic": "👑",
    "feature": "🚀",
    "user_story": "✍️",
    "task": "🛠️"
}
ARTEFATOS = ["epic", "feature", "user_story", "task"]

st.set_page_config(page_title="Assistente Ágil IA Premium", layout="wide", page_icon="⚡")

# Custom CSS para o toque premium, os cards de fluxo e a CORREÇÃO VISUAL DO TEXTO GERADO
st.markdown("""
<style>
/* Título Principal Impactante */
.stApp > header {
    background-color: transparent;
}
.big-font {
    font-size:30px !important;
    font-weight: bold;
    color: #4A70A7; /* Cor principal - Azul Sóbrio */
    text-shadow: 2px 2px 4px #ccc;
}
/* Estilo para os Cards de Fluxo */
.stContainer {
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.1);
    transition: 0.3s;
}
.stContainer:hover {
    box-shadow: 0 8px 16px 0 rgba(0, 0, 0, 0.2);
}
/* Ajuste de espaçamento para o sidebar */
[data-testid="stSidebarContent"] {
    padding-top: 2rem;
}
/* CORREÇÃO: Estilo para a caixa de texto gerado (com quebra de linha) */
.generated-text-box {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 5px;
    white-space: pre-wrap; /* Garante quebras de linha e formatação Markdown */
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)


CONFIG_FILE = "config.json"
try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    st.error("Arquivo config.json não encontrado. Crie um antes de rodar o app.")
    st.stop()

# =====================
# FUNÇÃO PARA EXPORTAR PDF
# (Adaptada com as novas cores)
# =====================
def exportar_pdf(resultados, filename="artefatos.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.add_page()
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(74, 112, 167) # Nova cor principal
    pdf.cell(0, 15, "ARTEFATOS ÁGEIS GERADOS POR IA ⚡", ln=True, align='C')
    pdf.ln(10)
    
    for tipo, conteudo in resultados.items():
        pdf.set_fill_color(240, 245, 255) # Fundo levemente azul
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 0, 0)
        
        pdf.cell(0, 8, f"{EMOJIS.get(tipo, '')} {tipo.upper()}", ln=True, fill=True)
        
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(50, 50, 50)
        
        try:
            conteudo_str = conteudo.encode('latin-1', 'replace').decode('latin-1')
        except:
            conteudo_str = conteudo 
            
        pdf.multi_cell(0, 6, conteudo_str)
        pdf.ln(5)
    
    buffer = io.BytesIO()
    pdf.output(buffer, dest='S')
    buffer.seek(0)
    return buffer

# =====================
# CONFIGURAÇÕES DE IA (Sidebar)
# =====================
with st.sidebar:
    st.header("🎯 **Ciclo de Refinamento Ágil**")
    st.markdown("---")
    menu_option = st.radio(
        "Navegação Rápida",
        ["🧠 Geração de Artefatos", "⚙️ Configurações de IA", "📂 Exportação", "ℹ️ Sobre"]
    )
    st.markdown("---")
    if "resultados" in st.session_state:
        st.success("✅ Artefatos prontos para exportação!")

# =========================================================================================
# GERAÇÃO DE ARTEFATOS (Principal)
# =========================================================================================
if menu_option == "🧠 Geração de Artefatos":
    st.markdown('<p class="big-font">⚡ Assistente Ágil IA - Refinamento Acelerado</p>', unsafe_allow_html=True)
    st.info("Defina o escopo, gere o ciclo completo de artefatos ágeis e prepare-se para o *sprint*.")
    
    st.markdown("---")

    # --- 1. Input do Usuário (Layout aprimorado) ---
    st.subheader("1. 📝 Defina o Escopo")
    
    col_contexto, col_notas = st.columns(2)
    with col_contexto:
        contexto = st.text_area("🧩 Contexto principal do projeto", height=150, help="Descreva o projeto, produto ou funcionalidade principal.", key="input_contexto")
    
    with col_notas:
        notas = st.text_area("📝 Notas e Diretrizes adicionais", height=150, help="Informações extras, restrições ou público-alvo.", key="input_notas")

    col_model, col_button = st.columns([2, 1])
    with col_model:
        modelo_escolhido = st.selectbox("🧠 Modelo de IA para Geração", ["Gemini", "ChatGPT", "Copilot"], help="Selecione o LLM desejado.", key="select_model")
    with col_button:
        st.write("") 
        gerar = st.button("🚀 INICIAR GERAÇÃO DE ARTEFATOS", type="primary", use_container_width=True)

    st.markdown("---")
    
    # --- 2. Processamento e Fluxo Visual (Cards Premium Limpos) ---
    st.subheader("2. 💡 Visualização do Ciclo")
    
    cols_flow = st.columns(len(ARTEFATOS))
    
    # Lista de placeholders para os cards serem atualizados
    card_placeholders = []
    
    # Inicializa os cards fixos (sem repetição)
    for i, tipo in enumerate(ARTEFATOS):
        with cols_flow[i]:
            # Cria um container placeholder para o card
            card_ph = st.empty()
            card_placeholders.append(card_ph)
            
            # Desenha o estado inicial do card
            with card_ph.container(border=True):
                emoji = EMOJIS[tipo]
                cor = CORES[tipo]
                titulo = tipo.upper()
                
                is_done = "resultados" in st.session_state and tipo in st.session_state["resultados"]
                
                st.markdown(f"**<span style='color:{cor};'>{emoji} {titulo}</span>**", unsafe_allow_html=True)
                if is_done:
                     st.caption("✅ Concluído")
                else:
                    st.caption("⚪ Não iniciado")
                    
    st.markdown("---")

    if gerar:
        if not contexto:
            st.error("⚠️ O campo 'Contexto principal do projeto' é obrigatório. Por favor, preencha para iniciar a geração.")
        else:
            resultados = {}
            
            # NOVO TÍTULO DE RESUMO
            st.subheader("3. ⏳ Processo de Geração Inteligente")
            st.markdown(f"Analisando **contexto** e **playbook** ({modelo_escolhido})...")
            
            # Loop de geração
            for i, tipo in enumerate(ARTEFATOS):
                
                # --- ATUALIZAÇÃO DO CARD: Estado 'Processando' ---
                with card_placeholders[i].container(border=True):
                    st.markdown(f"**<span style='color:{CORES[tipo]};'>{EMOJIS[tipo]} {tipo.upper()}</span>**", unsafe_allow_html=True)
                    st.caption("⚡ Processando...")
                
                # NOVO CONTEÚDO PARA ST.STATUS
                with st.status(f"{EMOJIS[tipo]} Gerando **{tipo.upper()}** com {modelo_escolhido}...", expanded=False, state="running") as status:
                    
                    st.write(f"**{EMOJIS[tipo]} PASSO 1/3: Construindo Prompt (contextualizando {tipo.upper()}).**")
                    
                    prompt_final = f"{config.get('ia_role','')}\n\n"
                    if "playbook_text" in config:
                        prompt_final += f"Playbook/Diretriz: {config['playbook_text']}\n\n"
                    prompt_final += f"{config['prompts'][tipo]}\n\nContexto:\n{contexto}\nNotas:\n{notas}"
                    
                    st.write(f"**{EMOJIS[tipo]} PASSO 2/3: Invocando Modelo de IA ({modelo_escolhido}).**")
                    
                    try:
                        # Chamada IA
                        if modelo_escolhido == "Gemini":
                            resposta = gerar_resposta_gemini(prompt_final, config["api_keys"]["gemini"])
                        elif modelo_escolhido == "ChatGPT":
                            resposta = gerar_resposta_gpt(prompt_final, config["api_keys"]["chatgpt"])
                        else:
                            resposta = gerar_resposta_copilot(prompt_final, config["api_keys"]["copilot"])
                            
                        resultados[tipo] = resposta
                        
                        st.write(f"**{EMOJIS[tipo]} PASSO 3/3: Artefato recebido e validado.**")
                        status.update(label=f"✅ **{tipo.upper()}** - Geração Finalizada!", state="complete", expanded=False)
                        
                        # --- ATUALIZAÇÃO DO CARD: Estado 'Concluído' ---
                        with card_placeholders[i].container(border=True):
                            st.markdown(f"**<span style='color:{CORES[tipo]};'>{EMOJIS[tipo]} {tipo.upper()}</span>**", unsafe_allow_html=True)
                            st.caption("✅ Concluído com sucesso")
                        
                    except Exception as e:
                        resposta = f"Erro ao gerar {tipo.upper()}: {e}"
                        resultados[tipo] = resposta
                        
                        st.write(f"**{EMOJIS[tipo]} ERRO FATAL: Falha na comunicação com a API.**")
                        status.update(label=f"❌ Erro ao gerar {tipo.upper()}", state="error", expanded=True)
                        st.exception(e)
                        
                        # --- ATUALIZAÇÃO DO CARD: Estado 'Erro' ---
                        with card_placeholders[i].container(border=True):
                            st.markdown(f"**<span style='color:{CORES[tipo]};'>{EMOJIS[tipo]} {tipo.upper()}</span>**", unsafe_allow_html=True)
                            st.caption("❌ Erro de Geração")
                        
            st.session_state["resultados"] = resultados
            st.toast("🚀 Geração de Artefatos Completa!", icon='🎉')
            
    # --- 3. Exibição dos Detalhes (Correção de Funcionalidade Visual) ---
    if "resultados" in st.session_state:
        st.markdown("## 4. 📖 Detalhes dos Artefatos")
        st.success("Visualize os resultados e vá para 'Exportação' para baixar a planilha!")
        
        tabs = st.tabs([f"{EMOJIS[tipo]} {tipo.upper()}" for tipo in ARTEFATOS])
        
        for i, tipo in enumerate(ARTEFATOS):
            with tabs[i]:
                st.subheader(f"Conteúdo do {tipo.upper()}")
                
                # Usa a classe CSS para quebrar linha e dar o visual premium
                conteudo = st.session_state["resultados"].get(tipo, "Não gerado ou erro.")
                
                # Aplica o estilo de caixa de texto com a cor da borda do artefato
                st.markdown(f"<div class='generated-text-box' style='border-left: 5px solid {CORES[tipo]};'>{conteudo}</div>", unsafe_allow_html=True)

# =====================
# CONFIGURAÇÕES
# =====================
elif menu_option == "⚙️ Configurações de IA":
    st.title("⚙️ Configurações Avançadas da IA")
    st.markdown("Organize as chaves de API, defina o papel da IA e personalize os prompts.")
    
    # Organização por abas
    tab_ia_role, tab_playbook, tab_prompts = st.tabs(["🔑 Chaves e Papel da IA", "📄 Playbook", "💬 Prompts Padrão"])
    
    with tab_ia_role:
        st.subheader("API Keys (Chaves de Acesso)")
        col_api1, col_api2, col_api3 = st.columns(3)
        
        keys_list = list(config["api_keys"].keys())
        for i, key in enumerate(keys_list):
            with [col_api1, col_api2, col_api3][i % 3]:
                config["api_keys"][key] = st.text_input(f"{key.upper()} API Key", value=config["api_keys"].get(key, ""), type="password")

        st.subheader("🤖 Papel da IA (System Role)")
        config["ia_role"] = st.text_area("Descreva como a IA deve atuar", value=config.get("ia_role",""), height=100, 
                                          help="Ex: 'Você é um Product Owner sênior, focado em clareza e detalhamento técnico...'")

    with tab_playbook:
        st.subheader("📄 Upload de Playbook ou Documentação")
        arquivo_ppt = st.file_uploader("Upload de Playbook em PPTX (opcional)", type=["pptx"])
        if arquivo_ppt:
            with st.spinner("Processando e extraindo texto do Playbook..."):
                config["playbook_text"] = extrair_texto_ppt(arquivo_ppt)
            st.success("Playbook carregado e processado com sucesso! A IA usará este texto como diretriz.")
        elif "playbook_text" in config and config["playbook_text"]:
             st.info("Playbook atual carregado. Faça um novo upload para substituir ou modifique o texto diretamente na config.json.")

    with tab_prompts:
        st.subheader("💬 Prompts Padrão por Artefato")
        for p in ARTEFATOS:
            st.markdown(f"**{EMOJIS.get(p, '💬')} Prompt para {p.upper()}**")
            config["prompts"][p] = st.text_area(f"Prompt base para {p.upper()}", value=config["prompts"].get(p, ""), height=120, label_visibility="collapsed")

    if st.button("💾 Salvar Todas as Configurações", type="primary", use_container_width=True):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        st.success("✅ Configurações salvas com sucesso! As alterações serão aplicadas na próxima geração.")

# =====================
# SOBRE
# =====================
elif menu_option == "ℹ️ Sobre":
    st.title("💡 O Conceito por Trás do Assistente Ágil IA")
    st.markdown("""
    Este assistente é a sua **ferramenta definitiva** para otimizar o processo de criação de artefatos ágeis. 
    
    ### 🎯 Nosso Objetivo
    Reduzir o tempo gasto em detalhamento e documentação, permitindo que o time se concentre na **entrega de valor**.
    
    ---
    
    #### 👑 EPIC (Visão)
    Define o objetivo de alto nível.
    
    #### 🚀 FEATURE (Solução)
    O grande bloco de funcionalidades necessário para alcançar o Epic.
    
    #### ✍️ USER STORY (Valor)
    O detalhe da funcionalidade do ponto de vista do usuário final.
    
    #### 🛠️ TASK (Execução)
    As atividades técnicas necessárias para implementar a User Story.
    
    ---
    
    **Desenvolvido com 💛 e Python/Streamlit.**
    """)

# =====================
# EXPORTAÇÃO
# =====================
elif menu_option == "📂 Exportação":
    st.title("📂 Preparar para o Azure DevOps / Documentação")
    st.info("Seus artefatos estão prontos. Baixe a planilha Excel para importação e o PDF para registro formal.")
    
    if "resultados" not in st.session_state:
        st.warning("⚠️ Gere os artefatos no menu 'Geração de Artefatos' antes de exportar.")
    else:
        df = exportar_artefatos(st.session_state["resultados"])
        
        st.subheader("Tabela de Artefatos Gerados")
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Baixar Excel (.xlsx) para Azure DevOps",
                data=baixar_excel(df),
                file_name="artefatos_agile_premium.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col2:
            try:
                pdf_buffer = exportar_pdf(st.session_state["resultados"])
                st.download_button(
                    label="📥 Baixar PDF para Documentação",
                    data=pdf_buffer,
                    file_name="artefatos_agile_premium.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}. Verifique as permissões de codificação de texto.")