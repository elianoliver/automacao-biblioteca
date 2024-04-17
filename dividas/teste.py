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

    wait = WebDriverWait(driver, 10)

    # Função de login
    def fazer_login(username, password):
        driver.get("https://pergamumweb.com.br/pergamumweb_ifc/home_geral/login.jsp")

        username_input = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div[2]/div[1]/div[2]/div/input')))
        password_input = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div[2]/div[1]/div[3]/div[1]/input')))

        username_input.send_keys(username)
        password_input.send_keys(password)

    def navegar_ate_emprestimos():

        bt_hamburguinho = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/div[1]/button')))
        bt_hamburguinho.click()
        time.sleep(2)

        bt_materiais = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[6]/div/div[2]/div[1]')))
        bt_materiais.click()
        time.sleep(2)

        bt_emprestimo = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="menuModulo1"]/div[1]')))
        bt_emprestimo.click()
        time.sleep(2)

    def verificar_estudantes():
        alunos_com_livros = []
        alunos_sem_livros = []

        # Muda para a última aba aberta
        driver.switch_to.window(driver.window_handles[-1])
        iframe = driver.find_element(By.NAME, "meio")

        with open('excel/situacao_atualizada.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)

        # Loop para verificar cada aluno
        for aluno in dados['alunos_com_debito']:
            driver.switch_to.frame(iframe)
            matricula_dados = aluno['Matrícula']
            matricula_input = wait.until(EC.presence_of_element_located((By.ID, "id_txt_cod_pessoa")))
            matricula_input.send_keys(matricula_dados)
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

                aluno['LivrosEmprestados'] = []

                for linha in linhas:
                    tds = linha.find_elements(By.TAG_NAME, "td")

                    td3 = tds[3].get_attribute("innerText").strip()
                    td5 = tds[5].get_attribute("innerText").strip()
                    td6 = tds[6].get_attribute("innerText").strip()
                    td7 = tds[7].get_attribute("innerText").strip()

                    aluno['LivrosEmprestados'].append(td3)

                print(f"td3: {td3}")
                print(f"td5: {td5}")
                print(f"td6: {td6}")
                print(f"td7: {td7}")

                alunos_com_livros.append(aluno)

            except:
                alunos_sem_livros.append(aluno)

            matricula_input = wait.until(EC.presence_of_element_located((By.ID, "id_txt_cod_pessoa")))
            matricula_input.clear()
            driver.switch_to.default_content()

        print(f"Alunos com livros:\n {alunos_com_livros}")
        print(f"Alunos sem livros:\n {alunos_sem_livros}")

        # Atualiza o arquivo JSON
        with open('excel/situacao_atualizada.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
            
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

        navegar_ate_emprestimos()
        time.sleep(5)
        verificar_estudantes()

    # Botão de login
    login_button = Button(root, text="Realizar Login", command=realizar_login)
    login_button.place(relx=0.5, rely=0.5, anchor=CENTER)


    root.mainloop()