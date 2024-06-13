import pandas as pd
import json

# VARIAVEIS ===================================================================
caminho_arquivo_json = './excel/alunos_atualizado_emprestimo.json'
caminho_nova_planilha_excel = './excel/nova_planilha.xlsx'

# FUNÇÕES =====================================================================
def equalize_lists(data):
    equalized_data = {}
    # Calcula o comprimento máximo entre todas as listas no dicionário
    max_len = max(len(v) if isinstance(v, list) else 1 for v in data.values())

    for key, value in data.items():
        # Se for uma lista, estende com o último elemento até o comprimento máximo
        if isinstance(value, list):
            extended_list = value + [value[-1] if value else None] * (max_len - len(value))
            equalized_data[key] = extended_list
        # Se não for uma lista, cria uma lista repetindo o valor até o comprimento máximo
        else:
            repeated_value_list = [value] * max_len
            equalized_data[key] = repeated_value_list

    return equalized_data

def desencapsular_aluno(aluno):
    # Extrai as listas de livros atrasados e entregues do dicionário do aluno
    livros_atrasados = aluno.pop('LivrosAtrasados', [])
    livros_entregues = aluno.pop('LivrosEntregues', [])

    # Cria uma nova lista de dicionários, cada um representando um livro que o aluno tem ou teve emprestado
    # Cada dicionário contém todas as informações do aluno, além das informações do livro
    alunos_desencapsulados = []
    for livro in livros_atrasados + livros_entregues:
        aluno_com_livro = dict(aluno, **livro)
        alunos_desencapsulados.append(aluno_com_livro)

    # Se a lista de alunos desencapsulados estiver vazia (ou seja, o aluno não tem nem teve livros emprestados),
    # retorna uma lista contendo apenas o dicionário do aluno
    if not alunos_desencapsulados:
        return [aluno]

    return alunos_desencapsulados

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