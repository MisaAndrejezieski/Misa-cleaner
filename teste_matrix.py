import tkinter as tk

from matrix_rain import MatrixFullscreen

root = tk.Tk()
root.geometry("800x600")
root.title("TESTE MATRIX")

# Inicia a Matrix
matrix = MatrixFullscreen(root)
matrix.iniciar()

# Fecha após 5 segundos
root.after(5000, lambda: matrix.parar())
root.after(5000, root.destroy)

root.mainloop()