import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Lançamentos", page_icon="🧠", layout="centered")

st.title("🧠 Lançamentos")
st.subheader("📋 Cole sua tabela:")

texto = st.text_area("Cole aqui:", height=300)

if st.button("🚀 Processar"):
    if texto.strip() == "":
        st.warning("⚠️ Cole os dados no campo acima.")
    else:
        linhas = texto.strip().splitlines()

        # 🔥 Junta linhas quebradas
        linhas_corrigidas = []
        linha_acumulada = ""

        for linha in linhas:
            linha_check = linha.strip()
            if any(x in linha_check.upper() for x in ["CÁLCULO LIQUIDADO", "VERSÃO", "PÁG"]):
                continue  # Ignorar linhas de rodapé

            numeros = re.findall(r'[\d\.,]+', linha_check)
            if len(numeros) >= 3:
                if linha_acumulada:
                    linha_completa = linha_acumulada + " " + linha_check
                    linhas_corrigidas.append(linha_completa.strip())
                    linha_acumulada = ""
                else:
                    linhas_corrigidas.append(linha_check.strip())
            else:
                linha_acumulada += " " + linha_check

        if linha_acumulada:
            linhas_corrigidas.append(linha_acumulada.strip())

        # 🏗️ Processamento das linhas corrigidas
        dados = []
        for linha in linhas_corrigidas:
            numeros = re.findall(r'[\d\.,]+', linha)

            if len(numeros) >= 1:
                total = numeros[-1]
                try:
                    total = float(total.replace('.', '').replace(',', '.'))
                except:
                    total = 0.0

                descricao = linha
                for num in numeros[-3:]:
                    descricao = descricao.rsplit(num, 1)[0]
                descricao = descricao.strip().upper()

                dados.append([descricao, total])

        df = pd.DataFrame(dados, columns=['Descricao', 'Total'])

        # 🔥 Agrupamento correto
        def agrupar_verba(descricao):
            if "FGTS" in descricao and "MULTA" not in descricao:
                return "FGTS + MULTA 40%"
            if "MULTA SOBRE FGTS" in descricao:
                return "FGTS + MULTA 40%"

            prefixos_reflexos = ["13º", "FÉRIAS", "AVISO", "REPOUSO"]

            if any(descricao.startswith(prefixo) for prefixo in prefixos_reflexos):
                if "SOBRE" in descricao:
                    partes = descricao.split("SOBRE", 1)
                    verba = partes[1].strip()
                    return verba
                else:
                    return descricao
            else:
                return descricao

        df['Verba Consolidada'] = df['Descricao'].apply(agrupar_verba)

        resultado = df.groupby('Verba Consolidada').sum(numeric_only=True).reset_index()

        st.success("✅ Processamento concluído!")

        st.subheader("📊 Resultado Consolidado:")

        # 🔢 Calcular o total geral
        total_geral = resultado['Total'].sum()

        # ➕ Adicionar uma linha de total no dataframe de exibição
        linha_total = pd.DataFrame([['TOTAL GERAL', total_geral]], columns=['Verba Consolidada', 'Total'])
        resultado_com_total = pd.concat([resultado, linha_total], ignore_index=True)

        # 🔧 Formatar os valores no padrão brasileiro (apenas na interface)
        resultado_exibicao = resultado_com_total.copy()
        resultado_exibicao['Total'] = resultado_exibicao['Total'].apply(
            lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

        st.dataframe(resultado_exibicao)
