import streamlit as st
import pandas as pd
import pygsheets
import os
import datetime
from streamlit_option_menu import option_menu
from streamlit_javascript import st_javascript

# Configuração da página para tela inteira
st.set_page_config(layout="wide")



# Menu de navegação
selecao = option_menu(
    menu_title="App BackStock",
    options=["NA CAIXA", "Tabela"],
    icons=["box", "table"],
    menu_icon="cast",
    orientation="horizontal"
)

# Autorizar acesso ao Google Sheets
credenciais = pygsheets.authorize(service_file=os.path.join(os.getcwd(), "cred.json"))
meuArquivoGoogleSheets = "https://docs.google.com/spreadsheets/d/1SFModXntK_P68nyofSYiB636eKG_uSZc_-f-mvWP1Yc/"
arquivo = credenciais.open_by_url(meuArquivoGoogleSheets)
aba = arquivo.worksheet_by_title("backstock")

# Carregar os dados da planilha e remover colunas vazias
data = aba.get_all_values()
if data:
    df = pd.DataFrame(data[1:], columns=data[0])  # Cria DataFrame com cabeçalho correto
    df = df.loc[:, ~df.columns.duplicated()]  # Remove colunas duplicadas
    df = df.dropna(axis=1, how="all")  # Remove colunas completamente vazias
else:
    df = pd.DataFrame(columns=["Bulto", "Peça", "Categoria", "Data/Hora"])

# Função para salvar dados no Google Sheets
def salvar_dados_no_sheets(bulto, peca, categoria):
    data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Obtém data e hora atual
    nova_linha = [bulto, peca, categoria, data_hora]
    aba.append_table(values=[nova_linha], start="A1", dimension="ROWS", overwrite=False)

# Configuração das telas
#titulo = f"COLETE O CÓDIGO DO BULTO {selecao}"
#st.title(titulo)

if selecao == "NA CAIXA":
    # Inicializar session_state
    if "bulto_numero" not in st.session_state:
        st.session_state["bulto_numero"] = ""
        st.session_state["bulto_cadastrado"] = False

    if "peca" not in st.session_state:
        st.session_state["peca"] = ""

    if not st.session_state["bulto_cadastrado"]:
        # Campo de entrada para o número do bulto
        bulto = st.text_input("Digite o número do bulto que está na caixa:")
        if bulto:
            st.session_state["bulto_numero"] = bulto
            st.session_state["bulto_cadastrado"] = True
            st.rerun()

    else:
        # Exibir o número do bulto e os campos para cadastro
        st.write(f"Bulto: {st.session_state['bulto_numero']}")
        categoria = st.radio("Escolha uma categoria:", ["Ubicação", "Limpeza", "Tara Maior"], index=None)

        # Gerar uma chave única para cada atualização do input
        unique_key = f"peca_{st.session_state.get('peca_reset_count', 0)}"
        peca = st.text_input("Digite a peça para este bulto:", key=unique_key)

        # Aplicar foco automático no campo de peça após cada cadastro
        st_javascript("""
            setTimeout(() => {
                const inputs = document.querySelectorAll('input[type="text"]');
                if (inputs.length > 0) {
                    inputs[inputs.length - 1].focus();
                }
            }, 100);
        """)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cadastrar Peça"):
                if not peca or categoria is None:
                    st.warning("Preencha todos os campos antes de cadastrar a peça.")
                else:
                    salvar_dados_no_sheets(st.session_state["bulto_numero"], peca, categoria)
                    st.success(f"Peça '{peca}' cadastrada no Bulto {st.session_state['bulto_numero']}!")

                    # Incrementar um contador para forçar a reinicialização do input
                    st.session_state["peca_reset_count"] = st.session_state.get("peca_reset_count", 0) + 1
                    st.rerun()

        with col2:
            if st.button("Finalizar Bulto"):
                st.success("Bulto finalizado com sucesso!")
                st.session_state["bulto_numero"] = ""
                st.session_state["bulto_cadastrado"] = False
                st.session_state["peca_reset_count"] = 0  # Resetar contador do input
                st.rerun()

elif selecao == "Tabela":
    st.write("### Dados do BackStock")
    st.write(df)  # Exibe a tabela na tela principal
st.markdown(
    """
    <div style="display: flex; justify-content: center;">
        <img src="https://automni.com.br/wp-content/uploads/2022/08/Logo-IDLogistics-PNG.svg" width="400">
    </div>
    """,
    unsafe_allow_html=True
)
    
    
st.markdown(
    """
    <style>
        .footer {
            #position: fixed;
            bottom: 10;
            right: 10px;
            font-size: 10px;
            text-align: center;
            background-color: white;
            padding: 5px;
            z-index: 100;
        }
    </style>
    <div class="footer">
        Copyright © 2025 Direitos Autorais Desenvolvedor Rogério Ferreira
    </div>
    """,
    unsafe_allow_html=True
)
