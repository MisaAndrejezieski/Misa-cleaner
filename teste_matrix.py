import tkinter as tk

from matrix_rain import MatrixRain


def testar_matrix():
	root = tk.Tk()
	root.geometry("800x600")
	root.withdraw()

	matrix = MatrixRain(root)
	assert matrix.colunas

	root.update()
	matrix.parar()
	matrix.destroy()
	root.destroy()


if __name__ == "__main__":
	testar_matrix()
	print("Teste Matrix aprovado")