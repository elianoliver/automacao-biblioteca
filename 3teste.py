import pygame
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurações Pygame
pygame.init()

# Constantes
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 300
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
BUTTON_COLOR = BLUE
CHECKBOX_RECT = pygame.Rect(10, 10, 20, 20)

# Inicialização da janela Pygame
window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Automatização com Pygame e Selenium')

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
        # login_button.click()

    # preencher os campos quando o programa iniciar
    fazer_login('elian.oliveira', '4192')

    # Fonte Pygame
    font = pygame.font.Font(None, 36)

    # Elementos da interface
    button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 150, 200, 50)

    # Loop principal do Pygame
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):                    
                    BUTTON_COLOR = WHITE
                    wait = WebDriverWait(driver, 10)
                    login_button = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/div/div/div[2]/div[1]/div[6]/div/button')))
                    login_button.click()
                    print("entrei porra")
                    
                    time.sleep(5)
                    
                    outro_botao = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/div[1]/button')))
                    outro_botao.click()

            elif event.type == pygame.MOUSEBUTTONUP:
                BUTTON_COLOR = BLUE

        window_surface.fill(WHITE)
        pygame.draw.rect(window_surface, BUTTON_COLOR, button_rect)

        # Renderizar o texto
        text = font.render("Clique no botão para efetuar o login:", True, BLACK)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 70))
        window_surface.blit(text, text_rect)

        # Renderizar o texto do botão
        button_text = font.render("Realizar Login", True, (50, 50, 50))
        button_text_rect = button_text.get_rect(center=button_rect.center)
        window_surface.blit(button_text, button_text_rect)

        # Renderizar a checkbox
        pygame.draw.rect(window_surface, BLACK, CHECKBOX_RECT, width=2)

        pygame.display.update()

# Encerrar o Pygame
pygame.quit()
