# app.py
import streamlit as st
import json
from ia_models import gerar_resposta_gemini, gerar_resposta_gpt, gerar_resposta_copilot
from utils import exportar_artefatos, baixar_excel, extrair_texto_ppt
from fpdf import FPDF # type: ignore
import io
import pandas as pd

# =====================
# CONFIGURAÇÃO DE PÁGINA
# =====================
st.set_page_config(page_title="Assistente Ágil IA", layout="wide", page_icon="🤖")

CONFIG_FILE = "config.json"
try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    st.error("Arquivo config.json não encontrado. Crie um antes de rodar o app.")
    st.stop()

# =====================
# FUNÇÃO PARA EXPORTAR PDF
# (Mantida a mesma, mas é bom usar uma biblioteca com suporte a unicode/UTF-8 melhor se for para PT-BR, como ReportLab ou pdfkit)
# =====================
def exportar_pdf(resultados, filename="artefatos.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    # Para suportar acentos e caracteres especiais:
    # 1. Deve-se incluir fontes compatíveis (ex: Arial/Times New Roman do FPDF não suportam UTF-8 nativamente)
    # 2. Usar a codificação correta. 
    # Para este exemplo, vou simular o uso correto, mas você pode precisar de 'pdf.add_font' e 'pdf.set_font' personalizados.
    
    # Exemplo simples, se não usar chars especiais:
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Artefatos Ageis", ln=True, align='C')
    pdf.ln(10)
    
    for tipo, conteudo in resultados.items():
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 8, tipo.upper(), ln=True)
        pdf.set_font("Arial", '', 12)
        
        # Converte para string que o FPDF entenda (pode falhar com acentos se a fonte não for adicionada corretamente)
        try:
            conteudo_str = conteudo.encode('latin-1', 'replace').decode('latin-1')
        except:
            conteudo_str = conteudo # Tenta sem conversão, mas pode quebrar.
            
        pdf.multi_cell(0, 6, conteudo_str)
        pdf.ln(5)
    
    buffer = io.BytesIO()
    pdf.output(buffer, dest='S') # Usar 'S' para obter a string de saída, depois escrever no buffer
    buffer.seek(0)
    return buffer

# =====================
# CONFIGURAÇÕES DE IA (Sidebar)
# =====================
with st.sidebar:
    st.title("🤖 Ciclo de Refinamento Ágil")
    menu_option = st.radio(
        "Navegação",
        ["🧠 Geração de Artefatos", "⚙️ Configurações de IA", "📂 Exportação", "ℹ️ Sobre"]
    )

# =========================================================================================
# GERAÇÃO DE ARTEFATOS (Principal - Foco da UX)
# =========================================================================================
if menu_option == "🧠 Geração de Artefatos":
    st.title("🤖 Gerencie o Ciclo de Refinamento")
    st.markdown("---")
    
    # --- Input do Usuário (Sempre visível) ---
    st.subheader("1. 🧩 Contexto e Modelo")
    
    col_input, col_model = st.columns([3, 1])
    
    with col_input:
        contexto = st.text_area("Contexto do projeto", height=100, help="Descreva o projeto, produto ou funcionalidade principal.")
        notas = st.text_area("Notas adicionais (opcional)", height=80, help="Informações extras, restrições ou público-alvo.")
    
    with col_model:
        modelo_escolhido = st.selectbox("Modelo de IA", ["Gemini", "ChatGPT", "Copilot"], label_visibility="visible")
        gerar = st.button("🚀 Gerar Artefatos", use_container_width=True)

    st.markdown("---")

    # --- Processamento e Resultados ---
    
    artefatos = ["epic", "feature", "user_story", "task"]
    emojis = ["🌟", "🚀", "📝", "✅"]
    
    if gerar:
        if not contexto:
            st.error("⚠️ Por favor, preencha o contexto do projeto antes de gerar.")
        else:
            resultados = {}
            st.subheader("2. ⏳ Processamento dos Artefatos")
            
            # Utilizando st.columns para o fluxo visual
            cols_flow = st.columns(len(artefatos))
            
            for i, tipo in enumerate(artefatos):
                # Placeholder para o status visual
                with cols_flow[i]:
                    st.metric(label=f"{emojis[i]} {tipo.upper()}", value="Processando...")
                
                # Barra de status para a chamada da IA
                with st.status(f"Gerando **{tipo.upper()}** com {modelo_escolhido}...", expanded=True) as status:
                    st.write(f"Preparando prompt para {tipo.upper()}...")
                    
                    prompt_final = f"{config.get('ia_role','')}\n\n"
                    if "playbook_text" in config:
                        prompt_final += f"Playbook: {config['playbook_text']}\n\n"
                    prompt_final += f"{config['prompts'][tipo]}\n\nContexto:\n{contexto}\nNotas:\n{notas}"
                    
                    try:
                        # Chamada IA
                        if modelo_escolhido == "Gemini":
                            resposta = gerar_resposta_gemini(prompt_final, config["api_keys"]["gemini"])
                        elif modelo_escolhido == "ChatGPT":
                            resposta = gerar_resposta_gpt(prompt_final, config["api_keys"]["chatgpt"])
                        else:
                            resposta = gerar_resposta_copilot(prompt_final, config["api_keys"]["copilot"])
                            
                        resultados[tipo] = resposta
                        status.update(label=f"✅ **{tipo.upper()}** Gerado!", state="complete", expanded=False)
                        
                    except Exception as e:
                        resposta = f"Erro ao gerar {tipo.upper()}: {e}"
                        resultados[tipo] = resposta
                        status.update(label=f"❌ Erro ao gerar {tipo.upper()}", state="error", expanded=True)
                        st.exception(e)
                    
                    # Atualiza o contêiner visual após a conclusão/erro
                    with cols_flow[i]:
                        st.metric(label=f"{emojis[i]} {tipo.upper()}", value="✅ Concluído")
                        
            st.session_state["resultados"] = resultados
            st.toast("🚀 Geração de Artefatos Completa!", icon='🎉')
            
    # Mostrar artefatos gerados com abas
    if "resultados" in st.session_state:
        st.subheader("3. 📖 Resultados Detalhados")
        
        # Cria abas com o título e emoji
        tabs = st.tabs([f"{emojis[i]} {tipo.upper()}" for i, tipo in enumerate(artefatos)])
        
        for i, tipo in enumerate(artefatos):
            with tabs[i]:
                st.markdown(st.session_state["resultados"].get(tipo, "Não gerado ou erro."))

