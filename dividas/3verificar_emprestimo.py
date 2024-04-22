import os
import time
import json
import sys
from login import fazer_login
from datetime import datetime
from tkinter import *
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

# Configurações Selenium
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

# Inicialização do WebDriver Selenium
with webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install())) as driver:

    wait = WebDriverWait(driver, 10)

    def navegar_ate_emprestimos():
        bt_hamburguinho = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/div[1]/button')))
        bt_hamburguinho.click()

        bt_materiais = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div/div[2]/div[1]')))
        bt_materiais.click()

        bt_emprestimo = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="menuModulo1"]/div[1]')))
        bt_emprestimo.click()

    def verificar_estudantes():
        # Muda para a última aba aberta
        driver.switch_to.window(driver.window_handles[-1])
        iframe = driver.find_element(By.NAME, "meio")

        with open('excel/alunos_atualizado.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)

        novas_categorias = {
            "com_debito_com_atrasado": [],
            "com_debito_sem_atrasado": [],
            "sem_debito_sem_atrasado": [],
            "sem_debito_com_atrasado": []
        }

        for categoria, alunos in dados.items():
            print(f"Verificando a categoria {categoria}...")

            # Loop para verificar cada aluno
            for aluno in alunos:
                driver.switch_to.frame(iframe)
                numero_matricula = aluno['Matrícula']

                matricula_input = wait.until(EC.presence_of_element_located((By.ID, "id_txt_cod_pessoa")))
                matricula_input.send_keys(numero_matricula)
                matricula_input.send_keys(Keys.TAB)

                # fechar o alerta
                try:
                    alerta = wait.until(EC.alert_is_present())
                    time.sleep(2)
                    alerta.accept()
                except:
                    pass

                # fechar a janela de afastamento
                try:
                    wait.until(EC.visibility_of_element_located((By.ID, "id_tableAfastamento")))
                    btn_fechar = wait.until(EC.element_to_be_clickable((By.NAME, "btn_fechar")))
                    time.sleep(2)
                    btn_fechar.click()
                except:
                    pass

                # Verifica se a tabela tem um thead. Se tem thead, tem livros emprestados
                try:
                    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='tabelaEmprestimo']/thead")))
                    linhas = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#tabelaEmprestimo tbody tr")))

                    aluno['LivrosAtrasados'] = []
                    aluno['Multa total'] = 0

                    for linha in linhas:
                        tds = linha.find_elements(By.TAG_NAME, "td")

                        livro = {
                            "Título": tds[3].get_attribute("innerText").strip(),
                            "Emprestado em": tds[5].get_attribute("innerText").strip(),
                            "Devolução prevista": tds[6].get_attribute("innerText").strip(),
                            "Dias de atraso": tds[7].get_attribute("innerText").strip(),
                            "Valor": tds[13].get_attribute("innerText").strip()
                        }

                        dias_atraso = int(livro["Dias de atraso"]) if livro["Dias de atraso"].isdigit() else 0

                        if dias_atraso > 0:
                            aluno["Multa total"] += float(livro["Valor"].replace(',', '.'))
                            aluno['LivrosAtrasados'].append(livro)
                            aluno["Obs. da Biblioteca"] = "Possui débito e livros atrasados"

                    # Adiciona o aluno à nova categoria fora do loop dos livros
                    if aluno['LivrosAtrasados']:
                        if categoria == "com_debito_sem_atrasado":
                            novas_categorias["com_debito_com_atrasado"].append(aluno)
                        elif categoria == "sem_debito_sem_atrasado":
                            novas_categorias["sem_debito_com_atrasado"].append(aluno)
                    else:
                        if categoria == "com_debito_sem_atrasado":
                            novas_categorias["com_debito_sem_atrasado"].append(aluno)
                        else:
                            novas_categorias["sem_debito_sem_atrasado"].append(aluno)
                except:
                    if categoria == "com_debito_sem_atrasado":
                        novas_categorias["com_debito_sem_atrasado"].append(aluno)
                    else:
                        novas_categorias["sem_debito_sem_atrasado"].append(aluno)
                    pass

                matricula_input = wait.until(EC.presence_of_element_located((By.ID, "id_txt_cod_pessoa")))
                matricula_input.clear()
                driver.switch_to.default_content()

        # Atualiza o arquivo JSON
        with open('excel/alunos_atualizado_emprestimo.json', 'w', encoding='utf-8') as f:
            json.dump(novas_categorias, f, ensure_ascii=False, indent=4)

        sys.exit()

    # preencher os campos de login
    load_dotenv()
    username = os.getenv('USER')
    password = os.getenv('PASSWORD')
    fazer_login(driver, wait, username, password)

    # Interface gráfica
    root = Tk()
    root.geometry("200x100")
    root.title("Automatização com Tkinter e Selenium")

    def realizar_funcoes():
        wait = WebDriverWait(driver, 10)
        login_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div[2]/div[1]/div[6]/div/button')))
        login_button.click()
        print("entrei porra")

        navegar_ate_emprestimos()
        time.sleep(2)
        verificar_estudantes()

   # Botão de login
    login_button = Button(root, text="Realizar Login", command=realizar_funcoes)
    login_button.place(relx=0.5, rely=0.5, anchor=CENTER)

    root.mainloop()