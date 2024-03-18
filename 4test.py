import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

servico = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servico)

navegador.get("https://pergamumweb.com.br/pergamumweb_ifc/home_geral/login.jsp")
navegador.find_element('xpath', '/html/body/div/div/div/div[1]/div/div/div[2]/div[1]/div[2]/div/input').send_keys('usuario')

time.sleep(5)