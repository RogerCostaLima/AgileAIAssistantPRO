import streamlit as st
import json
import os
import io
import pandas as pd
import time
from fpdf import FPDF # type: ignore
# Importação mock da biblioteca pptx, que seria usada para extração
# import { Presentation } from 'pptx'; // Mock

# ==============================================================================
# MOCKS PARA FUNÇÕES EXTERNAS (ia_models e utils)
# Estas funções simulam a lógica de IA e utilidades (Excel/PPTX)
# Para um ambiente real, você as implementaria em arquivos separados.
# ==============================================================================

def gerar_resposta_gemini(prompt, api_key):
    """MOCK: Simula a geração de resposta do Gemini."""
    if not api_key:
        raise ValueError("Chave Gemini não configurada.")
    time.sleep(0.5) 
    return f"**[GEMINI - EPIC]** Proposta de Épico Baseada em IA:\n\n*Tema:* {prompt[prompt.find('Contexto:')+10:prompt.find('Notas:')].strip()}\n\nO objetivo é focar em uma experiência de compra 'Premium' para o usuário."

def gerar_resposta_gpt(prompt, api_key):
    """MOCK: Simula a geração de resposta do ChatGPT."""
    if not api_key:
        raise ValueError("Chave ChatGPT não configurada.")
    time.sleep(0.5)
    return f"**[CHATGPT - FEATURE]** Proposta de Feature Baseada em IA:\n\n*Título:* Implementação de Pagamento Rápido via Pix.\n\nEsta feature reduzirá o atrito na etapa final do checkout."

def gerar_resposta_copilot(prompt, api_key):
    """MOCK: Simula a geração de resposta do Copilot."""
    if not api_key:
        raise ValueError("Chave Copilot não configurada.")
    time.sleep(0.5)
    return f"**[COPILOT - USER STORY]** Proposta de User Story Baseada em IA:\n\nComo um **usuário VIP**, eu quero **salvar meu endereço de entrega automaticamente**, para que **eu finalize compras com apenas um clique.**"

def extrair_texto_ppt(uploaded_file):
    """MOCK: Simula a extração de texto de um arquivo PPTX."""
    # A implementação real usaria `from pptx import Presentation`
    return "Playbook Mock: Nossas user stories devem seguir o formato 'Como [usuário], eu quero [objetivo], para que [benefício].' Detalhe critérios de aceitação rigorosamente."

def exportar_artefatos(resultados):
    """Cria um DataFrame a partir dos resultados para exportação."""
    data = {
        'Tipo': list(resultados.keys()),
        'Conteúdo': list(resultados.values())
    }
    # Adiciona colunas vazias para simular a estrutura Azure DevOps
    df = pd.DataFrame(data)
    df['Título Curto'] = df['Tipo'].apply(lambda x: x.upper()) + ' - ' + [f'Item {i}' for i in range(len(df))]
    return df[['Tipo', 'Título Curto', 'Conteúdo']]

