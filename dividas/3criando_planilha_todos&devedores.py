# Este script lê um arquivo JSON contendo dados de várias planilhas, cria um DataFrame consolidado
# e salva duas sheets em uma nova planilha Excel. A primeira sheet ("Todos") contém todos os dados
# consolidados, enquanto a segunda sheet ("Nao_Regulares") inclui apenas os dados dos alunos que
# não estão regulares na biblioteca.

import pandas as pd
import json

# VARIAVEIS ===================================================================
caminho_arquivo_json = './excel/situacao_atualizada.json'
caminho_nova_planilha_excel = './excel/nova_planilha.xlsx'  # Caminho da nova planilha Excel

# FUNÇÕES =====================================================================
def criar_nova_planilha_a_partir_json(caminho_arquivo_json, caminho_nova_planilha_excel):
    try:
        with open(caminho_arquivo_json, 'r', encoding='utf-8') as json_file:
            dados_json = json.load(json_file)

            # Criar um DataFrame do Pandas para alunos com débito
            df_alunos_com_debito = pd.DataFrame(dados_json['alunos_com_debito'])

            # Criar um DataFrame do Pandas para alunos sem débito
            df_alunos_sem_debito = pd.DataFrame(dados_json['alunos_sem_debito'])

            # Salvar os DataFrames como duas sheets diferentes em uma nova planilha Excel
            with pd.ExcelWriter(caminho_nova_planilha_excel, engine='xlsxwriter') as writer:
                df_alunos_com_debito.to_excel(writer, sheet_name='Alunos_Com_Deito', index=False)
                df_alunos_sem_debito.to_excel(writer, sheet_name='Alunos_Sem_Deito', index=False)

            print(f"A nova planilha foi criada com sucesso: {caminho_nova_planilha_excel}")

    except Exception as e:
        print(f"Ocorreu um erro ao criar a nova planilha: {e}")

# EXECUTANDO O PROGRAMA ========================================================
criar_nova_planilha_a_partir_json(caminho_arquivo_json, caminho_nova_planilha_excel)
