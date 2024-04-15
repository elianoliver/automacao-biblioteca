import subprocess

# Lista com os nomes dos scripts que você quer rodar em sequência
scripts = ['1planilha_to_json.py', '2verificar_devedores_json.py', '3criando_planilha_todos&devedores.py']

# Loop para executar os scripts um após o outro
for script in scripts:
    subprocess.run(['python', script])
