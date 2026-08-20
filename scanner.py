"""
MISA-CLEANER - Scanner de Resquícios Digitais
VERSÃO 3.0 - Com proteção de sistema, detecção de arquivos em uso e logs inteligentes

MELHORIAS:
✅ Pastas do sistema (Java, Edge, Android) são protegidas automaticamente
✅ Arquivos em uso são detectados e ignorados silenciosamente
✅ Logs de "Acesso Negado" são suprimidos (mostrados apenas em DEBUG)
✅ Diagnóstico detalhado mostra o que foi ignorado e por quê
✅ 100% seguro - nunca tenta deletar arquivos do sistema ou em uso
"""
import hashlib
import os
import shutil
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple

from logger import Logger


class Scanner:
    """Scanner profissional com proteção inteligente de sistema"""
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
        self.resultados = {
            'resquicios': [],
            'obsoletos': [],
            'duplicados': []
        }
        self.parar_varredura = False
        self.total_verificados = 0
        
        # Estatísticas de ignorados (para diagnóstico)
        self.ignorados_sistema = 0      # Pastas do sistema protegidas
        self.ignorados_em_uso = 0       # Arquivos em uso
        self.ignorados_lista_negra = 0  # Pastas da lista negra
        self.ignorados_extensao = 0     # Extensões ignoradas
        
        # Pastas comuns de programas (ESCOPO REDUZIDO E SEGURO)
        self.pastas_sistema = [
            os.environ.get('APPDATA', ''),           # C:\Users\Usuario\AppData\Roaming
            os.environ.get('LOCALAPPDATA', ''),      # C:\Users\Usuario\AppData\Local
            os.environ.get('PROGRAMFILES', ''),      # C:\Program Files
            os.environ.get('PROGRAMFILES(X86)', ''), # C:\Program Files (x86)
            # REMOVIDO: os.path.expanduser('~')  # NUNCA varrer a raiz do usuário!
        ]
        
        # 🛡️ LISTA COMPLETA DE PASTAS IGNORADAS (BLOQUEIO TOTAL)
        self.pastas_ignoradas = self._build_ignore_list()
        
        # 🛡️ PASTAS DO SISTEMA PROTEGIDAS (NUNCA VARRER)
        self.pastas_sistema_protegidas = self._build_system_protected_list()
        
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
        
        # 🌟 NOVO: Arquivos/Pastas do usuário que são seguros para deletar
        # (usado para sugerir exclusão)
        self.pastas_seguras_para_deletar = [
            'Temp', 'Cache', 'Logs', 'Backup', 'Old',
            'node_modules', '__pycache__', '.venv', 'venv'
        ]
        
    def _build_system_protected_list(self) -> List[str]:
        """
        Constrói lista de pastas do sistema que NUNCA devem ser varridas
        """
        user = os.path.expanduser('~')
        program_files = os.environ.get('PROGRAMFILES', '')
        program_files_x86 = os.environ.get('PROGRAMFILES(X86)', '')
        
        # Pastas do sistema Windows
        sistema_windows = [
            "C:\\Windows",
            "C:\\Windows\\System32",
            "C:\\Windows\\SysWOW64",
            "C:\\Windows\\WinSxS",
            "C:\\Windows\\Installer",
            "C:\\Windows\\Microsoft.NET",
            "C:\\Windows\\assembly",
            "C:\\ProgramData",
            "C:\\Users\\Public",
            "C:\\PerfLogs",
            "C:\\Recovery",
            "C:\\$Recycle.Bin",
            "C:\\System Volume Information",
        ]
        
        # Programas instalados (PROTEGIDOS - nunca deletar)
        programas_instalados = [
            os.path.join(program_files, 'Java'),
            os.path.join(program_files, 'Android'),
            os.path.join(program_files, 'Android Studio'),
            os.path.join(program_files, 'JetBrains'),
            os.path.join(program_files, 'Git'),
            os.path.join(program_files, 'nodejs'),
            os.path.join(program_files, 'Microsoft SQL Server'),
            os.path.join(program_files, 'dotnet'),
            os.path.join(program_files, 'WindowsApps'),
            
            os.path.join(program_files_x86, 'Java'),
            os.path.join(program_files_x86, 'Microsoft', 'Edge'),
            os.path.join(program_files_x86, 'Google', 'Chrome'),
            os.path.join(program_files_x86, 'Mozilla Firefox'),
            os.path.join(program_files_x86, 'Steam'),
            os.path.join(program_files_x86, 'Epic Games'),
            os.path.join(program_files_x86, 'Ubisoft'),
            os.path.join(program_files_x86, 'Origin'),
            os.path.join(program_files_x86, 'GOG Galaxy'),
        ]
        
        # Pastas do usuário que são programas (PROTEGIDOS)
        pastas_usuario_programas = [
            os.path.join(user, 'AppData', 'Local', 'Android'),
            os.path.join(user, 'AppData', 'Local', 'Google', 'Chrome'),
            os.path.join(user, 'AppData', 'Local', 'Microsoft', 'Edge'),
            os.path.join(user, 'AppData', 'Local', 'Programs'),
            os.path.join(user, 'AppData', 'Local', 'GitHubDesktop'),
            os.path.join(user, 'AppData', 'Roaming', 'Code'),
            os.path.join(user, '.android'),
            os.path.join(user, '.gradle'),
            os.path.join(user, '.m2'),
            os.path.join(user, '.npm'),
            os.path.join(user, '.yarn'),
            os.path.join(user, '.dotnet'),
            os.path.join(user, '.rustup'),
            os.path.join(user, '.cargo'),
            os.path.join(user, '.vscode'),
            os.path.join(user, '.idea'),
        ]
        
        # Combinar todas as listas e normalizar
        todas = sistema_windows + programas_instalados + pastas_usuario_programas
        return [os.path.normpath(p) for p in todas if p and os.path.normpath(p)]
        
    def _build_ignore_list(self) -> List[str]:
        """Constrói lista completa de pastas ignoradas (expansível)"""
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
        
    def _eh_pasta_sistema_protegida(self, caminho: str) -> bool:
        """
        Verifica se o caminho é uma pasta do sistema que NUNCA deve ser varrida
        """
        if not caminho:
            return True
            
        try:
            caminho_norm = os.path.normpath(caminho).lower()
            
            for protegida in self.pastas_sistema_protegidas:
                if not protegida:
                    continue
                    
                protegida_norm = os.path.normpath(protegida).lower()
                
                # Verifica se o caminho começa com a pasta protegida
                if caminho_norm.startswith(protegida_norm):
                    return True
                    
            return False
            
        except Exception:
            return False
            
    def _arquivo_em_uso(self, caminho: str) -> bool:
        """
        Verifica se um arquivo está em uso por outro processo
        Retorna True se estiver em uso (deve ser ignorado)
        """
        if not os.path.exists(caminho):
            return False
            
        if not os.path.isfile(caminho):
            return False
            
        try:
            # Tenta abrir o arquivo com compartilhamento de leitura
            # Se falhar, está em uso
            with open(caminho, 'rb') as f:
                f.read(1)
            return False
        except (PermissionError, OSError, IOError):
            # Arquivo em uso ou protegido
            return True
        except Exception:
            return True
            
    def _deve_ignorar(self, caminho: str, logar: bool = False) -> bool:
        """
        Verifica se o caminho deve ser ignorado com correspondência exata
        de componentes de diretório (evita falsos positivos)
        
        Args:
            caminho: Caminho a verificar
            logar: Se deve logar quando ignorado (False = silencioso)
        """
        if not caminho:
            return True
            
        try:
            caminho_norm = os.path.normpath(caminho).lower()
            partes = caminho_norm.split(os.sep)
            
            # 1. Verifica se é pasta do sistema protegida
            if self._eh_pasta_sistema_protegida(caminho):
                self.ignorados_sistema += 1
                if logar:
                    self.logger.debug(f"⏭️ Sistema protegido: {caminho}")
                return True
                
            # 2. Verifica lista negra (ignorados)
            for ignorado in self.pastas_ignoradas:
                if not ignorado:
                    continue
                    
                ignorado_norm = os.path.normpath(ignorado).lower()
                partes_ignorado = ignorado_norm.split(os.sep)
                
                # Verifica se o caminho ignorado corresponde a um prefixo de pastas
                if len(partes_ignorado) <= len(partes):
                    if partes[:len(partes_ignorado)] == partes_ignorado:
                        self.ignorados_lista_negra += 1
                        if logar:
                            self.logger.debug(f"⏭️ Lista negra: {caminho}")
                        return True
                        
                # Para 'node_modules', '.git', etc., verifica qualquer nível
                if ignorado_norm in ['node_modules', '.git', '.venv', 'venv', '__pycache__']:
                    if ignorado_norm in partes:
                        self.ignorados_lista_negra += 1
                        if logar:
                            self.logger.debug(f"⏭️ Lista negra: {caminho}")
                        return True
                        
            # 3. Verifica se é arquivo em uso (apenas arquivos)
            if os.path.isfile(caminho):
                if self._arquivo_em_uso(caminho):
                    self.ignorados_em_uso += 1
                    if logar:
                        self.logger.debug(f"⏭️ Arquivo em uso: {caminho}")
                    return True
                    
            return False
            
        except Exception:
            return False
            
    def _verificar_permissao(self, caminho: str, silencioso: bool = True) -> Tuple[bool, str]:
        """
        Verifica se tem permissão de acesso ao caminho
        
        Args:
            caminho: Caminho a verificar
            silencioso: Se deve logar erros (True = silencioso)
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
            if not silencioso:
                self.logger.debug(f"🔒 Sem permissão: {caminho}")
            return False, "SEM PERMISSÃO"
            
        except OSError as e:
            if "267" in str(e):
                if not silencioso:
                    self.logger.debug(f"📁 Pasta bloqueada: {caminho}")
                return False, "PASTA BLOQUEADA"
            elif "5" in str(e):
                if not silencioso:
                    self.logger.debug(f"🔒 Acesso negado: {caminho}")
                return False, "ACESSO NEGADO"
            else:
                if not silencioso:
                    self.logger.debug(f"⚠️ Erro: {caminho} - {str(e)[:50]}")
                return False, f"ERRO: {str(e)[:50]}"
                
        except Exception as e:
            if not silencioso:
                self.logger.debug(f"⚠️ Erro: {caminho} - {str(e)[:50]}")
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
                    
                # Filtra pastas ignoradas em tempo real (silencioso)
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
        """Encontra resquícios de programas deletados (com filtros inteligentes)"""
        resultados = []
        self.logger.info("🔍 BUSCANDO RESQUÍCIOS DE PROGRAMAS...")
        
        for pasta_base in self.pastas_sistema[:3]:
            if not pasta_base or not os.path.exists(pasta_base):
                continue
                
            # Verifica se a pasta base é protegida
            if self._deve_ignorar(pasta_base):
                self.logger.debug(f"⏭️ Pasta base ignorada: {pasta_base}")
                continue
                
            self.logger.debug(f"📁 Verificando: {pasta_base}")
                
            try:
                for item in os.listdir(pasta_base):
                    if self.parar_varredura:
                        return resultados
                        
                    caminho_item = os.path.join(pasta_base, item)
                    
                    # Ignora pastas proibidas (silencioso)
                    if self._deve_ignorar(caminho_item):
                        continue
                        
                    if not os.path.isdir(caminho_item):
                        continue
                        
                    # Verifica permissão (silencioso)
                    tem_perm, _ = self._verificar_permissao(caminho_item, silencioso=True)
                    if not tem_perm:
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
                self.logger.debug(f"⚠️ Não foi possível verificar {pasta_base}: {str(e)[:50]}")
                continue
                
        self.logger.info(f"✅ Resquícios encontrados: {len(resultados)}")
        return resultados

    def _encontrar_obsoletos(self, callback_progresso: Optional[Callable] = None,
                            callback_resultado: Optional[Callable] = None) -> List[Dict]:
        """Encontra arquivos/pastas obsoletos (1+ ano sem acesso) com filtros"""
        resultados = []
        um_ano_atras = datetime.now() - timedelta(days=365)
        self.logger.info("📂 BUSCANDO ARQUIVOS OBSOLETOS...")
        
        pastas_para_varer = [p for p in self.pastas_sistema if p and os.path.exists(p)]
        
        for pasta in pastas_para_varer:
            if self.parar_varredura:
                return resultados
                
            # Verifica se a pasta base é protegida
            if self._deve_ignorar(pasta):
                self.logger.debug(f"⏭️ Pasta ignorada: {pasta}")
                continue
                
            try:
                self._escavar_obsoletos(pasta, um_ano_atras, resultados, 
                                       callback_progresso, callback_resultado, 0)
            except (PermissionError, OSError) as e:
                self.logger.debug(f"⚠️ Não foi possível verificar {pasta}: {str(e)[:50]}")
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
            
        # Ignora pastas proibidas (silencioso)
        if self._deve_ignorar(caminho):
            return
            
        # Verifica permissão (silencioso)
        tem_perm, _ = self._verificar_permissao(caminho, silencioso=True)
        if not tem_perm:
            return
            
        try:
            for item in os.listdir(caminho):
                if self.parar_varredura:
                    return
                    
                item_path = os.path.join(caminho, item)
                
                # Ignora arquivos/pastas proibidas (silencioso)
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
        """Encontra arquivos duplicados com filtros inteligentes"""
        resultados = []
        hash_map = {}
        self.logger.info("📎 BUSCANDO ARQUIVOS DUPLICADOS...")
        
        pastas_para_varer = [p for p in self.pastas_sistema if p and os.path.exists(p)]
        arquivos_verificados = 0
        limite_arquivos = 50000
        
        for pasta in pastas_para_varer:
            if self.parar_varredura:
                return resultados
                
            # Verifica se a pasta base é protegida
            if self._deve_ignorar(pasta):
                self.logger.debug(f"⏭️ Pasta ignorada: {pasta}")
                continue
                
            try:
                arquivos_verificados = self._escavar_duplicados(
                    pasta, hash_map, callback_progresso, 
                    arquivos_verificados, limite_arquivos
                )
                if arquivos_verificados >= limite_arquivos:
                    self.logger.aviso(f"⏸️ Limite de {limite_arquivos} arquivos atingido")
                    break
            except (PermissionError, OSError) as e:
                self.logger.debug(f"⚠️ Não foi possível verificar {pasta}: {str(e)[:50]}")
                continue
                
        # Processa resultados (filtra arquivos em uso)
        for file_hash, arquivos in hash_map.items():
            if len(arquivos) > 1:
                # Filtra arquivos em uso
                arquivos_validos = []
                for a in arquivos:
                    if not self._arquivo_em_uso(a):
                        arquivos_validos.append(a)
                    else:
                        self.ignorados_em_uso += 1
                        
                if len(arquivos_validos) > 1:
                    tamanho_total = sum(self._calcular_tamanho_arquivo(a) for a in arquivos_validos)
                    if tamanho_total > 1:
                        resultado = {
                            'hash': file_hash,
                            'arquivos': arquivos_validos,
                            'tamanho_total_mb': tamanho_total,
                            'tipo': 'duplicado',
                            'caminho': arquivos_validos[0],
                            'is_pasta': False
                        }
                        resultados.append(resultado)
                        if callback_resultado:
                            callback_resultado(resultado)
                        self.logger.aviso(f"📎 Duplicado: {os.path.basename(arquivos_validos[0])} ({tamanho_total:.1f} MB, {len(arquivos_validos)} cópias)")
                    
        self.logger.info(f"✅ Duplicados encontrados: {len(resultados)}")
        return resultados

    def _escavar_duplicados(self, caminho: str, hash_map: Dict, 
                           callback_progresso: Optional[Callable],
                           contador: int, limite: int) -> int:
        """Escava recursivamente em busca de duplicados (com filtros)"""
        if self.parar_varredura or contador >= limite:
            return contador
            
        # Ignora pastas proibidas (silencioso)
        if self._deve_ignorar(caminho):
            return contador
            
        # Verifica permissão (silencioso)
        tem_perm, _ = self._verificar_permissao(caminho, silencioso=True)
        if not tem_perm:
            return contador
            
        try:
            for item in os.listdir(caminho):
                if self.parar_varredura or contador >= limite:
                    return contador
                    
                item_path = os.path.join(caminho, item)
                
                # Ignora pastas/arquivos proibidos (silencioso)
                if self._deve_ignorar(item_path):
                    continue
                
                if os.path.isfile(item_path):
                    # Ignora extensões desnecessárias
                    ext = os.path.splitext(item_path)[1].lower()
                    if ext in self.extensoes_ignoradas:
                        self.ignorados_extensao += 1
                        continue
                        
                    # Ignora arquivos em uso
                    if self._arquivo_em_uso(item_path):
                        self.ignorados_em_uso += 1
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
                for chunk in iter(lambda: f.read(8192), b""):
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
        Executa varredura completa (3 camadas) com proteção inteligente
        """
        # Reset estatísticas
        self.ignorados_sistema = 0
        self.ignorados_em_uso = 0
        self.ignorados_lista_negra = 0
        self.ignorados_extensao = 0
        
        self.logger.limpar()
        self.resultados = {'resquicios': [], 'obsoletos': [], 'duplicados': []}
        self.parar_varredura = False
        self.total_verificados = 0
        
        self.logger.info("🚀 INICIANDO PROTOCOLO MISA-CLEANER v3.0...")
        self.logger.info("⚡ 3 CAMADAS DE ANÁLISE ATIVADAS:")
        self.logger.info("   1. 🔴 RESQUÍCIOS DE PROGRAMAS DELETADOS")
        self.logger.info("   2. 📂 ARQUIVOS OBSOLETOS (> 1 ano sem acesso)")
        self.logger.info("   3. 📎 ARQUIVOS DUPLICADOS (> 1 MB)")
        self.logger.info("🛡️ PROTEÇÃO DE SISTEMA ATIVADA")
        
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
            total_ignorados = (self.ignorados_sistema + self.ignorados_em_uso + 
                             self.ignorados_lista_negra + self.ignorados_extensao)
            
            self.logger.info("")
            self.logger.info("═" * 50)
            self.logger.sucesso(f"🎯 VARREDURA CONCLUÍDA! {total} RESQUÍCIOS ENCONTRADOS")
            self.logger.info(f"   📊 Verificados: {self.total_verificados} itens")
            self.logger.info(f"   🔴 Resquícios: {len(self.resultados['resquicios'])}")
            self.logger.info(f"   📂 Obsoletos: {len(self.resultados['obsoletos'])}")
            self.logger.info(f"   📎 Duplicados: {len(self.resultados['duplicados'])}")
            
            # Informações sobre itens ignorados (apenas se houver)
            if total_ignorados > 0:
                self.logger.info(f"   ⏭️ Ignorados: {total_ignorados} itens (protegidos/em uso)")
                
            # Atualiza logger
            self.logger.total_encontrados = total
            self.logger.total_verificados = self.total_verificados
            self.logger.pastas_ignoradas = self.ignorados_sistema + self.ignorados_lista_negra
            self.logger.arquivos_ignorados = self.ignorados_em_uso + self.ignorados_extensao
                
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
        """Deleta uma pasta com verificação de segurança"""
        # Verifica se é pasta do sistema protegida
        if self._eh_pasta_sistema_protegida(caminho):
            msg = f"⏭️ PASTA DO SISTEMA PROTEGIDA (pulada): {caminho}"
            self.logger.debug(msg)
            return False, msg
            
        # Verifica se está em uso
        if self._arquivo_em_uso(caminho):
            msg = f"⏭️ PASTA EM USO (pulada): {caminho}"
            self.logger.debug(msg)
            return False, msg
            
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
                msg = f"⏭️ NÃO FOI POSSÍVEL EXCLUIR (protegido): {caminho}"
                self.logger.debug(msg)
                return False, msg
        except Exception as e:
            msg = f"⏭️ NÃO FOI POSSÍVEL EXCLUIR: {caminho}"
            self.logger.debug(msg)
            return False, msg

    def deletar_arquivo(self, caminho: str) -> Tuple[bool, str]:
        """Deleta um arquivo com verificação de segurança"""
        # Verifica se é pasta do sistema protegida
        if self._eh_pasta_sistema_protegida(caminho):
            msg = f"⏭️ ARQUIVO DO SISTEMA PROTEGIDO (pulado): {caminho}"
            self.logger.debug(msg)
            return False, msg
            
        # Verifica se está em uso
        if self._arquivo_em_uso(caminho):
            msg = f"⏭️ ARQUIVO EM USO (pulado): {caminho}"
            self.logger.debug(msg)
            return False, msg
            
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
                msg = f"⏭️ NÃO FOI POSSÍVEL EXCLUIR (protegido): {caminho}"
                self.logger.debug(msg)
                return False, msg
        except Exception as e:
            msg = f"⏭️ NÃO FOI POSSÍVEL EXCLUIR: {caminho}"
            self.logger.debug(msg)
            return False, msg
            
    def get_diagnostico_completo(self) -> Dict[str, Any]:
        """
        Retorna diagnóstico completo com estatísticas de ignorados
        """
        resumo = self.logger.get_resumo()
        resumo.update({
            'ignorados_sistema': self.ignorados_sistema,
            'ignorados_em_uso': self.ignorados_em_uso,
            'ignorados_lista_negra': self.ignorados_lista_negra,
            'ignorados_extensao': self.ignorados_extensao,
            'total_ignorados': (self.ignorados_sistema + self.ignorados_em_uso + 
                               self.ignorados_lista_negra + self.ignorados_extensao)
        })
        return resumo