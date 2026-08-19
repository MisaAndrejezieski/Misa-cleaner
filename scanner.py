import os
import shutil
from datetime import datetime, timedelta

from matrix_style import RESET, VERDE_ESCURO, VERDE_MATRIX, imprimir_matrix


class Scanner:
    def __init__(self):
        self.resultados = []
        self.parar_varredura = False
        self.pastas_ignoradas = [
            "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
            "C:\\System32", "C:\\Users\\Public", "C:\\$Recycle.Bin",
            "C:\\System Volume Information", "D:\\System Volume Information"
        ]
        
    def verificar_ultimo_acesso(self, caminho):
        try:
            stat = os.stat(caminho)
            ultimo_acesso = datetime.fromtimestamp(stat.st_atime)
            um_ano_atras = datetime.now() - timedelta(days=365)
            return ultimo_acesso < um_ano_atras
        except:
            return False

    def calcular_tamanho(self, caminho):
        total = 0
        try:
            for root, dirs, files in os.walk(caminho):
                for f in files:
                    try:
                        total += os.path.getsize(os.path.join(root, f))
                    except:
                        pass
        except:
            return 0
        return total / (1024 * 1024)

    def escanear_pasta(self, caminho, callback_progresso=None, callback_resultado=None):
        if self.parar_varredura:
            return
            
        try:
            if os.path.exists(caminho) and os.path.isdir(caminho):
                if self.verificar_ultimo_acesso(caminho):
                    tamanho_mb = self.calcular_tamanho(caminho)
                    if tamanho_mb > 1:
                        resultado = {
                            'caminho': caminho,
                            'tamanho_mb': tamanho_mb,
                            'ultimo_acesso': datetime.fromtimestamp(os.stat(caminho).st_atime)
                        }
                        self.resultados.append(resultado)
                        
                        # 🟢 EFEITO MATRIX: Achamos uma relíquia!
                        msg = f">>> SISTEMA: RELÍQUIA ENCONTRADA EM {caminho} ({tamanho_mb:.1f} MB)"
                        imprimir_matrix(msg, delay=0.02, cor=VERDE_MATRIX)
                        
                        if callback_resultado:
                            callback_resultado(resultado)
                
                try:
                    itens = os.listdir(caminho)
                except:
                    itens = []
                    
                for item in itens:
                    if self.parar_varredura:
                        break
                    item_path = os.path.join(caminho, item)
                    if os.path.isdir(item_path):
                        if not any(item_path.startswith(ign) for ign in self.pastas_ignoradas):
                            self.escanear_pasta(item_path, callback_progresso, callback_resultado)
                            
            if callback_progresso:
                callback_progresso(caminho)
                
        except (PermissionError, OSError):
            pass

    def escanear_tudo(self, callback_progresso=None, callback_resultado=None):
        self.resultados = []
        self.parar_varredura = False
        
        imprimir_matrix(">> INICIANDO PROTOCOLO MISA-CLEANER...", delay=0.05)
        imprimir_matrix(">> VARREDURA MATRIX ATIVADA. AGUARDE...", delay=0.03)
        
        unidades = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
        
        for unidade in unidades:
            if self.parar_varredura:
                break
            if not any(unidade.startswith(ign) for ign in self.pastas_ignoradas):
                self.escanear_pasta(unidade, callback_progresso, callback_resultado)
        
        imprimir_matrix(">> VARREDURA CONCLUÍDA. SISTEMA SEGURO.", delay=0.03)
        return self.resultados

    def parar(self):
        self.parar_varredura = True
        imprimir_matrix(">> PROTOCOLO DE PARADA INICIADO.", cor=VERDE_ESCURO)

    def deletar_pasta(self, caminho):
        try:
            shutil.rmtree(caminho)
            imprimir_matrix(f">> EXCLUSÃO CONFIRMADA: {caminho}", cor=VERDE_ESCURO)
            return True, f"EXCLUÍDO: {caminho}"
        except Exception as e:
            imprimir_matrix(f">> ERRO NA EXCLUSÃO: {caminho}", cor=VERDE_ESCURO)
            return False, f"ERRO: {str(e)}"