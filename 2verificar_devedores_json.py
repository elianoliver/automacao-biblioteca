import time
import json
from tkinter import *
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

    # Função de login
    def fazer_login(username, password):
        driver.get("https://pergamumweb.com.br/pergamumweb_ifc/home_geral/login.jsp")

        wait = WebDriverWait(driver, 10)
        username_input = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div[2]/div[1]/div[2]/div/input')))
        password_input = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div[2]/div[1]/div[3]/div[1]/input')))

        username_input.send_keys(username)
        password_input.send_keys(password)

    def navegar_ate_debitos():
        wait = WebDriverWait(driver, 20)  # Aumentar o tempo de espera para 20 segundos

        bt_hamburguinho = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/div[1]/button')))
        bt_hamburguinho.click()
        time.sleep(2)

        bt_materiais = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div/div[2]/div[1]')))
        bt_materiais.click()
        time.sleep(2)

        bt_debitos = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div/div[2]/div[2]/div[3]')))
        bt_debitos.click()
        time.sleep(2)

        bt_pagamento = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div/div[2]/div[2]/div[4]/div[1]/div')))
        bt_pagamento.click()
        time.sleep(2)

    def verificar_estudantes():
        # Listas para armazenar alunos com e sem débito
        alunos_com_debito = []
        alunos_sem_debito = []

        # Carrega os dados do arquivo JSON
        with open('excel/dados_sem_palavra_chave.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)

        # Muda para a última aba aberta
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)
        iframe = driver.find_element(By.NAME, "meio")

        # Itera sobre cada turma nos dados
        for turma, alunos in dados.items():
            print(f"Verificando a turma {turma}...")

            # Itera sobre cada aluno na turma
            for aluno in alunos:

                # Muda para o iframe
                driver.switch_to.frame(iframe)

                # Tenta capturar o elemento com o ID "id_txt_cod_pessoa"
                try:
                    # Extrai a matrícula do aluno
                    matricula_dados = aluno['Matrícula']

                    # Adiciona uma espera explícita
                    wait = WebDriverWait(driver, 10)

                    matricula_input = wait.until(EC.presence_of_element_located((By.ID, "id_txt_cod_pessoa")))
                    matricula_input.send_keys(matricula_dados)
                    matricula_input.send_keys(Keys.TAB)

                    # Aguarda até que o alerta esteja presente
                    try:
                        alerta = wait.until(EC.alert_is_present())

                        # Captura o texto do alerta
                        texto_alerta = alerta.text
                        print(f"{matricula_dados} - {texto_alerta}")

                        # Fecha o alerta
                        alerta.accept()

                        # Adiciona o aluno à lista de alunos com débito
                        alunos_sem_debito.append(aluno)

                    except TimeoutException:
                        # Se não houver alerta, o aluno tem débito
                        alunos_com_debito.append(aluno)
                        print(f"Aluno com débito encontrado: {matricula_dados}")

                        # Seleciona novamente o input id_txt_cod_pessoa
                        matricula_input = wait.until(EC.presence_of_element_located((By.ID, "id_txt_cod_pessoa")))
                        matricula_input.clear()

                except Exception as e:
                    print(f"Erro ao tentar encontrar o elemento: {e}")

                finally:
                    # Volta para o contexto padrão (fora do iframe)
                    driver.switch_to.default_content()

                time.sleep(2)

        # Cria um dicionário com as listas de alunos com e sem débito
        resultado = {
            'alunos_com_debito': alunos_com_debito,
            'alunos_sem_debito': alunos_sem_debito
        }

        # Grava o resultado em um arquivo JSON
        with open('./excel/situacao_atualizada.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)

        print("Arquivo JSON criado com sucesso.")

    # preencher os campos quando o programa iniciar
    fazer_login('elian.oliveira', '4192')

    # Interface gráfica
    root = Tk()
    root.geometry("200x100")
    root.title("Automatização com Tkinter e Selenium")


    def realizar_login():
        wait = WebDriverWait(driver, 10)
        login_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div[2]/div[1]/div[6]/div/button')))
        login_button.click()
        print("entrei porra")

        navegar_ate_debitos()
        time.sleep(5)
        verificar_estudantes()

   # Botão de login
    login_button = Button(root, text="Realizar Login", command=realizar_login)
    login_button.place(relx=0.5, rely=0.5, anchor=CENTER)


    root.mainloop()