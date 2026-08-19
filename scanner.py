"""
MISA-CLEANER - Scanner de Resquícios Digitais
Versão refatorada com tratamento de erros robusto e filtros inteligentes
"""
import hashlib
import os
import shutil
import subprocess
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple

from logger import Logger, LogNivel


class Scanner:
    """Scanner profissional para encontrar resquícios, obsoletos e duplicados"""
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
        self.resultados = {
            'resquicios': [],
            'obsoletos': [],
            'duplicados': []
        }
        self.parar_varredura = False
        self.total_verificados = 0
        
        # Pastas comuns de programas (ESCOPO REDUZIDO)
        self.pastas_sistema = [
            os.environ.get('APPDATA', ''),           # C:\Users\Usuario\AppData\Roaming
            os.environ.get('LOCALAPPDATA', ''),      # C:\Users\Usuario\AppData\Local
            os.environ.get('PROGRAMFILES', ''),      # C:\Program Files
            os.environ.get('PROGRAMFILES(X86)', ''), # C:\Program Files (x86)
            # REMOVIDO: os.path.expanduser('~')  # NUNCA varrer a raiz do usuário!
        ]
        
        # 🛡️ LISTA COMPLETA DE PASTAS IGNORADAS (BLOQUEIO TOTAL)
        self.pastas_ignoradas = self._build_ignore_list()
        
        # Programas conhecidos para detecção de resquícios
        self.programas_conhecidos = [
            'Adobe', 'Photoshop', 'Illustrator', 'Premiere', 'AfterEffects',
            'Lightroom', 'Acrobat', 'Reader',
            'Spotify', 'Steam', 'Discord', 'Slack',
            'Zoom', 'Teams', 'Notion', 'Obsidian', 
            'VSCode', 'Visual Studio', 'Code',
            'Git', 'Node.js', 'Python', 'Anaconda', 
            'Chrome', 'Firefox', 'Edge', 'Opera', 'Brave', 'Vivaldi',
            'Minecraft', 'Epic Games', 'Origin', 'Ubisoft', 'GOG',
            'Office', 'Word', 'Excel', 'PowerPoint', 'Outlook', 'OneNote',
            'Skype', 'Telegram', 'WhatsApp', 'Signal',
            'Blender', 'Unity', 'Unreal Engine', 'Godot',
            'WinRAR', '7-Zip', 'VLC', 'Media Player Classic', 'MPC-HC',
            'Notepad++', 'Sublime Text', 'Atom', 'Brackets',
            'Postman', 'Insomnia', 'Docker', 'Kubernetes', 'Minikube',
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite',
            'VirtualBox', 'VMware', 'QEMU', 'WSL',
            'GitHub Desktop', 'GitKraken', 'SourceTree',
            'Figma', 'Sketch', 'InVision',
            'OBS Studio', 'Streamlabs', 'XSplit',
            'Cisco Webex', 'Google Meet', 'Jitsi',
            'Todoist', 'Trello', 'Asana', 'Jira',
            'HubSpot', 'Salesforce', 'Zendesk',
            'Android Studio', 'Xcode', 'IntelliJ', 'PyCharm', 'WebStorm'
        ]
        
        # Extensões de arquivos ignorados (nunca considerar como resquícios)
        self.extensoes_ignoradas = {
            '.exe', '.msi', '.dll', '.so', '.dylib', '.sys',
            '.pyc', '.pyo', '.pyd', '.class', '.o', '.obj',
            '.cache', '.log', '.tmp', '.temp', '.swp', '.bak',
            '.ico', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp',
            '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.wav', '.flac',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'
        }
        
    def _build_ignore_list(self) -> List[str]:
        """Constrói lista completa de pastas ignoradas"""
        user = os.path.expanduser('~')
        localappdata = os.environ.get('LOCALAPPDATA', '')
        appdata = os.environ.get('APPDATA', '')
        temp = os.environ.get('TEMP', '')
        tmp = os.environ.get('TMP', '')
        
        # Pastas do sistema (CRÍTICO)
        sistema = [
            "C:\\Windows", "C:\\System32", "C:\\SysWOW64",
            "C:\\$Recycle.Bin", "C:\\System Volume Information",
            "C:\\Windows\\WinSxS", "C:\\Windows\\Installer",
            "C:\\Windows\\Microsoft.NET", "C:\\Windows\\assembly",
            "C:\\ProgramData", "C:\\Users\\Public", "C:\\PerfLogs",
            "C:\\Recovery", "C:\\Documents and Settings",
            "C:\\Program Files\\WindowsApps",
            "C:\\Program Files\\Common Files",
            "C:\\Program Files (x86)\\Common Files",
            "C:\\Program Files\\Windows Defender",
            "C:\\Program Files\\Windows Mail",
            "C:\\Program Files\\Windows Media Player",
            "C:\\Program Files\\Windows NT",
            "C:\\Program Files\\Microsoft SQL Server",
            "C:\\Program Files\\dotnet"
        ]
        
        # Pastas do usuário (NUNCA VARRER)
        usuario = [
            os.path.join(user, 'Desktop'),
            os.path.join(user, 'Documents'),
            os.path.join(user, 'Downloads'),
            os.path.join(user, 'Music'),
            os.path.join(user, 'Pictures'),
            os.path.join(user, 'Videos'),
            os.path.join(user, 'OneDrive'),
            os.path.join(user, 'Dropbox'),
            os.path.join(user, 'Google Drive'),
            os.path.join(user, 'iCloudDrive'),
            os.path.join(user, '.cache'),
            os.path.join(user, '.config'),
            os.path.join(user, '.local'),
            os.path.join(user, '.vscode'),
            os.path.join(user, '.mozilla'),
            os.path.join(user, '.npm'),
            os.path.join(user, '.yarn'),
            os.path.join(user, '.gradle'),
            os.path.join(user, '.m2'),
            os.path.join(user, '.android'),
            os.path.join(user, '.dotnet'),
            os.path.join(user, '.rustup'),
            os.path.join(user, '.cargo'),
            os.path.join(user, '.venv'),
            os.path.join(user, 'venv'),
            os.path.join(user, 'env'),
            os.path.join(user, '.git'),
            os.path.join(user, '.svn'),
            os.path.join(user, '.hg'),
            os.path.join(user, 'AppData\\Local\\Temp'),
            os.path.join(user, 'AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files'),
            os.path.join(user, 'AppData\\Local\\Microsoft\\Windows\\Explorer'),
            os.path.join(user, 'AppData\\Local\\Microsoft\\Windows\\Caches'),
        ]
        
        # Pastas de navegadores (causam erro 267)
        navegadores = [
            os.path.join(localappdata, 'Google', 'Chrome'),
            os.path.join(localappdata, 'Microsoft', 'Edge'),
            os.path.join(localappdata, 'Mozilla', 'Firefox'),
            os.path.join(localappdata, 'Google', 'Chrome Beta'),
            os.path.join(localappdata, 'Google', 'Chrome Dev'),
            os.path.join(localappdata, 'Google', 'Chrome SxS'),
            os.path.join(appdata, 'Opera Software', 'Opera'),
            os.path.join(localappdata, 'BraveSoftware', 'Brave-Browser'),
            os.path.join(localappdata, 'Vivaldi'),
            os.path.join(appdata, 'pywebview'),
            "EBWebView", "GitHubDesktop", "Olk", "Clipchamp"
        ]
        
        # Pastas de desenvolvimento
        dev = [
            os.path.join(localappdata, 'Programs', 'Microsoft VS Code'),
            os.path.join(appdata, 'Code'),
            os.path.join(localappdata, 'Programs', 'Git'),
            os.path.join(localappdata, 'Programs', 'Python'),
            os.path.join(localappdata, 'Programs', 'Python3'),
            "node_modules", ".git", ".venv", "venv", "__pycache__", 
            "dist", "build", "out", "target", "bin", "obj",
            ".idea", ".vscode", ".vs", ".eclipse", ".classpath",
            ".project", ".settings", ".metadata"
        ]
        
        # Pastas temporárias
        temp_pastas = [
            temp, tmp,
            os.path.join(user, 'AppData', 'Local', 'Temp'),
            os.path.join(user, 'AppData', 'Local', 'Temp2'),
            os.path.join(user, 'AppData', 'Local', 'Cache'),
            "C:\\Windows\\Temp"
        ]
        
        # Combinar todas as listas
        todas = sistema + usuario + navegadores + dev + temp_pastas
        
        # Filtrar valores vazios e normalizar
        return [os.path.normpath(p) for p in todas if p and os.path.normpath(p)]
        
    def _deve_ignorar(self, caminho: str) -> bool:
        """
        Verifica se o caminho deve ser ignorado usando correspondência exata
        de componentes de diretório (evita falsos positivos)
        """
        if not caminho:
            return True
            
        try:
            caminho_norm = os.path.normpath(caminho).lower()
            partes = caminho_norm.split(os.sep)
            
            for ignorado in self.pastas_ignoradas:
                if not ignorado:
                    continue
                    
                ignorado_norm = os.path.normpath(ignorado).lower()
                partes_ignorado = ignorado_norm.split(os.sep)
                
                # Verifica se o caminho ignorado corresponde a um prefixo de pastas
                if len(partes_ignorado) <= len(partes):
                    if partes[:len(partes_ignorado)] == partes_ignorado:
                        # Se o caminho termina com o ignorado OU tem mais pastas depois
                        if len(partes) >= len(partes_ignorado):
                            return True
                            
                # Verifica se o nome da pasta está no caminho (apenas para alguns casos especiais)
                # Para 'node_modules', '.git', etc., verifica qualquer nível
                if ignorado_norm in ['node_modules', '.git', '.venv', 'venv', '__pycache__']:
                    if ignorado_norm in partes:
                        return True
                        
            return False
            
        except Exception:
            return False
            
    def _verificar_permissao(self, caminho: str) -> Tuple[bool, str]:
        """
        Verifica se tem permissão de acesso ao caminho
        Retorna (tem_permissao, motivo)
        """
        try:
            if os.path.isdir(caminho):
                # Tenta listar o diretório
                os.listdir(caminho)
            else:
                # Tenta abrir o arquivo
                with open(caminho, 'rb') as f:
                    f.read(1)
            return True, ""
        except PermissionError:
            return False, "SEM PERMISSÃO"
        except OSError as e:
            if "267" in str(e):
                return False, "PASTA BLOQUEADA (erro 267)"
            elif "5" in str(e):
                return False, "ACESSO NEGADO"
            else:
                return False, f"ERRO: {str(e)[:50]}"
        except Exception as e:
            return False, f"ERRO: {str(e)[:50]}"
            
    def _calcular_tamanho(self, caminho: str) -> float:
        """
        Calcula tamanho da pasta/arquivo ignorando pastas proibidas
        """
        if self._deve_ignorar(caminho):
            return 0
            
        total = 0
        try:
            if os.path.isfile(caminho):
                return os.path.getsize(caminho) / (1024 * 1024)
                
            for root, dirs, files in os.walk(caminho):
                if self.parar_varredura:
                    return total / (1024 * 1024)
                    
                # Filtra pastas ignoradas em tempo real
                if self._deve_ignorar(root):
                    continue
                    
                for f in files:
                    try:
                        file_path = os.path.join(root, f)
                        if not self._deve_ignorar(file_path):
                            total += os.path.getsize(file_path)
                    except (PermissionError, OSError):
                        continue
                        
        except (PermissionError, OSError):
            pass
            
        return total / (1024 * 1024)

    def _verificar_programa_existe(self, nome_programa: str) -> bool:
        """
        Verifica se um programa está instalado (com timeout e fallback)
        """
        # Primeiro verifica nas pastas do sistema
        for pasta in self.pastas_sistema[:3]:
            if not pasta:
                continue
            caminho_programa = os.path.join(pasta, nome_programa)
            if os.path.exists(caminho_programa):
                return True
                
        # Tenta via 'where' (Windows) com timeout
        try:
            import subprocess
            result = subprocess.run(
                ['where', nome_programa.lower()],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0 and result.stdout.strip():
                return True
        except subprocess.TimeoutExpired:
            self.logger.debug(f"⏱️ Timeout ao verificar programa: {nome_programa}")
        except FileNotFoundError:
            self.logger.debug(f"'where' não disponível para verificar: {nome_programa}")
        except Exception as e:
            self.logger.debug(f"Erro ao verificar {nome_programa}: {str(e)[:50]}")
            
        return False

    def _encontrar_resquicios_programas(self, callback_progresso: Optional[Callable] = None,
                                       callback_resultado: Optional[Callable] = None) -> List[Dict]:
        """Encontra resquícios de programas deletados"""
        resultados = []
        self.logger.info("🔍 BUSCANDO RESQUÍCIOS DE PROGRAMAS...")
        
        for pasta_base in self.pastas_sistema[:3]:  # APPDATA, LOCALAPPDATA, PROGRAMFILES
            if not pasta_base or not os.path.exists(pasta_base):
                continue
                
            self.logger.debug(f"📁 Verificando: {pasta_base}")
                
            try:
                for item in os.listdir(pasta_base):
                    if self.parar_varredura:
                        return resultados
                        
                    caminho_item = os.path.join(pasta_base, item)
                    
                    # Ignora pastas proibidas
                    if self._deve_ignorar(caminho_item):
                        self.logger.debug(f"⏭️ Ignorado (lista negra): {caminho_item}")
                        continue
                        
                    if not os.path.isdir(caminho_item):
                        continue
                        
                    # Verifica permissão
                    tem_perm, motivo = self._verificar_permissao(caminho_item)
                    if not tem_perm:
                        if motivo == "SEM PERMISSÃO":
                            self.logger.aviso(f"🔒 Sem permissão: {caminho_item}")
                        else:
                            self.logger.aviso(f"⚠️ {motivo}: {caminho_item}")
                        continue
                        
                    for programa in self.programas_conhecidos:
                        if programa.lower() in item.lower():
                            if not self._verificar_programa_existe(programa):
                                tamanho = self._calcular_tamanho(caminho_item)
                                if tamanho > 1:  # > 1 MB
                                    resultado = {
                                        'caminho': caminho_item,
                                        'tamanho_mb': tamanho,
                                        'tipo': 'resquicio',
                                        'programa': programa,
                                        'ultimo_acesso': self._obter_ultimo_acesso(caminho_item),
                                        'is_pasta': True
                                    }
                                    resultados.append(resultado)
                                    if callback_resultado:
                                        callback_resultado(resultado)
                                    self.logger.sucesso(f"🔴 Resquício: {programa} ({tamanho:.1f} MB)")
                            break
                            
                    if callback_progresso:
                        callback_progresso(caminho_item)
                        self.total_verificados += 1
                        
            except (PermissionError, OSError) as e:
                self.logger.aviso(f"⚠️ Não foi possível verificar {pasta_base}: {str(e)[:50]}")
                continue
                
        self.logger.info(f"✅ Resquícios encontrados: {len(resultados)}")
        return resultados

    def _encontrar_obsoletos(self, callback_progresso: Optional[Callable] = None,
                            callback_resultado: Optional[Callable] = None) -> List[Dict]:
        """Encontra arquivos/pastas obsoletos (1+ ano sem acesso)"""
        resultados = []
        um_ano_atras = datetime.now() - timedelta(days=365)
        self.logger.info("📂 BUSCANDO ARQUIVOS OBSOLETOS...")
        
        pastas_para_varer = [p for p in self.pastas_sistema if p and os.path.exists(p)]
        
        for pasta in pastas_para_varer:
            if self.parar_varredura:
                return resultados
            try:
                self._escavar_obsoletos(pasta, um_ano_atras, resultados, 
                                       callback_progresso, callback_resultado, 0)
            except (PermissionError, OSError) as e:
                self.logger.aviso(f"⚠️ Não foi possível verificar {pasta}: {str(e)[:50]}")
                continue
                
        self.logger.info(f"✅ Obsoletos encontrados: {len(resultados)}")
        return resultados

    def _escavar_obsoletos(self, caminho: str, data_limite: datetime, resultados: List[Dict],
                          callback_progresso: Optional[Callable], 
                          callback_resultado: Optional[Callable],
                          profundidade: int = 0):
        """Escava recursivamente em busca de obsoletos (com limite de profundidade)"""
        if self.parar_varredura:
            return
            
        # Limite de profundidade para evitar loops
        if profundidade > 20:
            self.logger.debug(f"⏭️ Profundidade máxima atingida: {caminho}")
            return
            
        # Ignora pastas proibidas
        if self._deve_ignorar(caminho):
            self.logger.debug(f"⏭️ Ignorado (lista negra): {caminho}")
            return
            
        # Verifica permissão
        tem_perm, motivo = self._verificar_permissao(caminho)
        if not tem_perm:
            if motivo == "SEM PERMISSÃO":
                self.logger.aviso(f"🔒 Sem permissão: {caminho}")
            else:
                self.logger.aviso(f"⚠️ {motivo}: {caminho}")
            return
            
        try:
            for item in os.listdir(caminho):
                if self.parar_varredura:
                    return
                    
                item_path = os.path.join(caminho, item)
                
                # Ignora arquivos/pastas proibidas
                if self._deve_ignorar(item_path):
                    continue
                    
                try:
                    # Verifica data de último acesso
                    ultimo_acesso = datetime.fromtimestamp(os.stat(item_path).st_atime)
                    
                    if ultimo_acesso < data_limite:
                        if os.path.isdir(item_path):
                            tamanho = self._calcular_tamanho(item_path)
                            if tamanho > 1:  # > 1 MB
                                resultado = {
                                    'caminho': item_path,
                                    'tamanho_mb': tamanho,
                                    'tipo': 'obsoleto',
                                    'ultimo_acesso': ultimo_acesso,
                                    'is_pasta': True
                                }
                                resultados.append(resultado)
                                if callback_resultado:
                                    callback_resultado(resultado)
                                self.logger.aviso(f"📂 Obsoleto: {item} ({tamanho:.1f} MB)")
                                
                    # Se for pasta, continua escavando
                    if os.path.isdir(item_path):
                        self._escavar_obsoletos(item_path, data_limite, resultados,
                                               callback_progresso, callback_resultado, 
                                               profundidade + 1)
                                               
                except (PermissionError, OSError):
                    # Ignora silenciosamente erros de arquivos individuais
                    continue
                    
            if callback_progresso:
                callback_progresso(caminho)
                self.total_verificados += 1
                
        except (PermissionError, OSError) as e:
            if "267" not in str(e):  # Ignora erro 267 (pasta bloqueada)
                self.logger.debug(f"⚠️ Erro ao escavar {caminho}: {str(e)[:50]}")

    def _encontrar_duplicados(self, callback_progresso: Optional[Callable] = None,
                             callback_resultado: Optional[Callable] = None) -> List[Dict]:
        """Encontra arquivos duplicados (limite aumentado)"""
        resultados = []
        hash_map = {}
        self.logger.info("📎 BUSCANDO ARQUIVOS DUPLICADOS...")
        
        pastas_para_varer = [p for p in self.pastas_sistema if p and os.path.exists(p)]
        arquivos_verificados = 0
        limite_arquivos = 50000  # AUMENTADO de 1000 para 50000
        
        for pasta in pastas_para_varer:
            if self.parar_varredura:
                return resultados
            try:
                arquivos_verificados = self._escavar_duplicados(
                    pasta, hash_map, callback_progresso, 
                    arquivos_verificados, limite_arquivos
                )
                if arquivos_verificados >= limite_arquivos:
                    self.logger.aviso(f"⏸️ Limite de {limite_arquivos} arquivos atingido")
                    break
            except (PermissionError, OSError) as e:
                self.logger.aviso(f"⚠️ Não foi possível verificar {pasta}: {str(e)[:50]}")
                continue
                
        # Processa resultados
        for file_hash, arquivos in hash_map.items():
            if len(arquivos) > 1:
                tamanho_total = sum(self._calcular_tamanho_arquivo(a) for a in arquivos)
                if tamanho_total > 1:
                    resultado = {
                        'hash': file_hash,
                        'arquivos': arquivos,
                        'tamanho_total_mb': tamanho_total,
                        'tipo': 'duplicado',
                        'caminho': arquivos[0],
                        'is_pasta': False  # É arquivo, não pasta
                    }
                    resultados.append(resultado)
                    if callback_resultado:
                        callback_resultado(resultado)
                    self.logger.aviso(f"📎 Duplicado: {os.path.basename(arquivos[0])} ({tamanho_total:.1f} MB, {len(arquivos)} cópias)")
                    
        self.logger.info(f"✅ Duplicados encontrados: {len(resultados)}")
        return resultados

    def _escavar_duplicados(self, caminho: str, hash_map: Dict, 
                           callback_progresso: Optional[Callable],
                           contador: int, limite: int) -> int:
        """Escava recursivamente em busca de duplicados"""
        if self.parar_varredura or contador >= limite:
            return contador
            
        if self._deve_ignorar(caminho):
            return contador
            
        # Verifica permissão
        tem_perm, _ = self._verificar_permissao(caminho)
        if not tem_perm:
            return contador
            
        try:
            for item in os.listdir(caminho):
                if self.parar_varredura or contador >= limite:
                    return contador
                    
                item_path = os.path.join(caminho, item)
                
                if self._deve_ignorar(item_path):
                    continue
                
                if os.path.isfile(item_path):
                    # Ignora extensões desnecessárias
                    ext = os.path.splitext(item_path)[1].lower()
                    if ext in self.extensoes_ignoradas:
                        continue
                        
                    try:
                        tamanho = os.path.getsize(item_path) / (1024 * 1024)
                        if tamanho > 1:  # > 1 MB
                            file_hash = self._calcular_hash(item_path)
                            if file_hash:
                                if file_hash not in hash_map:
                                    hash_map[file_hash] = []
                                hash_map[file_hash].append(item_path)
                                contador += 1
                                
                                if contador % 100 == 0:
                                    self.logger.debug(f"🔍 Verificados: {contador} arquivos")
                    except (PermissionError, OSError):
                        continue
                        
                elif os.path.isdir(item_path):
                    contador = self._escavar_duplicados(
                        item_path, hash_map, callback_progresso, contador, limite
                    )
                    
            if callback_progresso:
                callback_progresso(caminho)
                self.total_verificados += 1
                
        except (PermissionError, OSError):
            pass
            
        return contador

    def _calcular_hash(self, caminho: str) -> Optional[str]:
        """Calcula hash MD5 de um arquivo (com chunks para arquivos grandes)"""
        try:
            hash_md5 = hashlib.md5()
            with open(caminho, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):  # AUMENTADO para 8KB
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (PermissionError, OSError):
            return None

    def _calcular_tamanho_arquivo(self, caminho: str) -> float:
        """Calcula tamanho de um arquivo"""
        try:
            return os.path.getsize(caminho) / (1024 * 1024)
        except (PermissionError, OSError):
            return 0

    def _obter_ultimo_acesso(self, caminho: str) -> Optional[datetime]:
        """Obtém data do último acesso"""
        try:
            return datetime.fromtimestamp(os.stat(caminho).st_atime)
        except (PermissionError, OSError):
            return None

    def escanear_tudo(self, callback_progresso: Optional[Callable] = None,
                     callback_resultado: Optional[Callable] = None) -> Dict[str, List]:
        """
        Executa varredura completa (3 camadas)
        """
        self.logger.limpar()
        self.resultados = {'resquicios': [], 'obsoletos': [], 'duplicados': []}
        self.parar_varredura = False
        self.total_verificados = 0
        
        self.logger.info("🚀 INICIANDO PROTOCOLO MISA-CLEANER...")
        self.logger.info("⚡ 3 CAMADAS DE ANÁLISE ATIVADAS:")
        self.logger.info("   1. 🔴 RESQUÍCIOS DE PROGRAMAS DELETADOS")
        self.logger.info("   2. 📂 ARQUIVOS OBSOLETOS (> 1 ano sem acesso)")
        self.logger.info("   3. 📎 ARQUIVOS DUPLICADOS (> 1 MB)")
        
        try:
            # Camada 1: Resquícios
            self.logger.info("")
            self.logger.info("═" * 50)
            self.resultados['resquicios'] = self._encontrar_resquicios_programas(
                callback_progresso, callback_resultado
            )
            
            if self.parar_varredura:
                self.logger.aviso("⏹️ VARREDURA INTERROMPIDA PELO USUÁRIO")
                return self.resultados
                
            # Camada 2: Obsoletos
            self.logger.info("")
            self.logger.info("═" * 50)
            self.resultados['obsoletos'] = self._encontrar_obsoletos(
                callback_progresso, callback_resultado
            )
            
            if self.parar_varredura:
                self.logger.aviso("⏹️ VARREDURA INTERROMPIDA PELO USUÁRIO")
                return self.resultados
                
            # Camada 3: Duplicados
            self.logger.info("")
            self.logger.info("═" * 50)
            self.resultados['duplicados'] = self._encontrar_duplicados(
                callback_progresso, callback_resultado
            )
            
            # Estatísticas finais
            total = sum(len(v) for v in self.resultados.values())
            self.logger.info("")
            self.logger.info("═" * 50)
            self.logger.sucesso(f"🎯 VARREDURA CONCLUÍDA! {total} RESQUÍCIOS ENCONTRADOS")
            self.logger.info(f"   📊 Verificados: {self.total_verificados} itens")
            self.logger.info(f"   🔴 Resquícios: {len(self.resultados['resquicios'])}")
            self.logger.info(f"   📂 Obsoletos: {len(self.resultados['obsoletos'])}")
            self.logger.info(f"   📎 Duplicados: {len(self.resultados['duplicados'])}")
            
            # Atualiza logger
            self.logger.total_encontrados = total
            self.logger.total_verificados = self.total_verificados
                
        except Exception as e:
            self.logger.critico(f"💥 ERRO CRÍTICO NA VARREDURA: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            
        return self.resultados

    def parar(self) -> None:
        """Para a varredura em andamento"""
        self.parar_varredura = True
        self.logger.aviso("⏹️ PARANDO VARREDURA...")

    def deletar_pasta(self, caminho: str) -> Tuple[bool, str]:
        """Deleta uma pasta com fallback e tratamento de erros"""
        try:
            shutil.rmtree(caminho)
            self.logger.sucesso(f"🗑️ EXCLUÍDO: {caminho}")
            return True, f"EXCLUÍDO: {caminho}"
        except PermissionError:
            # Tenta remover atributos somente leitura e tentar novamente
            try:
                for root, dirs, files in os.walk(caminho):
                    for f in files:
                        try:
                            os.chmod(os.path.join(root, f), 0o777)
                        except:
                            pass
                    for d in dirs:
                        try:
                            os.chmod(os.path.join(root, d), 0o777)
                        except:
                            pass
                shutil.rmtree(caminho)
                self.logger.sucesso(f"🗑️ EXCLUÍDO (FORÇADO): {caminho}")
                return True, f"EXCLUÍDO (FORÇADO): {caminho}"
            except Exception as e:
                msg = f"🔴 NÃO FOI POSSÍVEL EXCLUIR: {caminho}\n   Motivo: {str(e)}\n   💡 Tente fechar programas que estejam usando esta pasta"
                self.logger.erro(msg)
                return False, msg
        except Exception as e:
            msg = f"🔴 ERRO AO EXCLUIR: {caminho}\n   Motivo: {str(e)}"
            self.logger.erro(msg)
            return False, msg

    def deletar_arquivo(self, caminho: str) -> Tuple[bool, str]:
        """Deleta um arquivo com tratamento de erros"""
        try:
            os.remove(caminho)
            self.logger.sucesso(f"🗑️ EXCLUÍDO: {caminho}")
            return True, f"EXCLUÍDO: {caminho}"
        except PermissionError:
            # Tenta remover atributo somente leitura
            try:
                os.chmod(caminho, 0o777)
                os.remove(caminho)
                self.logger.sucesso(f"🗑️ EXCLUÍDO (FORÇADO): {caminho}")
                return True, f"EXCLUÍDO (FORÇADO): {caminho}"
            except Exception as e:
                msg = f"🔴 NÃO FOI POSSÍVEL EXCLUIR: {caminho}\n   Motivo: {str(e)}\n   💡 O arquivo pode estar em uso"
                self.logger.erro(msg)
                return False, msg
        except Exception as e:
            msg = f"🔴 ERRO AO EXCLUIR: {caminho}\n   Motivo: {str(e)}"
            self.logger.erro(msg)
            return False, msg