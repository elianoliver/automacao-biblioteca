import pandas as pd
import json

# VARIAVEIS ===================================================================
caminho_arquivo_json = './excel/situacao_atualizada.json'
caminho_nova_planilha_excel = './excel/nova_planilha.xlsx'  # Caminho da nova planilha Excel

# FUNÇÕES =====================================================================
def equalize_lists(data):
    max_len = max(len(v) if isinstance(v, list) else 1 for v in data.values())
    return {k: v + [v[-1]] * (max_len - len(v)) if isinstance(v, list) else [v] * max_len for k, v in data.items()}

def criar_nova_planilha_a_partir_json(caminho_arquivo_json, caminho_nova_planilha_excel):
    try:
        with open(caminho_arquivo_json, 'r', encoding='utf-8') as json_file:
            dados_json = json.load(json_file)

            # Aplicar a função equalize_lists a cada dicionário nos dados
            dados_json['alunos_com_debito'] = [equalize_lists(d) for d in dados_json['alunos_com_debito']]
            dados_json['alunos_sem_debito'] = [equalize_lists(d) for d in dados_json['alunos_sem_debito']]

            # Criar um DataFrame do Pandas para alunos com débito
            df_alunos_com_debito = pd.concat([pd.DataFrame(d) for d in dados_json['alunos_com_debito']], ignore_index=True)

            # Criar um DataFrame do Pandas para alunos sem débito
            df_alunos_sem_debito = pd.concat([pd.DataFrame(d) for d in dados_json['alunos_sem_debito']], ignore_index=True)

            # Salvar os DataFrames como duas sheets diferentes em uma nova planilha Excel
            with pd.ExcelWriter(caminho_nova_planilha_excel, engine='xlsxwriter') as writer:
                df_alunos_com_debito.to_excel(writer, sheet_name='Alunos_Com_Debito', index=False)
                df_alunos_sem_debito.to_excel(writer, sheet_name='Alunos_Sem_Debito', index=False)

            print(f"A nova planilha foi criada com sucesso: {caminho_nova_planilha_excel}")

    except Exception as e:
        print(f"Ocorreu um erro ao criar a nova planilha: {e}")

# EXECUTANDO O PROGRAMA ========================================================
criar_nova_planilha_a_partir_json(caminho_arquivo_json, caminho_nova_planilha_excel)