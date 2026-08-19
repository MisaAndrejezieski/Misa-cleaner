import os
import random
import sys
import time

# Cores ANSI
VERDE_MATRIX = '\033[92m'
VERDE_CLARO = '\033[92m'
VERDE_ESCURO = '\033[32m'
AMARELO = '\033[93m'
VERMELHO = '\033[91m'
AZUL = '\033[94m'
RESET = '\033[0m'
NEGRITO = '\033[1m'

def imprimir_matrix(texto, delay=0.01, cor=VERDE_MATRIX):
    """Imprime com efeito de digitação Matrix"""
    for char in texto:
        sys.stdout.write(cor + char + RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def linha_matrix_aleatoria(comprimento=None):
    """Gera linha aleatória estilo Matrix"""
    if comprimento is None:
        comprimento = random.randint(20, 50)
    caracteres = ['日','本','語','の','文','字','を','使','っ','て','い','ま','す',
                  '0','1','!','@','#','$','%','&','*','+','=','~']
    return ''.join(random.choice(caracteres) for _ in range(comprimento))

def exibir_chuva_matrix(tempo_segundos=3, intensidade=0.05):
    """Exibe a chuva Matrix com intensidade controlada"""
    linhas = os.get_terminal_size().lines if hasattr(os, 'get_terminal_size') else 30
    
    # Salva posição do cursor
    sys.stdout.write('\033[s')
    
    inicio = time.time()
    while time.time() - inicio < tempo_segundos:
        # Limpa a tela parcialmente
        sys.stdout.write('\033[0;0H')
        
        # Gera várias linhas Matrix
        for _ in range(linhas - 2):
            linha = linha_matrix_aleatoria()
            # Efeito de queda - algumas linhas começam do meio
            if random.random() < 0.3:
                sys.stdout.write(' ' * random.randint(5, 20))
            cor = random.choice([VERDE_MATRIX, VERDE_CLARO, VERDE_ESCURO])
            sys.stdout.write(cor + linha + RESET)
            sys.stdout.write('\n')
        
        time.sleep(intensidade)
    
    # Restaura o cursor
    sys.stdout.write('\033[u')
    sys.stdout.flush()

def limpar_terminal():
    """Limpa o terminal de forma cross-platform"""
    os.system('cls' if os.name == 'nt' else 'clear')