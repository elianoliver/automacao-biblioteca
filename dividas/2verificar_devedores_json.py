import time
import json
import sys
from datetime import datetime
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
        iframe = driver.find_element(By.NAME, "meio")

        # Adiciona uma espera explícita
        wait = WebDriverWait(driver, 10)

        def diferenca_dias(data1, data2):
            if data1 == '0,00' or data2 == '0,00':
                return 0  # ou qualquer valor padrão que você queira usar
            else:
                data1 = datetime.strptime(data1, '%d/%m/%Y %H:%M:%S.%f')
                data2 = datetime.strptime(data2, '%d/%m/%Y %H:%M:%S.%f')
                # Removendo horas, minutos, segundos e microssegundos
                data1 = data1.replace(hour=0, minute=0, second=0, microsecond=0)
                data2 = data2.replace(hour=0, minute=0, second=0, microsecond=0)
                return abs((data2 - data1).days)


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

                        # Adiciona o texto do alerta ao objeto aluno
                        aluno['texto_alerta'] = texto_alerta

                        # Adiciona o aluno à lista de alunos com débito
                        alunos_sem_debito.append(aluno)

                    except TimeoutException:
                        # Se não houver alerta, o aluno tem débito

                        linhas = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#table_debito_devolucao tbody tr:not(:first-child)")))
                        div_valor_debito = wait.until(EC.presence_of_element_located((By.ID, "divValorDebito"))).text.strip()

                        aluno['Livros'] = []
                        aluno['ValorLivros'] = []
                        aluno['Emprestado em'] = []
                        aluno['Devolução prevista'] = []
                        aluno['Devolução efetiva'] = []

                        # Itera sobre cada linha para capturar os elementos desejados
                        for linha in linhas:
                            # pegue todos os td's da linha
                            tds = linha.find_elements(By.TAG_NAME, "td")

                            td3 = tds[3].get_attribute("innerText").strip()
                            td9 = tds[9].get_attribute("innerText").strip()
                            td13 = tds[13].get_attribute("innerText").strip().split(' ')[0]
                            td14 = tds[14].get_attribute("innerText").strip().split(' ')[0]
                            td15 = tds[15].get_attribute("innerText").strip().split(' ')[0]

                            # Adiciona os valores às respectivas listas
                            aluno['Livros'].append(td3)
                            aluno['ValorLivros'].append(td9)
                            aluno['Emprestado em'].append(td13)
                            aluno['Devolução prevista'].append(td14)
                            aluno['Devolução efetiva'].append(td15)

                        aluno['Valor total a pagar'] = div_valor_debito

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
        sys.exit()

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