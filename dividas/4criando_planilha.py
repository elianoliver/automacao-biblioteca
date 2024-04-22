import pandas as pd
import json

# VARIAVEIS ===================================================================
caminho_arquivo_json = './excel/alunos_atualizado_emprestimo.json'
caminho_nova_planilha_excel = './excel/nova_planilha.xlsx'

# FUNÇÕES =====================================================================
def equalize_lists(data):
    max_len = max(len(v) if isinstance(v, list) else 1 for v in data.values())
    return {k: v + [v[-1] if v else None] * (max_len - len(v)) if isinstance(v, list) else [v] * max_len for k, v in data.items()}

def desencapsular_aluno(aluno):
    livros_atrasados = aluno.pop('LivrosAtrasados', [])
    livros_entregues = aluno.pop('LivrosEntregues', [])
    alunos_desencapsulados = [dict(aluno, **livro) for livro in livros_atrasados + livros_entregues]
    return alunos_desencapsulados if alunos_desencapsulados else [aluno]

def criar_nova_planilha_a_partir_json(caminho_arquivo_json, caminho_nova_planilha_excel):
    try:
        with open(caminho_arquivo_json, 'r', encoding='utf-8') as json_file:
            dados_json = json.load(json_file)

            # Desencapsular os valores dentro do aluno
            for categoria in dados_json:
                alunos_desencapsulados = []
                for aluno in dados_json[categoria]:
                    alunos_desencapsulados.extend(desencapsular_aluno(aluno))
                dados_json[categoria] = alunos_desencapsulados

            # Aplicar a função equalize_lists a cada dicionário nos dados
            for categoria in dados_json:
                for i in range(len(dados_json[categoria])):
                    dados_json[categoria][i] = equalize_lists(dados_json[categoria][i])

            # Criar um DataFrame do Pandas para cada categoria
            dataframes = {categoria: pd.concat([pd.DataFrame(d) for d in dados_json[categoria]], ignore_index=True) for categoria in dados_json if dados_json[categoria]}

            # Salvar os DataFrames como sheets diferentes em uma nova planilha Excel
            with pd.ExcelWriter(caminho_nova_planilha_excel, engine='xlsxwriter') as writer:
                for categoria, df in dataframes.items():
                    if not df.empty:
                        df.to_excel(writer, sheet_name=categoria, index=False)

            print(f"A nova planilha foi criada com sucesso: {caminho_nova_planilha_excel}")

    except Exception as e:
        print(f"Ocorreu um erro ao criar a nova planilha: {e}")

# EXECUTANDO O PROGRAMA ========================================================
criar_nova_planilha_a_partir_json(caminho_arquivo_json, caminho_nova_planilha_excel)