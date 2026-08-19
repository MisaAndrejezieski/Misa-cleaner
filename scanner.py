import os
import shutil
from datetime import datetime, timedelta


class Scanner:
    def __init__(self):
        self.resultados = []
        self.parar_varredura = False
        self.pastas_alvo = [
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\Users\\{}\\AppData\\Local",
            "C:\\Users\\{}\\AppData\\Roaming",
            "C:\\Users\\{}\\Documents",
            "D:\\"
        ]
        self.pastas_ignoradas = [
            "C:\\Program Files\\WindowsApps",
            "C:\\Program Files\\Common Files",
            "C:\\Program Files (x86)\\Common Files"
        ]
        
    def _obter_usuario(self):
        return os.getenv('USERNAME', 'Default')

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

    def escanear(self, callback_progresso=None, callback_resultado=None):
        self.resultados = []
        self.parar_varredura = False
        usuario = self._obter_usuario()
        
        pastas_expandidas = []
        for p in self.pastas_alvo:
            if "{}" in p:
                pastas_expandidas.append(p.format(usuario))
            else:
                pastas_expandidas.append(p)
        
        for pasta in pastas_expandidas:
            if self.parar_varredura:
                break
            self._escanear_pasta(pasta, callback_progresso, callback_resultado)
        
        return self.resultados

    def _escanear_pasta(self, caminho, callback_progresso=None, callback_resultado=None):
        if self.parar_varredura:
            return
            
        try:
            if os.path.exists(caminho) and os.path.isdir(caminho):
                if self.verificar_ultimo_acesso(caminho):
                    tamanho_mb = self.calcular_tamanho(caminho)
                    if tamanho_mb > 1:
                        nome = os.path.basename(caminho).lower()
                        if 'temp' in nome or 'cache' in nome or 'old' in nome or 'backup' in nome:
                            resultado = {
                                'caminho': caminho,
                                'tamanho_mb': tamanho_mb,
                                'ultimo_acesso': datetime.fromtimestamp(os.stat(caminho).st_atime)
                            }
                            self.resultados.append(resultado)
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
                            self._escanear_pasta(item_path, callback_progresso, callback_resultado)
                            
            if callback_progresso:
                callback_progresso(caminho)
                
        except (PermissionError, OSError):
            pass

    def parar(self):
        self.parar_varredura = True

    def deletar_pasta(self, caminho):
        try:
            shutil.rmtree(caminho)
            return True, caminho
        except Exception as e:
            return False, str(e)