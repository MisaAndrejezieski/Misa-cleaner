import os
import tempfile
import unittest

from scanner import Scanner


class TestScanner(unittest.TestCase):
    def criar_scanner_de_teste(self, pasta: str) -> Scanner:
        scanner = Scanner()
        scanner.pastas_sistema = [pasta]
        scanner.pastas_ignoradas = []
        scanner.pastas_sistema_protegidas = []
        scanner.programas_conhecidos = []
        return scanner

    def test_encontra_arquivos_duplicados_em_pasta_temporaria(self):
        with tempfile.TemporaryDirectory() as pasta:
            conteudo = b"MISA-CLEANER\n" * 100_000
            primeiro = os.path.join(pasta, "primeiro.bin")
            segundo = os.path.join(pasta, "segundo.bin")

            with open(primeiro, "wb") as arquivo:
                arquivo.write(conteudo)
            with open(segundo, "wb") as arquivo:
                arquivo.write(conteudo)

            scanner = self.criar_scanner_de_teste(pasta)
            resultados = scanner.escanear_tudo()

            self.assertEqual(len(resultados["resquicios"]), 0)
            self.assertEqual(len(resultados["obsoletos"]), 0)
            self.assertEqual(len(resultados["duplicados"]), 1)
            self.assertEqual(len(resultados["duplicados"][0]["arquivos"]), 2)

    def test_deleta_apenas_o_arquivo_solicitado(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "remover.bin")
            with open(caminho, "wb") as arquivo:
                arquivo.write(b"arquivo de teste")

            scanner = self.criar_scanner_de_teste(pasta)
            sucesso, _ = scanner.deletar_arquivo(caminho)

            self.assertTrue(sucesso)
            self.assertFalse(os.path.exists(caminho))


if __name__ == "__main__":
    unittest.main()