def baixar_excel(df):
    """Cria um buffer de bytes para o download do Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Artefatos', index=False)
    output.seek(0)
    return output

# =====================
# CONFIGURAÇÃO DE ESTILO E CORES PREMIUM (COCA-COLA INSPIRED)
# ==========================================================

# Paleta de Cores
CORES_COCA = {
    "VERMELHO_PRIMARIO": "#E60000",
    "PRETO_SOLIDO": "#1A1A1A",
    "AMARELO_DOURADO": "#FFC300",
    "LARANJA_ESCURO": "#FF8C00",
    "FUNDO_CARD": "#FFF0F0" 
}

# Cores de Artefato mapeadas para a Paleta
CORES = {
    "epic": CORES_COCA["VERMELHO_PRIMARIO"],  
    "feature": CORES_COCA["AMARELO_DOURADO"], 
    "user_story": CORES_COCA["LARANJA_ESCURO"], 
    "task": CORES_COCA["PRETO_SOLIDO"]      
}
EMOJIS = {
    "epic": "👑",
    "feature": "🚀",
    "user_story": "✍️",
    "task": "🛠️"
}
ARTEFATOS = ["epic", "feature", "user_story", "task"]

st.set_page_config(page_title="Assistente Ágil IA Premium", layout="wide", page_icon="⚡")

# Custom CSS para o toque premium
st.markdown(f"""
<style>
/* 1. Reset e Cores de Fundo */
.stApp {{
    color: {CORES_COCA["PRETO_SOLIDO"]}; 
}}
.stApp > header {{
    background-color: transparent;
}}
/* 2. Estilo do Cabeçalho principal */
h1.st-emotion-cache-121aa6r, h1.css-1r6c0d8 {{ /* Adicionei classe genérica para robustez */
    color: {CORES_COCA["VERMELHO_PRIMARIO"]};
    font-size: 36px;
    border-bottom: 3px solid {CORES_COCA["VERMELHO_PRIMARIO"]};
    padding-bottom: 10px;
    margin-bottom: 20px;
}}
/* 3. Estilo para os Cards de Fluxo */
[data-testid="stVerticalBlock"] .stContainer {{
    border-radius: 10px;
    padding: 20px;
    background-color: {CORES_COCA["FUNDO_CARD"]}; 
    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.1);
    transition: 0.3s;
}}
[data-testid="stVerticalBlock"] .stContainer:hover {{
    box-shadow: 0 8px 16px 0 rgba(0, 0, 0, 0.2);
}}
/* Ajuste de espaçamento para o sidebar */
[data-testid="stSidebarContent"] {{
    padding-top: 2rem;
}}
/* ESTILO AJUSTADO: CORREÇÃO NO LAYOUT DO TEXTO DENTRO DOS RESULTADOS */
.generated-text-box {{
    background-color: white; 
    border: 1px solid #ddd;
    border-left: 5px solid {CORES_COCA["VERMELHO_PRIMARIO"]}; 
    padding: 15px;
    border-radius: 5px;
    white-space: pre-wrap; 
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.5; 
    margin-bottom: 10px; 
}}
/* Estilo para o TÍTULO DA ABA DE RESULTADOS */
.result-tab-title {{
    background-color: {CORES_COCA["PRETO_SOLIDO"]}; 
    color: white;
    font-size: 1.2em;
    font-weight: bold;
    padding: 8px 15px;
    border-radius: 5px 5px 0 0;
    margin-top: 10px;
}}
/* Cor do botão primário */
div.stButton > button.st-emotion-cache-nahz7x, div.stButton > button.st-bd {{ 
    background-color: {CORES_COCA["VERMELHO_PRIMARIO"]};
    color: white;
}}
</style>
""", unsafe_allow_html=True)


CONFIG_FILE = "config.json"

# Conteúdo inicial mínimo do config, caso não exista (para evitar erros de chave)
INITIAL_CONFIG = {
    "api_keys": {
        "gemini": "",
        "chatgpt": "",
        "copilot": ""
    },
    "ia_role": "Você é um Product Owner sênior, focado em clareza, detalhamento técnico e boas práticas ágeis. Seu objetivo é transformar o contexto fornecido em artefatos coesos, seguindo o playbook.",
    "prompts": {
        "epic": "Baseado no contexto, crie um EPIC (Épico) detalhado com o Título e a Descrição. Foco na visão de alto nível e no valor de negócio.", 
        "feature": "Baseado no EPIC e no contexto, crie uma FEATURE (Funcionalidade) com Título, Descrição e Critérios de Aceitação.",
        "user_story": "Baseado na FEATURE e no contexto, crie uma lista de 3 User Stories no formato 'Como <Tipo de Usuário>, eu quero <Meta>, para que <Benefício>' com Critérios de Aceitação claros.",
        "task": "Baseado na primeira User Story criada, detalhe 5 TASKS (Tarefas) técnicas ou não-funcionais necessárias para sua implementação (Ex: Design, Backend, Testes, Documentação)."
    }
}


try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    # Se não encontrar, cria o arquivo com a configuração inicial
    st.warning("Arquivo config.json não encontrado. Criando um arquivo padrão.")
    config = INITIAL_CONFIG
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
except json.JSONDecodeError:
    st.error("Erro ao ler config.json. O arquivo pode estar corrompido. Usando configurações padrão.")
    config = INITIAL_CONFIG


# =====================
# NOVA FUNÇÃO: Restaurar chaves e recarregar app
# =====================
def restaurar_chaves_api():
    """Restaura as chaves de API para valores vazios no config.json e reinicia o Streamlit."""
    
    # Cria uma cópia da configuração atual para não apagar 'ia_role' ou 'prompts'
    config_to_save = config.copy()
    
    # Define as chaves de API para strings vazias (o objetivo de segurança)
    config_to_save["api_keys"]["gemini"] = ""
    config_to_save["api_keys"]["chatgpt"] = ""
    config_to_save["api_keys"]["copilot"] = ""
    
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_to_save, f, indent=4, ensure_ascii=False)
        
        st.toast("✅ Chaves de API restauradas! Recarregando o aplicativo...", icon='🔒')
        # Método para forçar o recarregamento no Streamlit
        st.rerun() 
        
    except Exception as e:
        st.error(f"❌ Erro ao restaurar as chaves: {e}")

# =====================
# FUNÇÃO PARA EXPORTAR PDF (CORRIGIDA - SEM EMOJIS)
# =====================
def exportar_pdf(resultados, filename="artefatos.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.add_page()
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(230, 0, 0) 
    
    # 1. Título principal do PDF sem emojis
    pdf.cell(0, 15, "ARTEFATOS ÁGEIS GERADOS POR IA", ln=True, align='C') 
    pdf.ln(10)
    
    for tipo, conteudo in resultados.items():
        pdf.set_fill_color(255, 240, 240) 
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 0, 0)
        
        # 2. Título do Artefato sem emojis (uso de .upper() garante o nome)
        pdf.cell(0, 8, f"{tipo.upper()}", ln=True, fill=True)
        
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(50, 50, 50)
        
        try:
            # Garante que o conteúdo seja lido, mesmo com possíveis problemas de codificação
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
    st.header(f"🎯 **Ciclo de Refinamento Ágil**")
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
    
    st.title("⚡ Assistente Ágil IA - Refinamento Acelerado")
    st.info("Defina o escopo, gere o ciclo completo de artefatos ágeis e prepare-se para o *sprint*.")
    
    st.markdown("---")

    # --- 1. Defina o Escopo (COM EXPANDER) ---
    with st.expander("1. 📝 **Defina o Escopo** (Clique para expandir)", expanded=True):
        col_contexto, col_notas = st.columns(2)
        with col_contexto:
            # Usa o valor do session_state para persistir após st.rerun
            if "input_contexto" not in st.session_state:
                st.session_state["input_contexto"] = ""
            contexto = st.text_area("🧩 Contexto principal do projeto", value=st.session_state["input_contexto"], height=150, help="Descreva o projeto, produto ou funcionalidade principal.", key="input_contexto")
        
        with col_notas:
            if "input_notas" not in st.session_state:
                st.session_state["input_notas"] = ""
            notas = st.text_area("📝 Notas e Diretrizes adicionais", value=st.session_state["input_notas"], height=150, help="Informações extras, restrições ou público-alvo.", key="input_notas")

        col_model, col_button = st.columns([2, 1])
        with col_model:
            modelo_escolhido = st.selectbox("🧠 Modelo de IA para Geração", ["Gemini", "ChatGPT", "Copilot"], help="Selecione o LLM desejado.", key="select_model")
        with col_button:
            st.write("") 
            gerar = st.button("🚀 INICIAR GERAÇÃO DE ARTEFATOS", type="primary", use_container_width=True)

    st.markdown("---")
    
    # --- 2. Visualização do Ciclo (COM EXPANDER) ---
    with st.expander("2. 💡 **Visualização do Ciclo** (Clique para acompanhar)", expanded=True):
        cols_flow = st.columns(len(ARTEFATOS))
        
        card_placeholders = []
        
        # Inicializa os cards fixos (sem repetição)
        for i, tipo in enumerate(ARTEFATOS):
            with cols_flow[i]:
                card_ph = st.empty()
                card_placeholders.append(card_ph)
                
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
            
            # --- 3. Processo de Geração Inteligente (COM EXPANDER) ---
            with st.expander("3. ⏳ **Processo de Geração Inteligente** (Detalhes)", expanded=True):
                st.markdown(f"Analisando **contexto** e **playbook** ({modelo_escolhido})...")
                
                # Loop de geração
                for i, tipo in enumerate(ARTEFATOS):
                    
                    # --- ATUALIZAÇÃO DO CARD: Estado 'Processando' ---
                    with card_placeholders[i].container(border=True):
                        st.markdown(f"**<span style='color:{CORES[tipo]};'>{EMOJIS[tipo]} {tipo.upper()}</span>**", unsafe_allow_html=True)
                        st.caption("⚡ Processando...")
                    
                    # Usa st.status para feedback detalhado
                    with st.status(f"{EMOJIS[tipo]} Gerando **{tipo.upper()}** com {modelo_escolhido}...", expanded=False, state="running") as status:
                        
                        st.write(f"**{EMOJIS[tipo]} PASSO 1/3: Construindo Prompt (contextualizando {tipo.upper()}).**")
                        
                        prompt_final = f"{config.get('ia_role','')}\n\n"
                        if "playbook_text" in config:
                            prompt_final += f"Playbook/Diretriz: {config['playbook_text']}\n\n"
                        
                        # Garante que o prompt seja específico para o tipo de artefato
                        prompt_final += f"{config['prompts'].get(tipo, 'Gere um artefato.')}\n\nContexto:\n{contexto}\nNotas:\n{notas}"
                        
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
                            
                        except ValueError as ve:
                             # Captura a exceção de chave não configurada
                            resposta = f"Erro de Configuração: {ve}. Por favor, configure sua chave de API na seção 'Configurações de IA'."
                            resultados[tipo] = resposta
                            st.write(f"**{EMOJIS[tipo]} ERRO FATAL: Chave de API ausente.**")
                            status.update(label=f"❌ Erro ao gerar {tipo.upper()} (Chave ausente)", state="error", expanded=True)
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
            
            st.markdown("---") # Separador após a conclusão da geração

    # --- 4. Exibição dos Detalhes (COM EXPANDER e VISUAL COMPACTO) ---
    if "resultados" in st.session_state:
        with st.expander("4. 📖 **Detalhes dos Artefatos** (Resultados Finais)", expanded=True):
            st.success("Visualize os resultados e vá para 'Exportação' para baixar a planilha!")
            
            tabs = st.tabs([f"{EMOJIS[tipo]} {tipo.upper()}" for tipo in ARTEFATOS])
            
            for i, tipo in enumerate(ARTEFATOS):
                with tabs[i]:
                    # Título compacto com fundo escuro
                    st.markdown(
                        f"<div class='result-tab-title' style='background-color: {CORES[tipo]};'>"
                        f"Conteúdo Detalhado: {tipo.upper()}"
                        f"</div>", 
                        unsafe_allow_html=True
                    )
                    
                    # Usa a classe CSS para quebrar linha e dar o visual premium
                    conteudo = st.session_state["resultados"].get(tipo, "Não gerado ou erro.")
                    
                    # Aplica o estilo de caixa de texto com a cor da borda do artefato
                    st.markdown(f"<div class='generated-text-box' style='border-left: 5px solid {CORES[tipo]};'>{conteudo}</div>", unsafe_allow_html=True)

# =====================
# CONFIGURAÇÕES (COM BOTÃO DE RESTAURAÇÃO INTEGRADO)
# =====================
elif menu_option == "⚙️ Configurações de IA":
    st.title("⚙️ Configurações Avançadas da IA")
    st.markdown("Organize as chaves de API, defina o papel da IA e personalize os prompts.")
    
    # Organização por abas
    tab_ia_role, tab_playbook, tab_prompts = st.tabs(["🔑 Chaves e Papel da IA", "📄 Playbook", "💬 Prompts Padrão"])
    
    with tab_ia_role:
        st.subheader("🔑 Chaves de API (Acesso aos Modelos)")
        st.info("Insira sua chave de acesso para cada modelo de IA. Elas são salvas localmente no `config.json`.")
        
        # --- Layout HORIZONTAL para as chaves ---
        col_api1, col_api2, col_api3 = st.columns(3)
        keys_list = list(config["api_keys"].keys())
        columns = [col_api1, col_api2, col_api3]

        for i, key in enumerate(keys_list):
            with columns[i]:
                st.markdown(f"**{key.upper()} API Key**")
                config["api_keys"][key] = st.text_input(
                    f"Chave {key.upper()}", 
                    value=config["api_keys"].get(key, ""), 
                    type="password",
                    label_visibility="collapsed",
                    key=f"api_key_{key}" # Chave única para persistência
                )
        # --- Fim do Layout Horizontal ---

        st.subheader("🤖 Papel da IA (System Role)")
        config["ia_role"] = st.text_area("Descreva como a IA deve atuar", value=config.get("ia_role", INITIAL_CONFIG["ia_role"]), height=100, 
                                             help="Ex: 'Você é um Product Owner sênior, focado em clareza e detalhamento técnico...'")
        
        # --- BOTÕES DE AÇÃO: Restaurar e Salvar (Lado a Lado) ---
        st.markdown("---")
        st.subheader("🔒 Ações de Segurança e Salvar")
        
        col_restore, col_save = st.columns(2)
        
        with col_restore:
            st.button(
                "🗑️ Restaurar Chaves de API", 
                help="Remove TODAS as chaves salvas no config.json (define como vazio) por segurança.", 
                on_click=restaurar_chaves_api, 
                type="secondary",
                use_container_width=True
            )
        
        with col_save:
            # Lógica de salvamento completa
            if st.button("💾 Salvar Todas as Configurações", type="primary", use_container_width=True):
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                st.success("✅ Configurações salvas com sucesso! As alterações serão aplicadas na próxima geração.")

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
        st.info("Personalize as instruções enviadas para a IA para cada tipo de artefato.")
        for p in ARTEFATOS:
            st.markdown(f"**{EMOJIS.get(p, '💬')} Prompt para {p.upper()}**")
            # Usa o prompt inicial se a chave não existir no config carregado
            config["prompts"][p] = st.text_area(f"Prompt base para {p.upper()}", value=config["prompts"].get(p, INITIAL_CONFIG["prompts"].get(p, "")), height=120, label_visibility="collapsed")
    
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
                # O erro de codificação do PDF deve estar resolvido
                st.error(f"Erro ao gerar PDF: {e}. Se o erro persistir, verifique a instalação do fpdf.")
