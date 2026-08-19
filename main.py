import tkinter as tk

from matrix_style import VERDE_MATRIX, exibir_chuva_matrix, imprimir_matrix
from ui import MisaCleanerUI


def main():
    # 🌌 INTRODUÇÃO MATRIX
    print('\033[H\033[J', end='')  # Limpa o terminal
    imprimir_matrix("BEM-VINDO AO MISA-CLEANER", delay=0.08)
    imprimir_matrix("PREPARANDO O SISTEMA...", delay=0.05)
    
    # Exibe a "chuva de código" por 3 segundos
    exibir_chuva_matrix(tempo_segundos=3)
    
    # Limpa a tela de vez e inicia a interface
    print('\033[H\033[J', end='')
    imprimir_matrix(">> INTERFACE GRÁFICA INICIADA. O SISTEMA ESTÁ PRONTO.", delay=0.02)
    
    # Roda o Tkinter
    root = tk.Tk()
    app = MisaCleanerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()