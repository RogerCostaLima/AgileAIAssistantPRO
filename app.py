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
# =====================
def exportar_pdf(resultados, filename="artefatos.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Artefatos Ágeis", ln=True, align='C')
    pdf.ln(10)
    
    for tipo, conteudo in resultados.items():
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 8, tipo.upper(), ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 6, conteudo)
        pdf.ln(5)
    
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# =====================
# CONFIGURAÇÕES DE IA
# =====================
st.sidebar.title("📌 Ciclo de Refinamento Ágil")

menu_option = st.sidebar.radio(
    "Menu",
    ["🧠 Geração de Artefatos", "⚙️ Configurações de IA", "📂 Exportação", "ℹ️ Sobre"]
)

# =====================
# CONFIGURAÇÕES
# =====================
if menu_option == "⚙️ Configurações de IA":
    st.header("Configurações Avançadas da IA")
    st.subheader("API Keys")
    for key in config["api_keys"]:
        config["api_keys"][key] = st.text_input(f"{key.upper()} API Key", value=config["api_keys"][key], type="password")

    st.subheader("Como a IA deve atuar")
    config["ia_role"] = st.text_area("Descreva como a IA deve atuar", value=config.get("ia_role",""), height=80)

    arquivo_ppt = st.file_uploader("📄 Upload de Playbook em PPT (opcional)", type=["pptx"])
    if arquivo_ppt:
        config["playbook_text"] = extrair_texto_ppt(arquivo_ppt)
        st.success("Playbook carregado e processado com sucesso!")

    st.subheader("Prompts Padrão por Artefato")
    for p in config["prompts"]:
        config["prompts"][p] = st.text_area(f"Prompt para {p.upper()}", value=config["prompts"][p], height=100)

    if st.button("💾 Salvar Configurações"):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        st.success("✅ Configurações salvas com sucesso!")

# =====================
# SOBRE
# =====================
elif menu_option == "ℹ️ Sobre":
    st.title("🤖 Assistente Ágil IA")
    st.markdown("""
    - Gerencie o Ciclo de Refinamento
    - Fluxo visual do Epic até a Task
    - Exportação em Excel e PDF pronta para Azure DevOps
    """)

# =====================
# GERAÇÃO DE ARTEFATOS COM FLUXO VISUAL
# =====================
elif menu_option == "🧠 Geração de Artefatos":
    st.title("🧠 Gerencie o Ciclo de Refinamento")
    st.info("Defina o escopo, monitore o progresso e planeje os próximos ciclos. O fluxo visual ajuda a acompanhar do Epic até a Task.")

    contexto = st.text_area("🧩 Contexto do projeto", height=100)
    notas = st.text_area("📝 Notas adicionais (opcional)", height=80)
    modelo_escolhido = st.selectbox("Selecione o Modelo de IA", ["Gemini", "ChatGPT", "Copilot"])
    gerar = st.button("🚀 Gerar Artefatos")

    artefatos = ["epic", "feature", "user_story", "task"]
    emojis = ["", "", "", ""]
    cores = ["#FFD700", "#FF8C00", "#00BFFF", "#32CD32"]
    status_gerado = {}

    # Estrutura visual do ciclo
    if gerar:
        if not contexto:
            st.warning("Preencha o contexto do projeto antes de gerar.")
        else:
            resultados = {}
            for i, tipo in enumerate(artefatos):
                st.markdown(f"<div style='display:flex;align-items:center;'>"
                            f"<div style='width:20px;height:20px;background-color:{cores[i]};border-radius:50%;margin-right:10px;'></div>"
                            f"<h4 style='margin:0;'>{i+1} - {emojis[i]} {tipo.upper()} ⏳ Processando...</h4>"
                            f"</div>", unsafe_allow_html=True)

                prompt_final = f"{config.get('ia_role','')}\n\n"
                if "playbook_text" in config:
                    prompt_final += f"{config['playbook_text']}\n\n"
                prompt_final += f"{config['prompts'][tipo]}\n\nContexto:\n{contexto}\nNotas:\n{notas}"

                # Chamada IA
                if modelo_escolhido == "Gemini":
                    resposta = gerar_resposta_gemini(prompt_final, config["api_keys"]["gemini"])
                elif modelo_escolhido == "ChatGPT":
                    resposta = gerar_resposta_gpt(prompt_final, config["api_keys"]["chatgpt"])
                else:
                    resposta = gerar_resposta_copilot(prompt_final, config["api_keys"]["copilot"])

                resultados[tipo] = resposta
                status_gerado[tipo] = True

            st.session_state["resultados"] = resultados

    # Mostrar artefatos gerados com expanders e check
    if "resultados" in st.session_state:
        st.markdown("---")
        st.subheader("📂 Artefatos Gerados")
        for i, tipo in enumerate(artefatos):
            emoji = emojis[i]
            cor = cores[i]
            gerado = "✅" if tipo in status_gerado and status_gerado[tipo] else ""
            with st.expander(f"{i+1} - {emoji} {tipo.upper()} {gerado}"):
                st.markdown(f"<div style='border-left:5px solid {cor}; padding-left:10px'>{st.session_state['resultados'].get(tipo,'')}</div>", unsafe_allow_html=True)

# =====================
# EXPORTAÇÃO
# =====================
elif menu_option == "📂 Exportação":
    st.title("📂 Exportar Artefatos")
    if "resultados" not in st.session_state:
        st.warning("Gere os artefatos antes de exportar.")
    else:
        df = exportar_artefatos(st.session_state["resultados"])
        st.dataframe(df)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Baixar Excel",
                data=baixar_excel(df),
                file_name="artefatos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with col2:
            st.download_button(
                label="📥 Baixar PDF",
                data=exportar_pdf(st.session_state["resultados"]),
                file_name="artefatos.pdf",
                mime="application/pdf"
            )