# =====================
# CONFIGURAÇÕES
# =====================
elif menu_option == "⚙️ Configurações de IA":
    st.title("⚙️ Configurações Avançadas da IA")
    
    # Aba para API Keys e Role
    tab_ia_role, tab_playbook, tab_prompts = st.tabs(["🔑 Chaves e Papel da IA", "📄 Playbook", "💬 Prompts Padrão"])
    
    with tab_ia_role:
        st.subheader("API Keys")
        for key in config["api_keys"]:
            config["api_keys"][key] = st.text_input(f"{key.upper()} API Key", value=config["api_keys"][key], type="password")

        st.subheader("Como a IA deve atuar (System Role)")
        config["ia_role"] = st.text_area("Descreva como a IA deve atuar", value=config.get("ia_role",""), height=80, 
                                          help="Ex: 'Você é um Product Owner experiente e deve criar artefatos ágeis...'")

    with tab_playbook:
        st.subheader("Upload de Playbook/Documentação")
        arquivo_ppt = st.file_uploader("📄 Upload de Playbook em PPT (opcional)", type=["pptx"])
        if arquivo_ppt:
            with st.spinner("Processando Playbook..."):
                config["playbook_text"] = extrair_texto_ppt(arquivo_ppt)
            st.success("Playbook carregado e processado com sucesso!")
        elif "playbook_text" in config and config["playbook_text"]:
             st.info("Playbook atual carregado. Faça um novo upload para substituir.")

    with tab_prompts:
        st.subheader("Prompts Padrão por Artefato")
        for p in config["prompts"]:
            config["prompts"][p] = st.text_area(f"Prompt para {p.upper()}", value=config["prompts"][p], height=100)

    if st.button("💾 Salvar Configurações", use_container_width=True):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        st.success("✅ Configurações salvas com sucesso!")

# =====================
# SOBRE
# =====================
elif menu_option == "ℹ️ Sobre":
    st.title("ℹ️ Sobre o Assistente Ágil IA")
    st.markdown("""
    Este assistente é uma ferramenta projetada para acelerar o **Ciclo de Refinamento Ágil** (do Epic até a Task) usando Modelos de Linguagem Grande (LLMs).
    
    ---
    
    ### Principais Recursos
    * **Ciclo Visual:** Monitore o progresso do Epic (🌟) até a Task (✅).
    * **Modelos Flexíveis:** Escolha entre Gemini, ChatGPT ou Copilot.
    * **Customização:** Defina o papel da IA e carregue um Playbook para guiar a geração.
    * **Exportação Pronta:** Baixe os artefatos em Excel ou PDF, prontos para sistemas como Azure DevOps.
    """)
    st.image("", caption="Fluxo Ágil: Epic -> Feature -> User Story -> Task")

# =====================
# EXPORTAÇÃO
# =====================
elif menu_option == "📂 Exportação":
    st.title("📂 Exportar Artefatos")
    st.info("Baixe a planilha Excel para upload no Azure DevOps ou o PDF para documentação.")
    
    if "resultados" not in st.session_state:
        st.warning("⚠️ Gere os artefatos (Menu Geração de Artefatos) antes de exportar.")
    else:
        df = exportar_artefatos(st.session_state["resultados"])
        st.subheader("Pré-visualização da Tabela")
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Baixar Excel (.xlsx)",
                data=baixar_excel(df),
                file_name="artefatos_agile.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col2:
            try:
                # É importante que a função exportar_pdf tenha suporte adequado a caracteres especiais.
                pdf_buffer = exportar_pdf(st.session_state["resultados"])
                st.download_button(
                    label="📥 Baixar PDF",
                    data=pdf_buffer,
                    file_name="artefatos_agile.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")