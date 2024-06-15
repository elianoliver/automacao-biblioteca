import pandas as pd
import json

# VARIAVEIS ===================================================================
caminho_arquivo_excel = './excel/original.xlsx'
caminho_arquivo_json = './excel/alunos.json'
colunas_desejadas = ['Código pessoa', 'Nome da pessoa', 'Email']

# FUNÇÕES =====================================================================
def salvar_dados_em_json(dados, caminho_arquivo):
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as json_file:
            json.dump(dados, json_file, indent=2, default=str, ensure_ascii=False)
        print(f"Os dados foram salvos com sucesso no arquivo: {caminho_arquivo}")
    except Exception as e:
        print(f"Ocorreu um erro ao salvar os dados em JSON: {e}")

def obter_linhas_sem_palavra_chave(caminho_arquivo_excel, colunas_desejadas):
    linhas_encontradas = {}

    try:
        # Lê todas as planilhas do arquivo Excel
        planilhas = pd.read_excel(caminho_arquivo_excel, sheet_name=None, dtype={'Código pessoa': str})
        print(f"Planilhas lidas: {list(planilhas.keys())}")  # Debug: Imprime os nomes das planilhas lidas

        for nome_da_planilha, df in planilhas.items():
            print(f"Processando planilha: {nome_da_planilha}")  # Debug: Imprime o nome da planilha sendo processada

            # Verifica se as colunas desejadas existem na planilha
            if set(colunas_desejadas).issubset(df.columns):
                print(f"Colunas desejadas encontradas na planilha: {nome_da_planilha}")  # Debug
                # Seleciona apenas as colunas desejadas
                df = df[colunas_desejadas]

                # Converte colunas Timestamp para formato serializável
                for coluna in df.select_dtypes(include=['datetime64']).columns:
                    df[coluna] = df[coluna].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None)

                # Remove linhas vazias
                df = df.dropna(how='all')
                print(f"Linhas após remoção de vazias: {len(df)}")  # Debug: Imprime o número de linhas após remoção

                # Verifica se há linhas para processar após a remoção
                if df.empty:
                    print(f"Nenhuma linha válida encontrada na planilha {nome_da_planilha} para adicionar ao dicionário")  # Debug
                    continue  # Pula para a próxima planilha se esta estiver vazia

                # Processamento adicional aqui...

                # Adiciona as linhas da planilha correspondente ao dicionário
                linhas_encontradas[nome_da_planilha] = df.to_dict('records')

            else:
                print(f"As colunas desejadas não foram encontradas na planilha: {nome_da_planilha}")  # Debug

        return linhas_encontradas

    except Exception as e:
        print(f"Ocorreu um erro ao ler as planilhas: {e}")
        return None

# EXECUTANDO O PROGRAMA ========================================================
resultados = obter_linhas_sem_palavra_chave(caminho_arquivo_excel, colunas_desejadas)
print(f"Total de planilhas processadas: {len(resultados)}")  # Debug: Imprime o total de planilhas processadas

if resultados:
    salvar_dados_em_json(resultados, caminho_arquivo_json)