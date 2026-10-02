"""
MISA-CLEANER - Testes do MatrixRain
VERSÃO 4.0 - Testa criação, animação, parada e destruição
"""
import tkinter as tk

from matrix_rain import MatrixRain


def _criar_root():
    root = tk.Tk()
    root.geometry("800x600")
    root.update_idletasks()
    root.update()
    return root


def test_criacao_matrix():
    root = None
    matrix = None
    try:
        root = _criar_root()
        matrix = MatrixRain(root)
        matrix.place(x=0, y=0, relwidth=1, relheight=1)

        root.update()
        root.after(100, lambda: None)
        root.update()

        assert matrix.colunas, "MatrixRain nao criou colunas"
        assert len(matrix.colunas) > 0, "Lista de colunas esta vazia"

        for col in matrix.colunas:
            assert 'itens' in col
            assert 'chars' in col
            assert 'visiveis' in col
            assert len(col['itens']) == MatrixRain.MAX_CARACTERES_COLUNA
            assert len(col['visiveis']) == MatrixRain.MAX_CARACTERES_COLUNA

        print(f"OK: {len(matrix.colunas)} colunas criadas")

    finally:
        if matrix:
            matrix.parar()
            matrix.destroy()
        if root:
            root.destroy()


def test_parar_cancela_after():
    root = None
    matrix = None
    try:
        root = _criar_root()
        matrix = MatrixRain(root)
        matrix.place(x=0, y=0, relwidth=1, relheight=1)
        root.update()
        root.after(100, lambda: None)
        root.update()

        matrix.parar()

        assert matrix.animando is False
        assert matrix._after_id is None
        print("OK: parar() cancelou o after")

    finally:
        if matrix:
            try:
                matrix.destroy()
            except Exception:
                pass
        if root:
            root.destroy()


def test_parar_multiplas_vezes():
    root = None
    matrix = None
    try:
        root = _criar_root()
        matrix = MatrixRain(root)
        matrix.place(x=0, y=0, relwidth=1, relheight=1)
        root.update()

        for _ in range(5):
            matrix.parar()

        assert matrix.animando is False
        assert matrix._after_id is None
        print("OK: parar() idempotente")

    finally:
        if matrix:
            try:
                matrix.destroy()
            except Exception:
                pass
        if root:
            root.destroy()


def test_destroy_sem_crash():
    root = None
    matrix = None
    try:
        root = _criar_root()
        matrix = MatrixRain(root)
        matrix.place(x=0, y=0, relwidth=1, relheight=1)
        root.update()

        matrix.parar()
        matrix.destroy()
        print("OK: destroy() apos parar() sem crash")

    finally:
        if root:
            root.destroy()


if __name__ == "__main__":
    test_criacao_matrix()
    test_parar_cancela_after()
    test_parar_multiplas_vezes()
    test_destroy_sem_crash()
    print("\nTodos os testes do MatrixRain passaram")