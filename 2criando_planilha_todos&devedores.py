# Este script lê um arquivo JSON contendo dados de várias planilhas, cria um DataFrame consolidado
# e salva duas sheets em uma nova planilha Excel. A primeira sheet ("Todos") contém todos os dados
# consolidados, enquanto a segunda sheet ("Nao_Regulares") inclui apenas os dados dos alunos que
# não estão regulares na biblioteca.

import pandas as pd
import json

# VARIAVEIS ===================================================================
caminho_arquivo_json = './excel/dados_sem_palavra_chave.json'
caminho_nova_planilha_excel = './excel/nova_planilha.xlsx'  # Caminho da nova planilha Excel

# FUNÇÕES =====================================================================
def criar_nova_planilha_a_partir_json(caminho_json, caminho_nova_planilha_excel):
    try:
        with open(caminho_json, 'r', encoding='utf-8') as json_file:
            dados_json = json.load(json_file)

            # Criar um DataFrame do Pandas a partir dos dados do JSON
            df_nova_planilha = pd.DataFrame()

            for nome_planilha, dados in dados_json.items():
                df_temp = pd.DataFrame(dados)
                df_temp['Planilha'] = nome_planilha  # Adicionar uma coluna para o nome da planilha original
                df_nova_planilha = pd.concat([df_nova_planilha, df_temp], ignore_index=True)

            # Salvar o DataFrame completo como uma nova planilha Excel
            with pd.ExcelWriter(caminho_nova_planilha_excel, engine='xlsxwriter') as writer:
                df_nova_planilha.to_excel(writer, sheet_name='Todos', index=False)

                # Filtrar linhas com "Não" na coluna "REGULAR NA BIBLIOTECA?"
                coluna_regulares = 'REGULAR NA BIBLIOTECA? - SIM: salvar nada consta na pasta; NÃO: Mandar e-mail solicitando devolução ou pagamento'
                df_nova_planilha_nao_regulares = df_nova_planilha[df_nova_planilha[coluna_regulares] == 'Não']

                # Salvar o DataFrame filtrado como uma segunda sheet na mesma planilha Excel
                df_nova_planilha_nao_regulares.to_excel(writer, sheet_name='Nao_Regulares', index=False)

            print(f"A nova planilha foi criada com sucesso: {caminho_nova_planilha_excel}")

    except Exception as e:
        print(f"Ocorreu um erro ao criar a nova planilha: {e}")

# EXECUTANDO O PROGRAMA ========================================================
criar_nova_planilha_a_partir_json(caminho_arquivo_json, caminho_nova_planilha_excel)
