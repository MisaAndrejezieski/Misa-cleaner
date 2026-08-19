import tkinter as tk

from matrix_style import exibir_chuva_matrix, imprimir_matrix, limpar_terminal
from ui import MisaCleanerUI


def main():
    # 🌌 INTRODUÇÃO MATRIX
    limpar_terminal()
    
    imprimir_matrix("╔══════════════════════════════════════════╗", delay=0.02)
    imprimir_matrix("║          MISA-CLEANER v1.0             ║", delay=0.05)
    imprimir_matrix("║   ── Caçador de Resquícios Digitais ── ║", delay=0.05)
    imprimir_matrix("╚══════════════════════════════════════════╝", delay=0.02)
    
    imprimir_matrix("\n>> PREPARANDO SISTEMA...", delay=0.05)
    imprimir_matrix(">> CARREGANDO PROTOCOLOS MATRIX...", delay=0.03)
    
    # Exibe a chuva Matrix
    exibir_chuva_matrix(tempo_segundos=4, intensidade=0.04)
    
    limpar_terminal()
    
    imprimir_matrix(">> INTERFACE GRÁFICA INICIADA.", delay=0.02)
    imprimir_matrix(">> O SISTEMA ESTÁ PRONTO.\n", delay=0.02)
    
    # Roda a interface
    root = tk.Tk()
    app = MisaCleanerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()