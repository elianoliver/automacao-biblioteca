import time
import json
import sys
from login import fazer_login
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
import os

# Configurações Selenium
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

# Inicialização do WebDriver Selenium
with webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install())) as driver:

    wait = WebDriverWait(driver, 10)

    def navegar_ate_debitos():
        try:
            bt_hamburguinho = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/div[1]/button')))
            bt_hamburguinho.click()

            bt_materiais = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div/div[2]/div[1]')))
            bt_materiais.click()

            bt_debitos = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div/div[2]/div[2]/div[3]')))
            bt_debitos.click()

            bt_pagamento = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div/div[2]/div[2]/div[4]/div[1]/div')))
            bt_pagamento.click()
        except TimeoutException as e:
            print(f"Erro ao navegar até débitos: {e}")

    def normalizar_data(data):
        try:
            data_normalizada = datetime.strptime(data, '%d/%m/%Y %H:%M:%S.%f')
            return data_normalizada.strftime('%d/%m/%Y')
        except ValueError:
            try:
                data_normalizada = datetime.strptime(data, '%d/%m/%Y')
                return data_normalizada.strftime('%d/%m/%Y')
            except ValueError:
                return data

    # def diferenca_dias(data1, data2):
    #     if data1 == '0,00' or data2 == '0,00':
    #         return 0  # ou qualquer valor padrão que você queira usar
    #     else:
    #         data1 = datetime.strptime(data1, '%d/%m/%Y %H:%M:%S.%f')
    #         data2 = datetime.strptime(data2, '%d/%m/%Y %H:%M:%S.%f')
    #         # Removendo horas, minutos, segundos e microssegundos
    #         data1 = data1.replace(hour=0, minute=0, second=0, microsecond=0)
    #         data2 = data2.replace(hour=0, minute=0, second=0, microsecond=0)
    #         return abs((data2 - data1).days)

    def verificar_estudantes():
        alunos_com_debito = []
        alunos_sem_debito = []

        # Muda para a última aba aberta
        driver.switch_to.window(driver.window_handles[-1])
        iframe = driver.find_element(By.NAME, "meio")

        # Carrega os dados do arquivo JSON
        with open('excel/alunos.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)

        # Itera sobre cada aluno
        for aluno in dados["Página 1"]:
            print(f"Verificando aluno: {aluno['Nome da pessoa']}")
            driver.switch_to.frame(iframe)

            try:
                # Extrai a matrícula do aluno
                numero_matricula = aluno["Código pessoa"]

                matricula_input = wait.until(EC.presence_of_element_located((By.ID, "id_txt_cod_pessoa")))
                matricula_input.send_keys(numero_matricula)
                matricula_input.send_keys(Keys.TAB)

                # ========================= ALUNO SEM DÉBITO ==========================
                try:
                    alerta = wait.until(EC.alert_is_present())

                    if alerta.text == "Usuário não possui débitos!":
                        print(f"{numero_matricula} - Sem débitos.")

                        # Adiciona o texto do alerta ao objeto aluno
                        aluno = {
                            "Matrícula": numero_matricula,
                            "Aluno": aluno["Nome da pessoa"],
                            "Email": aluno["Email"],
                            "Texto do alerta": alerta.text
                        }

                        alerta.accept()

                        # Adiciona o aluno à lista de alunos sem débito
                        alunos_sem_debito.append(aluno)

                # ========================= ALUNO COM DÉBITO ==========================
                except TimeoutException:

                    try:
                        linhas = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#table_debito_devolucao tbody tr:not(:first-child)")))
                        div_valor_debito = wait.until(EC.presence_of_element_located((By.ID, "divValorDebito"))).text.strip()
                        aluno['LivrosEntregues'] = []

                        for linha in linhas:
                            # pegue todos os td's da linha
                            tds = linha.find_elements(By.TAG_NAME, "td")

                            livro = {
                                "Obs": "Multa gerada",
                                "Título": tds[3].get_attribute("innerText").strip(),
                                "Emprestado em": normalizar_data(tds[13].get_attribute("innerText").strip().split(' ')[0]),
                                "Devolução prevista": normalizar_data(tds[14].get_attribute("innerText").strip().split(' ')[0]),
                                "Devolução efetiva": normalizar_data(tds[15].get_attribute("innerText").strip().split(' ')[0]),
                                "Valor": tds[9].get_attribute("innerText").strip()
                            }

                            # Adiciona o livro à lista de livros
                            aluno['LivrosEntregues'].append(livro)

                        aluno['Valor total a pagar'] = div_valor_debito
                    except:
                        print(f"Sem livros entregues: {numero_matricula}")

                    try:
                        linhas_armario = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#table_debito_armario tbody tr:not(:first-child)")))

                        div_valor_debito = wait.until(EC.presence_of_element_located((By.ID, "divValorDebito"))).text.strip()
                        aluno['Armarios'] = []

                        # Itera sobre cada linha para capturar os elementos desejados
                        for linha in linhas_armario:
                            # pegue todos os td's da linha
                            tds = linha.find_elements(By.TAG_NAME, "td")

                            armario = {
                                "Obs": "Armário alugado",
                                "Título": "Nº " + tds[2].get_attribute("innerText").strip(),
                                "Emprestado em": normalizar_data(tds[3].get_attribute("innerText").strip()),
                                "Devolução prevista": normalizar_data(tds[3].get_attribute("innerText").strip()),
                                "Devolução efetiva": normalizar_data(tds[4].get_attribute("innerText").strip()),
                                "Valor": tds[9].get_attribute("innerText").strip()
                            }

                            # Adiciona o armário à lista de armários
                            aluno['Armarios'].append(armario)

                        aluno['Valor total a pagar'] = div_valor_debito

                    except TimeoutException as e:
                        print(f"Sem armários alugados: {numero_matricula}")


                    alunos_com_debito.append(aluno)
                    print(f"Aluno com débito encontrado: {numero_matricula}")

                # Seleciona novamente o input id_txt_cod_pessoa
                matricula_input = wait.until(EC.presence_of_element_located((By.ID, "id_txt_cod_pessoa")))
                matricula_input.clear()

            except Exception as e:
                print(f"Erro ao tentar encontrar o elemento: {e}")

            finally:
                # Volta para o contexto padrão (fora do iframe)
                driver.switch_to.default_content()

        # Cria um dicionário com as listas de alunos com e sem débito
        resultado = {
            'com_debito_sem_atrasado': alunos_com_debito,
            'sem_debito_sem_atrasado': alunos_sem_debito
        }

        # Grava o resultado em um arquivo JSON
        with open('./excel/alunos_atualizado.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)

        print("Arquivo JSON criado com sucesso.")
        sys.exit()

    def realizar_funcoes():
        wait = WebDriverWait(driver, 5)
        login_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div[2]/div[1]/div[6]/div/button')))
        login_button.click()
        print("entrei porra")

        navegar_ate_debitos()
        time.sleep(5)
        verificar_estudantes()

    def criar_interface_grafica():
        root = Tk()
        root.geometry("200x100")
        root.title("Automatização com Tkinter e Selenium")

        login_button = Button(root, text="Realizar Login", command=realizar_funcoes)
        login_button.place(relx=0.5, rely=0.5, anchor=CENTER)

        root.mainloop()

    load_dotenv()
    username = os.getenv('USER')
    password = os.getenv('PASSWORD')
    fazer_login(driver, wait, username, password)

    criar_interface_grafica()