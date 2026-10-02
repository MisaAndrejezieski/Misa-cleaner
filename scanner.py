"""
MISA-CLEANER - Scanner de Resquícios Digitais
VERSÃO 4.0 - Contadores corrigidos, proteção reforçada, deleção segura

MUDANÇAS:
- _deve_ignorar não infla mais os contadores (contadores só incrementam na varredura principal)
- Adicionadas pastas do sistema: Comms, Packages\LocalCache, TempState
- Removido chmod 0o777 (deleção forçada)
- Duplicados não varrem mais Program Files inteiro
- Sincronização com logger via atualizar_estatisticas_scanner
- Verificação de programa via registro do Windows (winreg)
"""
import hashlib
import os
import shutil
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple

from logger import Logger


class Scanner:
    """Scanner com proteção inteligente de sistema"""

    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
        self.resultados = {
            'resquicios': [],
            'obsoletos': [],
            'duplicados': []
        }
        self.parar_varredura = False
        self.total_verificados = 0

        # Estatísticas de ignorados (incrementadas APENAS na varredura principal)
        self.ignorados_sistema = 0
        self.ignorados_em_uso = 0
        self.ignorados_lista_negra = 0
        self.ignorados_extensao = 0

        # Escopo de varredura
        self.pastas_sistema = [
            os.environ.get('APPDATA', ''),
            os.environ.get('LOCALAPPDATA', ''),
            os.environ.get('PROGRAMFILES', ''),
            os.environ.get('PROGRAMFILES(X86)', ''),
        ]

        # Apenas pastas de usuário para duplicados (evita Program Files)
        self.pastas_duplicados = [
            os.environ.get('APPDATA', ''),
            os.environ.get('LOCALAPPDATA', ''),
        ]

        self.pastas_ignoradas = self._build_ignore_list()
        self.pastas_sistema_protegidas = self._build_system_protected_list()

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

        self.extensoes_ignoradas = {
            '.exe', '.msi', '.dll', '.so', '.dylib', '.sys',
            '.pyc', '.pyo', '.pyd', '.class', '.o', '.obj',
            '.cache', '.log', '.tmp', '.temp', '.swp', '.bak',
            '.ico', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp',
            '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.wav', '.flac',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'
        }

    def _build_system_protected_list(self) -> List[str]:
        """Pastas do sistema que NUNCA devem ser varridas"""
        user = os.path.expanduser('~')
        program_files = os.environ.get('PROGRAMFILES', '')
        program_files_x86 = os.environ.get('PROGRAMFILES(X86)', '')
        localappdata = os.environ.get('LOCALAPPDATA', '')
        appdata = os.environ.get('APPDATA', '')

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

        # NOVO: pastas voláteis do Windows que se regeneram
        pastas_volateis = [
            os.path.join(localappdata, 'Comms'),
            os.path.join(localappdata, 'Packages'),
            os.path.join(localappdata, 'ConnectedDevicesPlatform'),
            os.path.join(localappdata, 'D3DSCache'),
            os.path.join(localappdata, 'FontCache'),
            os.path.join(localappdata, 'IconCache'),
            os.path.join(localappdata, 'Microsoft', 'Windows', 'INetCache'),
            os.path.join(localappdata, 'Microsoft', 'Windows', 'INetCookies'),
            os.path.join(localappdata, 'Microsoft', 'Windows', 'WebCache'),
            os.path.join(localappdata, 'Microsoft', 'Windows', 'Explorer'),
            os.path.join(localappdata, 'Microsoft', 'Windows', 'Caches'),
            os.path.join(localappdata, 'Temp'),
            os.path.join(appdata, 'Microsoft', 'Windows', 'Recent'),
            os.path.join(appdata, 'Microsoft', 'Windows', 'Start Menu'),
        ]

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

        todas = sistema_windows + programas_instalados + pastas_volateis + pastas_usuario_programas
        return [os.path.normpath(p) for p in todas if p]

    def _build_ignore_list(self) -> List[str]:
        """Lista de pastas ignoradas"""
        user = os.path.expanduser('~')
        localappdata = os.environ.get('LOCALAPPDATA', '')
        appdata = os.environ.get('APPDATA', '')
        temp = os.environ.get('TEMP', '')
        tmp = os.environ.get('TMP', '')

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

        # NOVO: pastas voláteis
        volateis = [
            os.path.join(localappdata, 'Comms'),
            os.path.join(localappdata, 'Packages'),
            os.path.join(localappdata, 'ConnectedDevicesPlatform'),
            os.path.join(localappdata, 'D3DSCache'),
            os.path.join(localappdata, 'FontCache'),
            os.path.join(localappdata, 'IconCache'),
            os.path.join(localappdata, 'Microsoft', 'Windows', 'INetCache'),
            os.path.join(localappdata, 'Microsoft', 'Windows', 'INetCookies'),
            os.path.join(localappdata, 'Microsoft', 'Windows', 'WebCache'),
        ]

        temp_pastas = [
            temp, tmp,
            os.path.join(user, 'AppData', 'Local', 'Temp'),
            os.path.join(user, 'AppData', 'Local', 'Temp2'),
            os.path.join(user, 'AppData', 'Local', 'Cache'),
            "C:\\Windows\\Temp"
        ]

        todas = sistema + usuario + navegadores + dev + volateis + temp_pastas
        return [os.path.normpath(p) for p in todas if p]

    def _eh_pasta_sistema_protegida(self, caminho: str) -> bool:
        if not caminho:
            return True
        try:
            caminho_norm = os.path.normpath(caminho).lower()
            for protegida in self.pastas_sistema_protegidas:
                if not protegida:
                    continue
                protegida_norm = os.path.normpath(protegida).lower()
                if caminho_norm == protegida_norm:
                    return True
                if caminho_norm.startswith(protegida_norm + os.sep):
                    return True
            return False
        except Exception:
            return False

    def _arquivo_em_uso(self, caminho: str) -> bool:
        if not os.path.exists(caminho) or not os.path.isfile(caminho):
            return False
        try:
            with open(caminho, 'rb') as f:
                f.read(1)
            return False
        except (PermissionError, OSError, IOError):
            return True
        except Exception:
            return True

    def _deve_ignorar(self, caminho: str) -> bool:
        """
        Verifica se o caminho deve ser ignorado.
        NÃO incrementa contadores. Contadores só são incrementados
        na varredura principal quando o item é de fato ignorado.
        """
        if not caminho:
            return True
        try:
            caminho_norm = os.path.normpath(caminho).lower()
            partes = caminho_norm.split(os.sep)

            if self._eh_pasta_sistema_protegida(caminho):
                return True

            for ignorado in self.pastas_ignoradas:
                if not ignorado:
                    continue
                ignorado_norm = os.path.normpath(ignorado).lower()
                partes_ignorado = ignorado_norm.split(os.sep)

                if len(partes_ignorado) <= len(partes):
                    if partes[:len(partes_ignorado)] == partes_ignorado:
                        return True

                if ignorado_norm in ['node_modules', '.git', '.venv', 'venv', '__pycache__']:
                    if ignorado_norm in partes:
                        return True

            if os.path.isfile(caminho):
                if self._arquivo_em_uso(caminho):
                    return True

            return False
        except Exception:
            return False

    def _registrar_ignorado(self, tipo: str) -> None:
        """Incrementa contadores de ignorados (chamado na varredura principal)"""
        if tipo == 'sistema':
            self.ignorados_sistema += 1
        elif tipo == 'em_uso':
            self.ignorados_em_uso += 1
        elif tipo == 'lista_negra':
            self.ignorados_lista_negra += 1
        elif tipo == 'extensao':
            self.ignorados_extensao += 1

    def _verificar_permissao(self, caminho: str) -> Tuple[bool, str]:
        try:
            if os.path.isdir(caminho):
                os.listdir(caminho)
            else:
                with open(caminho, 'rb') as f:
                    f.read(1)
            return True, ""
        except PermissionError:
            return False, "SEM PERMISSAO"
        except OSError as e:
            if "267" in str(e):
                return False, "PASTA BLOQUEADA"
            elif "5" in str(e):
                return False, "ACESSO NEGADO"
            return False, f"ERRO: {str(e)[:50]}"
        except Exception as e:
            return False, f"ERRO: {str(e)[:50]}"

    def _calcular_tamanho(self, caminho: str) -> float:
        if self._deve_ignorar(caminho):
            return 0
        total = 0
        try:
            if os.path.isfile(caminho):
                return os.path.getsize(caminho) / (1024 * 1024)
            for root, dirs, files in os.walk(caminho):
                if self.parar_varredura:
                    break
                if self._deve_ignorar(root):
                    continue
                for f in files:
                    try:
                        fp = os.path.join(root, f)
                        if not self._deve_ignorar(fp):
                            total += os.path.getsize(fp)
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass
        return total / (1024 * 1024)

    def _verificar_programa_existe(self, nome_programa: str) -> bool:
        """
        Verifica se um programa está instalado via registro do Windows.
        Fallback: verificação de pastas comuns.
        """
        # 1. Registro do Windows (mais confiável)
        try:
            import winreg
            chaves = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            ]
            nome_lower = nome_programa.lower()
            for hkey, subkey in chaves:
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        i = 0
                        while True:
                            try:
                                sub = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, sub) as subkey_obj:
                                    try:
                                        display_name, _ = winreg.QueryValueEx(subkey_obj, "DisplayName")
                                        if nome_lower in display_name.lower():
                                            return True
                                    except FileNotFoundError:
                                        pass
                                i += 1
                            except OSError:
                                break
                except OSError:
                    continue
        except ImportError:
            pass
        except Exception:
            pass

        # 2. Fallback: verificar pastas comuns
        for pasta in self.pastas_sistema[:3]:
            if not pasta:
                continue
            if os.path.exists(os.path.join(pasta, nome_programa)):
                return True

        return False

    def _encontrar_resquicios_programas(self, callback_progresso=None, callback_resultado=None) -> List[Dict]:
        resultados = []
        self.logger.info("BUSCANDO RESQUICIOS DE PROGRAMAS...")

        for pasta_base in self.pastas_sistema[:3]:
            if not pasta_base or not os.path.exists(pasta_base):
                continue
            if self._deve_ignorar(pasta_base):
                self._registrar_ignorado('sistema')
                continue

            self.logger.debug(f"Verificando: {pasta_base}")

            try:
                for item in os.listdir(pasta_base):
                    if self.parar_varredura:
                        return resultados
                    caminho_item = os.path.join(pasta_base, item)

                    if self._deve_ignorar(caminho_item):
                        self._registrar_ignorado('lista_negra')
                        continue
                    if not os.path.isdir(caminho_item):
                        continue

                    tem_perm, _ = self._verificar_permissao(caminho_item)
                    if not tem_perm:
                        continue

                    for programa in self.programas_conhecidos:
                        if programa.lower() in item.lower():
                            if not self._verificar_programa_existe(programa):
                                tamanho = self._calcular_tamanho(caminho_item)
                                if tamanho > 1:
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
                                    self.logger.sucesso(f"Resquicio: {programa} ({tamanho:.1f} MB)")
                            break

                    if callback_progresso:
                        callback_progresso(caminho_item)
                        self.total_verificados += 1

            except (PermissionError, OSError) as e:
                self.logger.debug(f"Nao foi possivel verificar {pasta_base}: {str(e)[:50]}")
                continue

        self.logger.info(f"Resquicios encontrados: {len(resultados)}")
        return resultados

    def _encontrar_obsoletos(self, callback_progresso=None, callback_resultado=None) -> List[Dict]:
        resultados = []
        um_ano_atras = datetime.now() - timedelta(days=365)
        self.logger.info("BUSCANDO ARQUIVOS OBSOLETOS...")

        pastas_para_varer = [p for p in self.pastas_sistema if p and os.path.exists(p)]

        for pasta in pastas_para_varer:
            if self.parar_varredura:
                return resultados
            if self._deve_ignorar(pasta):
                self._registrar_ignorado('sistema')
                continue
            try:
                self._escavar_obsoletos(pasta, um_ano_atras, resultados,
                                       callback_progresso, callback_resultado, 0)
            except (PermissionError, OSError) as e:
                self.logger.debug(f"Nao foi possivel verificar {pasta}: {str(e)[:50]}")
                continue

        self.logger.info(f"Obsoletos encontrados: {len(resultados)}")
        return resultados

    def _escavar_obsoletos(self, caminho: str, data_limite: datetime, resultados: List[Dict],
                          callback_progresso, callback_resultado, profundidade: int = 0):
        if self.parar_varredura:
            return
        if profundidade > 20:
            return
        if self._deve_ignorar(caminho):
            return

        tem_perm, _ = self._verificar_permissao(caminho)
        if not tem_perm:
            return

        try:
            for item in os.listdir(caminho):
                if self.parar_varredura:
                    return
                item_path = os.path.join(caminho, item)

                if self._deve_ignorar(item_path):
                    self._registrar_ignorado('lista_negra')
                    continue

                try:
                    ultimo_acesso = datetime.fromtimestamp(os.stat(item_path).st_atime)
                    if ultimo_acesso < data_limite:
                        if os.path.isdir(item_path):
                            tamanho = self._calcular_tamanho(item_path)
                            if tamanho > 1:
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
                                self.logger.aviso(f"Obsoleto: {item} ({tamanho:.1f} MB)")

                    if os.path.isdir(item_path):
                        self._escavar_obsoletos(item_path, data_limite, resultados,
                                               callback_progresso, callback_resultado,
                                               profundidade + 1)
                except (PermissionError, OSError):
                    continue

            if callback_progresso:
                callback_progresso(caminho)
                self.total_verificados += 1

        except (PermissionError, OSError) as e:
            if "267" not in str(e):
                self.logger.debug(f"Erro ao escavar {caminho}: {str(e)[:50]}")

    def _encontrar_duplicados(self, callback_progresso=None, callback_resultado=None) -> List[Dict]:
        """
        Encontra duplicados APENAS em pastas de usuário.
        Não varre Program Files (evita calcular hash de milhares de DLLs).
        """
        resultados = []
        hash_map = {}
        self.logger.info("BUSCANDO ARQUIVOS DUPLICADOS...")

        pastas_para_varer = [p for p in self.pastas_duplicados if p and os.path.exists(p)]
        arquivos_verificados = 0
        limite_arquivos = 20000  # Reduzido de 50000 para 20000

        for pasta in pastas_para_varer:
            if self.parar_varredura:
                return resultados
            if self._deve_ignorar(pasta):
                self._registrar_ignorado('sistema')
                continue
            try:
                arquivos_verificados = self._escavar_duplicados(
                    pasta, hash_map, callback_progresso,
                    arquivos_verificados, limite_arquivos
                )
                if arquivos_verificados >= limite_arquivos:
                    self.logger.aviso(f"Limite de {limite_arquivos} arquivos atingido")
                    break
            except (PermissionError, OSError) as e:
                self.logger.debug(f"Nao foi possivel verificar {pasta}: {str(e)[:50]}")
                continue

        for file_hash, arquivos in hash_map.items():
            if len(arquivos) > 1:
                arquivos_validos = []
                for a in arquivos:
                    if not self._arquivo_em_uso(a):
                        arquivos_validos.append(a)
                    else:
                        self._registrar_ignorado('em_uso')

                if len(arquivos_validos) > 1:
                    tamanho_total = sum(self._calcular_tamanho_arquivo(a) for a in arquivos_validos)
                    if tamanho_total > 1:
                        resultado = {
                            'hash': file_hash,
                            'arquivos': arquivos_validos,
                            'tamanho_total_mb': tamanho_total,
                            'tamanho_mb': tamanho_total,   # compatibilidade com UI
                            'tipo': 'duplicado',
                            'caminho': arquivos_validos[0],
                            'programa': os.path.basename(arquivos_validos[0]),
                            'num_copias': len(arquivos_validos),
                            'is_pasta': False
                        }
                        resultados.append(resultado)
                        if callback_resultado:
                            callback_resultado(resultado)
                        self.logger.aviso(
                            f"Duplicado: {os.path.basename(arquivos_validos[0])} "
                            f"({tamanho_total:.1f} MB, {len(arquivos_validos)} copias)"
                        )

        self.logger.info(f"Duplicados encontrados: {len(resultados)}")
        return resultados

    def _escavar_duplicados(self, caminho: str, hash_map: Dict,
                           callback_progresso, contador: int, limite: int) -> int:
        if self.parar_varredura or contador >= limite:
            return contador
        if self._deve_ignorar(caminho):
            return contador

        tem_perm, _ = self._verificar_permissao(caminho)
        if not tem_perm:
            return contador

        try:
            for item in os.listdir(caminho):
                if self.parar_varredura or contador >= limite:
                    return contador
                item_path = os.path.join(caminho, item)

                if self._deve_ignorar(item_path):
                    self._registrar_ignorado('lista_negra')
                    continue

                if os.path.isfile(item_path):
                    ext = os.path.splitext(item_path)[1].lower()
                    if ext in self.extensoes_ignoradas:
                        self._registrar_ignorado('extensao')
                        continue

                    if self._arquivo_em_uso(item_path):
                        self._registrar_ignorado('em_uso')
                        continue

                    try:
                        tamanho = os.path.getsize(item_path) / (1024 * 1024)
                        if tamanho > 1:
                            file_hash = self._calcular_hash(item_path)
                            if file_hash:
                                if file_hash not in hash_map:
                                    hash_map[file_hash] = []
                                hash_map[file_hash].append(item_path)
                                contador += 1
                                if contador % 100 == 0:
                                    self.logger.debug(f"Verificados: {contador} arquivos")
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
        try:
            hash_md5 = hashlib.md5()
            with open(caminho, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (PermissionError, OSError):
            return None

    def _calcular_tamanho_arquivo(self, caminho: str) -> float:
        try:
            return os.path.getsize(caminho) / (1024 * 1024)
        except (PermissionError, OSError):
            return 0

    def _obter_ultimo_acesso(self, caminho: str) -> Optional[datetime]:
        try:
            return datetime.fromtimestamp(os.stat(caminho).st_atime)
        except (PermissionError, OSError):
            return None

    def escanear_tudo(self, callback_progresso=None, callback_resultado=None) -> Dict[str, List]:
        """Executa varredura completa de 3 camadas"""
        self.ignorados_sistema = 0
        self.ignorados_em_uso = 0
        self.ignorados_lista_negra = 0
        self.ignorados_extensao = 0

        self.logger.limpar()
        self.resultados = {'resquicios': [], 'obsoletos': [], 'duplicados': []}
        self.parar_varredura = False
        self.total_verificados = 0

        self.logger.info("INICIANDO PROTOCOLO MISA-CLEANER v4.0...")
        self.logger.info("3 CAMADAS DE ANALISE ATIVADAS:")
        self.logger.info("   1. RESQUICIOS DE PROGRAMAS DELETADOS")
        self.logger.info("   2. ARQUIVOS OBSOLETOS (> 1 ano sem acesso)")
        self.logger.info("   3. ARQUIVOS DUPLICADOS (> 1 MB)")
        self.logger.info("PROTECAO DE SISTEMA ATIVADA")

        try:
            self.logger.info("")
            self.logger.info("=" * 50)
            self.resultados['resquicios'] = self._encontrar_resquicios_programas(
                callback_progresso, callback_resultado
            )

            if self.parar_varredura:
                self.logger.aviso("VARREDURA INTERROMPIDA PELO USUARIO")
                self.logger.atualizar_estatisticas_scanner(self)
                return self.resultados

            self.logger.info("")
            self.logger.info("=" * 50)
            self.resultados['obsoletos'] = self._encontrar_obsoletos(
                callback_progresso, callback_resultado
            )

            if self.parar_varredura:
                self.logger.aviso("VARREDURA INTERROMPIDA PELO USUARIO")
                self.logger.atualizar_estatisticas_scanner(self)
                return self.resultados

            self.logger.info("")
            self.logger.info("=" * 50)
            self.resultados['duplicados'] = self._encontrar_duplicados(
                callback_progresso, callback_resultado
            )

            total = sum(len(v) for v in self.resultados.values())
            total_ignorados = (
                self.ignorados_sistema + self.ignorados_em_uso +
                self.ignorados_lista_negra + self.ignorados_extensao
            )

            self.logger.info("")
            self.logger.info("=" * 50)
            self.logger.sucesso(f"VARREDURA CONCLUIDA! {total} ITENS ENCONTRADOS")
            self.logger.info(f"   Verificados: {self.total_verificados} itens")
            self.logger.info(f"   Resquicios: {len(self.resultados['resquicios'])}")
            self.logger.info(f"   Obsoletos: {len(self.resultados['obsoletos'])}")
            self.logger.info(f"   Duplicados: {len(self.resultados['duplicados'])}")

            if total_ignorados > 0:
                self.logger.info(f"   Ignorados: {total_ignorados} itens (protegidos/em uso)")

            self.logger.atualizar_estatisticas_scanner(self)

        except Exception as e:
            self.logger.critico(f"ERRO CRITICO NA VARREDURA: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())

        return self.resultados

    def parar(self) -> None:
        self.parar_varredura = True
        self.logger.aviso("PARANDO VARREDURA...")

    # ============================================
    # MÉTODOS DE DELEÇÃO (SEGUROS, SEM FORÇAR)
    # ============================================

    def deletar_pasta(self, caminho: str) -> Tuple[bool, str]:
        """
        Deleta uma pasta com verificação de segurança.
        NÃO força permissões. Se não puder deletar, retorna erro.
        """
        if self._eh_pasta_sistema_protegida(caminho):
            return False, f"PASTA DO SISTEMA PROTEGIDA: {caminho}"

        if self._arquivo_em_uso(caminho):
            return False, f"PASTA EM USO: {caminho}"

        try:
            shutil.rmtree(caminho)
            self.logger.sucesso(f"EXCLUIDO: {caminho}")
            return True, f"EXCLUIDO: {caminho}"
        except PermissionError:
            return False, f"SEM PERMISSAO: {caminho}"
        except Exception as e:
            return False, f"ERRO: {caminho} - {str(e)[:50]}"

    def deletar_arquivo(self, caminho: str) -> Tuple[bool, str]:
        """Deleta um arquivo com verificação de segurança."""
        if self._eh_pasta_sistema_protegida(caminho):
            return False, f"ARQUIVO DO SISTEMA PROTEGIDO: {caminho}"

        if self._arquivo_em_uso(caminho):
            return False, f"ARQUIVO EM USO: {caminho}"

        try:
            os.remove(caminho)
            self.logger.sucesso(f"EXCLUIDO: {caminho}")
            return True, f"EXCLUIDO: {caminho}"
        except PermissionError:
            return False, f"SEM PERMISSAO: {caminho}"
        except Exception as e:
            return False, f"ERRO: {caminho} - {str(e)[:50]}"

    def get_diagnostico_completo(self) -> Dict[str, Any]:
        resumo = self.logger.get_resumo()
        resumo.update({
            'ignorados_sistema': self.ignorados_sistema,
            'ignorados_em_uso': self.ignorados_em_uso,
            'ignorados_lista_negra': self.ignorados_lista_negra,
            'ignorados_extensao': self.ignorados_extensao,
            'total_ignorados': (
                self.ignorados_sistema + self.ignorados_em_uso +
                self.ignorados_lista_negra + self.ignorados_extensao
            )
        })
        return resumo