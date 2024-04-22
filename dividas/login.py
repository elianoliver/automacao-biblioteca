from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fazer_login(driver, wait, username, password):
    driver.get("https://pergamumweb.com.br/pergamumweb_ifc/home_geral/login.jsp")

    username_input = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div[2]/div[1]/div[2]/div/input')))
    password_input = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div[2]/div[1]/div[3]/div[1]/input')))

    username_input.send_keys(username)
    password_input.send_keys(password)