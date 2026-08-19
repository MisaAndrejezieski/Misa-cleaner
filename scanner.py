import os
import shutil
import threading
from datetime import datetime, timedelta
from pathlib import Path


class Scanner:
    def __init__(self):
        self.resultados = []
        self.parar_varredura = False
        # Pastas do sistema que são ignoradas para evitar danos ou erros de permissão
        self.pastas_ignoradas = [
            "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
            "C:\\System32", "C:\\Users\\Public", "C:\\$Recycle.Bin",
            "C:\\Recovery", "C:\\System Volume Information", "C:\\boot",
            "D:\\System Volume Information", "D:\\$Recycle.Bin"
        ]
        
    def verificar_ultimo_acesso(self, caminho):
        """Verifica se a pasta foi acessada há mais de 1 ano"""
        try:
            stat = os.stat(caminho)
            ultimo_acesso = datetime.fromtimestamp(stat.st_atime)
            um_ano_atras = datetime.now() - timedelta(days=365)
            return ultimo_acesso < um_ano_atras
        except (PermissionError, OSError):
            return False

    def calcular_tamanho(self, caminho):
        """Calcula o tamanho total de uma pasta em MB"""
        total = 0
        try:
            for root, dirs, files in os.walk(caminho):
                for f in files:
                    try:
                        fp = os.path.join(root, f)
                        total += os.path.getsize(fp)
                    except (PermissionError, OSError):
                        pass
        except (PermissionError, OSError):
            return 0
        return total / (1024 * 1024)  # Converte bytes para MB

    def escanear_pasta(self, caminho, callback_progresso=None, callback_resultado=None):
        """Varre uma pasta recursivamente procurando pastas obsoletas"""
        if self.parar_varredura:
            return
            
        try:
            if os.path.exists(caminho) and os.path.isdir(caminho):
                # Verifica se é uma pasta obsoleta
                if self.verificar_ultimo_acesso(caminho):
                    tamanho_mb = self.calcular_tamanho(caminho)
                    if tamanho_mb > 1:  # Só considera pastas com mais de 1MB
                        resultado = {
                            'caminho': caminho,
                            'tamanho_mb': tamanho_mb,
                            'ultimo_acesso': datetime.fromtimestamp(os.stat(caminho).st_atime)
                        }
                        self.resultados.append(resultado)
                        if callback_resultado:
                            callback_resultado(resultado)
                
                # Continua varrendo subpastas
                try:
                    itens = os.listdir(caminho)
                except (PermissionError, OSError):
                    itens = []
                    
                for item in itens:
                    if self.parar_varredura:
                        break
                    item_path = os.path.join(caminho, item)
                    if os.path.isdir(item_path):
                        # Verifica se não é uma pasta ignorada
                        if not any(item_path.startswith(ign) for ign in self.pastas_ignoradas):
                            self.escanear_pasta(item_path, callback_progresso, callback_resultado)
                            
            if callback_progresso:
                callback_progresso(caminho)
                
        except (PermissionError, OSError):
            pass  # Ignora pastas sem permissão de acesso

    def escanear_tudo(self, callback_progresso=None, callback_resultado=None):
        """Varre todas as unidades do sistema"""
        self.resultados = []
        self.parar_varredura = False
        
        # Detecta todas as unidades disponíveis (C:, D:, E:, etc.)
        unidades = []
        letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for letra in letras:
            unidade = f"{letra}:\\"
            if os.path.exists(unidade):
                unidades.append(unidade)
        
        for unidade in unidades:
            if self.parar_varredura:
                break
            # Verifica se a unidade não é ignorada
            if not any(unidade.startswith(ign) for ign in self.pastas_ignoradas):
                self.escanear_pasta(unidade, callback_progresso, callback_resultado)
        
        return self.resultados

    def parar(self):
        """Para a varredura imediatamente"""
        self.parar_varredura = True

    def deletar_pasta(self, caminho):
        """Deleta uma pasta com segurança e retorna o resultado"""
        try:
            shutil.rmtree(caminho)
            return True, f"✅ Deletado: {caminho}"
        except Exception as e:
            return False, f"❌ Erro ao deletar {caminho}: {str(e)}"