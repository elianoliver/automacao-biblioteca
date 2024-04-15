# Este script lê um arquivo Excel contendo várias planilhas, filtra os dados com base em
# palavras-chave ignoradas e colunas desejadas, converte as colunas de data para um formato
# serializável, ignora as linhas vazias e salva os dados em um arquivo JSON.

import pandas as pd
import json
from datetime import datetime

# VARIAVEIS ===================================================================
caminho_arquivo_excel = './excel/original.xlsx'
palavras_chave_ignoradas = ['MODELO PARA CÓPIA']
caminho_arquivo_json = './excel/dados_sem_palavra_chave.json'
colunas_desejadas = ['Matrícula', 'ALUNO', 'REGULAR NA BIBLIOTECA? - SIM: salvar nada consta na pasta; NÃO: Mandar e-mail solicitando devolução ou pagamento', 'Obs. da Biblioteca']

# FUNÇÕES =====================================================================
def salvar_dados_em_json(dados, caminho_arquivo):
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as json_file:
            json.dump(dados, json_file, indent=2, default=str, ensure_ascii=False)
        print(f"Os dados foram salvos com sucesso no arquivo: {caminho_arquivo}")
    except Exception as e:
        print(f"Ocorreu um erro ao salvar os dados em JSON: {e}")

def obter_linhas_sem_palavra_chave(caminho_arquivo_excel, palavras_chave_ignoradas, colunas_desejadas):
    linhas_encontradas = {}

    try:
        # Lê todas as planilhas do arquivo Excel
        planilhas = pd.read_excel(caminho_arquivo_excel, sheet_name=None, dtype={'Matrícula': str})

        for nome_da_planilha, df in planilhas.items():
            # Verifica se alguma palavra-chave está presente no nome da planilha
            if not any(palavra.lower() in nome_da_planilha.lower() for palavra in palavras_chave_ignoradas):
                # Verifica se as colunas desejadas existem na planilha
                if set(colunas_desejadas).issubset(df.columns):
                    # Seleciona apenas as colunas desejadas
                    df = df[colunas_desejadas]

                    # Converte colunas Timestamp para formato serializável
                    for coluna in df.select_dtypes(include=['datetime64']).columns:
                        df[coluna] = df[coluna].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(x) else None)

                    # Remove linhas vazias
                    df = df.dropna(how='all')

                    # Adiciona as linhas da planilha correspondente
                    linhas_encontradas[nome_da_planilha] = df.to_dict(orient='records')

        return linhas_encontradas

    except Exception as e:
        print(f"Ocorreu um erro ao ler as planilhas: {e}")
        return None

# EXECUTANDO O PROGRAMA ========================================================
resultados = obter_linhas_sem_palavra_chave(caminho_arquivo_excel, palavras_chave_ignoradas, colunas_desejadas)

if resultados:
    salvar_dados_em_json(resultados, caminho_arquivo_json)
