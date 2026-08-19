"""
MISA-CLEANER - Ponto de entrada
"""
import tkinter as tk

from ui import MisaCleanerUI


def main() -> None:
    """Função principal"""
    root = tk.Tk()
    
    # Configurar scaling para HiDPI
    try:
        root.tk.call('tk', 'scaling', 1.5)
    except:
        pass
        
    app = MisaCleanerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()