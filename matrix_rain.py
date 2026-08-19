"""
MISA-CLEANER - Efeito Matrix Rain
USANDO BIBLIOTECA PRONTA - pymatrix-rain
"""
import os
import subprocess
import sys
import threading
import tkinter as tk


class MatrixRain:
    """CHUVA MATRIX USANDO BIBLIOTECA PRONTA"""
    
    def __init__(self, parent):
        self.parent = parent
        self.process = None
        self.animando = False
        
    def iniciar(self):
        """INICIA A CHUVA MATRIX EM UMA JANELA SEPARADA"""
        if self.animando:
            return
            
        self.animando = True
        
        # 🌟 CRIA UMA JANELA SEPARADA COM A CHUVA MATRIX
        # Usa o pymatrix-rain em uma thread separada
        def rodar_matrix():
            try:
                # Importa a biblioteca
                from pyrandoms import matrixrain

                # Roda a chuva Matrix em tela cheia
                matrixrain.main()
            except ImportError:
                # Se não tiver a biblioteca, usa o fallback
                self._fallback_matrix()
            except Exception as e:
                print(f"Erro na Matrix: {e}")
                self._fallback_matrix()
        
        # Roda em thread separada para não travar a UI
        self.thread = threading.Thread(target=rodar_matrix)
        self.thread.daemon = True
        self.thread.start()
    
    def _fallback_matrix(self):
        """FALLBACK: CHUVA MATRIX NO TERMINAL (CASO A BIBLIOTECA NÃO ESTEJA INSTALADA)"""
        try:
            # Tenta usar o cmatrix (se estiver instalado)
            subprocess.Popen(['cmatrix', '-s'], shell=True)
        except:
            # Se não tiver nada, usa o nosso próprio código
            self._matrix_simples()
    
    def _matrix_simples(self):
        """VERSÃO SIMPLES DA CHUVA MATRIX (FALLBACK)"""
        import os
        import random
        import time
        
        caracteres = ['日','本','語','の','文','字','を','使','っ','て','い','ま','す',
                     '0','1','2','3','4','5','6','7','8','9',
                     '!','@','#','$','%','&','*','+','=','~']
        
        try:
            while self.animando:
                linha = ''.join(random.choice(caracteres) for _ in range(80))
                print(f'\033[92m{linha}\033[0m')
                time.sleep(0.05)
        except:
            pass
    
    def parar(self):
        """PARA A CHUVA MATRIX"""
        self.animando = False
        if self.process:
            self.process.terminate()
    
    def destruir(self):
        """DESTROI A CHUVA MATRIX"""
        self.parar()