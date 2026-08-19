import random
import sys
import time

# Cores ANSI para o efeito Matrix
VERDE_MATRIX = '\033[92m'
VERDE_CLARO = '\033[92m'
VERDE_ESCURO = '\033[32m'
RESET = '\033[0m'
NEGRITO = '\033[1m'

def imprimir_matrix(texto, delay=0.01, cor=VERDE_MATRIX):
    """Imprime o texto com efeito de digitação Matrix"""
    for char in texto:
        sys.stdout.write(cor + char + RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # Quebra de linha no final

def linha_matrix_aleatoria():
    """Gera uma linha de caracteres aleatórios estilo Matrix (katakana)"""
    # Conjunto de caracteres que parecem Matrix
    caracteres = ['日', '本', '語', 'の', '文', '字', 'を', '使', 'っ', 'て', 'い', 'ま', 'す', '!', '@', '#', '$', '%', '&', '0', '1']
    linha = ''.join(random.choice(caracteres) for _ in range(random.randint(20, 40)))
    return linha

def exibir_chuva_matrix(tempo_segundos=1):
    """Exibe uma breve 'chuva de código' antes de começar"""
    inicio = time.time()
    while time.time() - inicio < tempo_segundos:
        # Pula algumas linhas para dar efeito de "queda"
        sys.stdout.write('\n' * random.randint(1, 3))
        linha = linha_matrix_aleatoria()
        cores = [VERDE_MATRIX, VERDE_CLARO, VERDE_ESCURO]
        cor = random.choice(cores)
        sys.stdout.write(cor + linha + RESET)
        sys.stdout.flush()
        time.sleep(0.1)
    # Limpa a tela de forma suave para começar o scanner
    print('\033[H\033[J', end='')