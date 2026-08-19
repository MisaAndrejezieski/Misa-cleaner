import hashlib
import os
import shutil
from datetime import datetime, timedelta


class Scanner:
    def __init__(self):
        self.resultados = {
            'resquicios': [],
            'obsoletos': [],
            'duplicados': []
        }
        self.parar_varredura = False
        
        # Pastas comuns de programas
        self.pastas_sistema = [
            os.environ.get('APPDATA', ''),
            os.environ.get('LOCALAPPDATA', ''),
            os.environ.get('PROGRAMFILES', ''),
            os.environ.get('PROGRAMFILES(X86)', ''),
            os.path.expanduser('~')
        ]
        
        # ==========================================
        # 🛡️ LISTA DE PASTAS IGNORADAS (Corrigida)
        # ==========================================
        self.pastas_ignoradas = [
            # Pastas críticas do Windows
            "C:\\Windows", "C:\\System32", "C:\\$Recycle.Bin",
            "C:\\System Volume Information", "C:\\Windows\\WinSxS", "C:\\Windows\\Installer",
            "C:\\Users\\Public", os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp'),
            
            # 🟢 IGNORAR PASTAS DE CACHE DOS NAVEGADORES E PYTHON
            # Google Chrome
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data'),
            # Microsoft Edge
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data'),
            # PyWebview (biblioteca usada pelo seu programa)
            os.path.join(os.environ.get('APPDATA', ''), 'pywebview'),
            # Ollama (apareceu no seu log)
            os.path.join(os.environ.get('APPDATA', ''), 'ollama app.exe'),
            
            # 🟢 IGNORAR PASTAS DE DESENVOLVIMENTO
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Microsoft VS Code'),
            os.path.join(os.environ.get('APPDATA', ''), 'Code'),
            "node_modules", ".git", ".venv", "__pycache__"
        ]
        # ==========================================

        # Programas conhecidos
        self.programas_conhecidos = [
            'Adobe', 'Photoshop', 'Illustrator', 'Premiere', 'AfterEffects',
            'Spotify', 'Steam', 'Discord', 'Slack',
            'Zoom', 'Teams', 'Notion', 'Obsidian', 'VSCode', 'Visual Studio',
            'Git', 'Node.js', 'Python', 'Anaconda', 'Chrome',
            'Firefox', 'Edge', 'Opera', 'Brave', 'Vivaldi',
            'Minecraft', 'Epic Games', 'Origin', 'Ubisoft', 'GOG',
            'Office', 'Word', 'Excel', 'PowerPoint', 'Outlook',
            'Skype', 'Telegram', 'WhatsApp', 'Signal',
            'Blender', 'Unity', 'Unreal Engine',
            'WinRAR', '7-Zip', 'VLC', 'Media Player Classic',
            'Notepad++', 'Sublime Text', 'Atom',
            'Postman', 'Insomnia', 'Docker', 'Kubernetes',
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis',
            'VirtualBox', 'VMware', 'QEMU'
        ]

    def verificar_se_programa_existe(self, nome_programa):
        for pasta in self.pastas_sistema[:3]:
            if not pasta:
                continue
            caminho_programa = os.path.join(pasta, nome_programa)
            if os.path.exists(caminho_programa):
                return True
        
        try:
            import subprocess
            result = subprocess.run(
                ['where', nome_programa.lower()],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                return True
        except:
            pass
            
        return False

    def encontrar_resquicios_programas(self, callback_progresso=None, callback_resultado=None):
        resultados = []
        
        for pasta_base in self.pastas_sistema[:2]:
            if not pasta_base or not os.path.exists(pasta_base):
                continue
                
            try:
                for item in os.listdir(pasta_base):
                    if self.parar_varredura:
                        return resultados
                        
                    caminho_item = os.path.join(pasta_base, item)
                    if not os.path.isdir(caminho_item):
                        continue
                    
                    if self._deve_ignorar(caminho_item):
                        continue
                        
                    for programa in self.programas_conhecidos:
                        if programa.lower() in item.lower():
                            if not self.verificar_se_programa_existe(programa):
                                tamanho = self.calcular_tamanho(caminho_item)
                                if tamanho > 1:
                                    resultado = {
                                        'caminho': caminho_item,
                                        'tamanho_mb': tamanho,
                                        'tipo': 'resquicio',
                                        'programa': programa,
                                        'ultimo_acesso': self.obter_ultimo_acesso(caminho_item)
                                    }
                                    resultados.append(resultado)
                                    if callback_resultado:
                                        callback_resultado(resultado)
                            break
                    
                    if callback_progresso:
                        callback_progresso(caminho_item)
                        
            except (PermissionError, OSError):
                pass
                
        return resultados

    def encontrar_obsoletos(self, callback_progresso=None, callback_resultado=None):
        resultados = []
        um_ano_atras = datetime.now() - timedelta(days=365)
        
        pastas_para_varer = [p for p in self.pastas_sistema if p and os.path.exists(p)]
        
        for pasta in pastas_para_varer:
            if self.parar_varredura:
                return resultados
            try:
                self._escavar_obsoletos(pasta, um_ano_atras, resultados, callback_progresso, callback_resultado)
            except (PermissionError, OSError):
                continue
                
        return resultados

    def _escavar_obsoletos(self, caminho, data_limite, resultados, callback_progresso, callback_resultado):
        if self.parar_varredura:
            return
        
        if self._deve_ignorar(caminho):
            return
            
        try:
            for item in os.listdir(caminho):
                if self.parar_varredura:
                    return
                    
                item_path = os.path.join(caminho, item)
                
                try:
                    ultimo_acesso = datetime.fromtimestamp(os.stat(item_path).st_atime)
                    
                    if ultimo_acesso < data_limite:
                        if os.path.isdir(item_path):
                            tamanho = self.calcular_tamanho(item_path)
                            if tamanho > 1:
                                resultado = {
                                    'caminho': item_path,
                                    'tamanho_mb': tamanho,
                                    'tipo': 'obsoleto',
                                    'ultimo_acesso': ultimo_acesso
                                }
                                resultados.append(resultado)
                                if callback_resultado:
                                    callback_resultado(resultado)
                    
                    if os.path.isdir(item_path):
                        self._escavar_obsoletos(item_path, data_limite, resultados, callback_progresso, callback_resultado)
                        
                except (PermissionError, OSError):
                    continue
                    
            if callback_progresso:
                callback_progresso(caminho)
                
        except (PermissionError, OSError):
            pass

    def encontrar_duplicados(self, callback_progresso=None, callback_resultado=None):
        resultados = []
        hash_map = {}
        pastas_para_varer = [p for p in self.pastas_sistema if p and os.path.exists(p)]
        arquivos_verificados = 0
        limite_arquivos = 1000
        
        for pasta in pastas_para_varer:
            if self.parar_varredura:
                return resultados
            try:
                arquivos_verificados = self._escavar_duplicados(
                    pasta, hash_map, callback_progresso, arquivos_verificados, limite_arquivos
                )
                if arquivos_verificados >= limite_arquivos:
                    break
            except (PermissionError, OSError):
                continue
                
        for file_hash, arquivos in hash_map.items():
            if len(arquivos) > 1:
                tamanho_total = sum(self.calcular_tamanho_arquivo(a) for a in arquivos)
                if tamanho_total > 1:
                    resultado = {
                        'hash': file_hash,
                        'arquivos': arquivos,
                        'tamanho_total_mb': tamanho_total,
                        'tipo': 'duplicado',
                        'caminho': arquivos[0]
                    }
                    resultados.append(resultado)
                    if callback_resultado:
                        callback_resultado(resultado)
                    
        return resultados

    def _escavar_duplicados(self, caminho, hash_map, callback_progresso, contador, limite):
        if self.parar_varredura or contador >= limite:
            return contador
            
        if self._deve_ignorar(caminho):
            return contador
            
        try:
            for item in os.listdir(caminho):
                if self.parar_varredura or contador >= limite:
                    return contador
                    
                item_path = os.path.join(caminho, item)
                
                if os.path.isfile(item_path):
                    try:
                        tamanho = os.path.getsize(item_path) / (1024 * 1024)
                        if tamanho > 1:
                            file_hash = self.calcular_hash(item_path)
                            if file_hash:
                                if file_hash not in hash_map:
                                    hash_map[file_hash] = []
                                hash_map[file_hash].append(item_path)
                                contador += 1
                    except (PermissionError, OSError):
                        pass
                elif os.path.isdir(item_path):
                    contador = self._escavar_duplicados(
                        item_path, hash_map, callback_progresso, contador, limite
                    )
                    
            if callback_progresso:
                callback_progresso(caminho)
                
        except (PermissionError, OSError):
            pass
            
        return contador

    def _deve_ignorar(self, caminho):
        for ignorado in self.pastas_ignoradas:
            if caminho and ignorado:
                if caminho.startswith(ignorado) or ignorado in caminho.split(os.sep):
                    return True
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

    def calcular_tamanho_arquivo(self, caminho):
        try:
            return os.path.getsize(caminho) / (1024 * 1024)
        except:
            return 0

    def calcular_hash(self, caminho):
        try:
            hash_md5 = hashlib.md5()
            with open(caminho, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None

    def obter_ultimo_acesso(self, caminho):
        try:
            return datetime.fromtimestamp(os.stat(caminho).st_atime)
        except:
            return None

    def escanear_tudo(self, callback_progresso=None, callback_resultado=None):
        self.resultados = {
            'resquicios': [],
            'obsoletos': [],
            'duplicados': []
        }
        self.parar_varredura = False
        
        try:
            self.resultados['resquicios'] = self.encontrar_resquicios_programas(
                callback_progresso, callback_resultado
            )
            
            if not self.parar_varredura:
                self.resultados['obsoletos'] = self.encontrar_obsoletos(
                    callback_progresso, callback_resultado
                )
            
            if not self.parar_varredura:
                self.resultados['duplicados'] = self.encontrar_duplicados(
                    callback_progresso, callback_resultado
                )
                
        except Exception as e:
            print(f"Erro durante a varredura: {e}")
            
        return self.resultados

    def parar(self):
        self.parar_varredura = True

    def deletar_pasta(self, caminho):
        try:
            shutil.rmtree(caminho)
            return True, f"EXCLUÍDO: {caminho}"
        except Exception as e:
            return False, f"ERRO: {str(e)}"

    def deletar_arquivo(self, caminho):
        try:
            os.remove(caminho)
            return True, f"EXCLUÍDO: {caminho}"
        except Exception as e:
            return False, f"ERRO: {str(e)}"