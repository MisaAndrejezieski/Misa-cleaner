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
        
        # Pastas a serem ignoradas (sistema)
        self.pastas_ignoradas = [
            "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
            "C:\\System32", "C:\\Users\\Public", "C:\\$Recycle.Bin",
            "C:\\System Volume Information", "D:\\System Volume Information",
            "C:\\Windows\\WinSxS", "C:\\Windows\\Installer"
        ]
        
        # Programas conhecidos para verificar resquícios
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
        """Verifica se um programa ainda está instalado no sistema"""
        # Verifica nas pastas de programas
        for pasta in self.pastas_sistema[:3]:
            if not pasta:
                continue
            caminho_programa = os.path.join(pasta, nome_programa)
            if os.path.exists(caminho_programa):
                return True
        
        # Verifica no PATH do sistema
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
        """Encontra pastas de programas que foram deletados"""
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
                    
                    # Verifica se deve ignorar esta pasta
                    if any(caminho_item.startswith(ign) for ign in self.pastas_ignoradas):
                        continue
                        
                    for programa in self.programas_conhecidos:
                        if programa.lower() in item.lower():
                            # Verifica se o programa ainda existe
                            if not self.verificar_se_programa_existe(programa):
                                tamanho = self.calcular_tamanho(caminho_item)
                                if tamanho > 1:  # Mais de 1MB
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
        """Encontra arquivos e pastas não acessados há mais de 1 ano"""
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
        """Função recursiva para encontrar arquivos obsoletos"""
        if self.parar_varredura:
            return
        
        # Verifica se deve ignorar esta pasta
        if any(caminho.startswith(ign) for ign in self.pastas_ignoradas):
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
                            if tamanho > 1:  # Mais de 1MB
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
        """Encontra arquivos duplicados baseado no hash MD5"""
        resultados = []
        hash_map = {}
        pastas_para_varer = [p for p in self.pastas_sistema if p and os.path.exists(p)]
        arquivos_verificados = 0
        limite_arquivos = 1000  # Limite para não travar o sistema
        
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
                
        # Identifica duplicados
        for file_hash, arquivos in hash_map.items():
            if len(arquivos) > 1:
                tamanho_total = sum(self.calcular_tamanho_arquivo(a) for a in arquivos)
                if tamanho_total > 1:
                    resultado = {
                        'hash': file_hash,
                        'arquivos': arquivos,
                        'tamanho_total_mb': tamanho_total,
                        'tipo': 'duplicado',
                        'caminho': arquivos[0]  # Mostra o primeiro como referência
                    }
                    resultados.append(resultado)
                    if callback_resultado:
                        callback_resultado(resultado)
                    
        return resultados

    def _escavar_duplicados(self, caminho, hash_map, callback_progresso, contador, limite):
        """Função recursiva para encontrar arquivos duplicados"""
        if self.parar_varredura or contador >= limite:
            return contador
            
        # Verifica se deve ignorar esta pasta
        if any(caminho.startswith(ign) for ign in self.pastas_ignoradas):
            return contador
            
        try:
            for item in os.listdir(caminho):
                if self.parar_varredura or contador >= limite:
                    return contador
                    
                item_path = os.path.join(caminho, item)
                
                if os.path.isfile(item_path):
                    try:
                        tamanho = os.path.getsize(item_path) / (1024 * 1024)
                        if tamanho > 1:  # Só verifica arquivos > 1MB
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

    def calcular_tamanho(self, caminho):
        """Calcula o tamanho de uma pasta em MB"""
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
        """Calcula o tamanho de um arquivo em MB"""
        try:
            return os.path.getsize(caminho) / (1024 * 1024)
        except:
            return 0

    def calcular_hash(self, caminho):
        """Calcula o hash MD5 de um arquivo"""
        try:
            hash_md5 = hashlib.md5()
            with open(caminho, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None

    def obter_ultimo_acesso(self, caminho):
        """Obtém a data do último acesso"""
        try:
            return datetime.fromtimestamp(os.stat(caminho).st_atime)
        except:
            return None

    def escanear_tudo(self, callback_progresso=None, callback_resultado=None):
        """Executa todos os tipos de varredura"""
        self.resultados = {
            'resquicios': [],
            'obsoletos': [],
            'duplicados': []
        }
        self.parar_varredura = False
        
        try:
            # 1. Resquícios de programas deletados
            self.resultados['resquicios'] = self.encontrar_resquicios_programas(
                callback_progresso, callback_resultado
            )
            
            # 2. Arquivos obsoletos
            if not self.parar_varredura:
                self.resultados['obsoletos'] = self.encontrar_obsoletos(
                    callback_progresso, callback_resultado
                )
            
            # 3. Arquivos duplicados
            if not self.parar_varredura:
                self.resultados['duplicados'] = self.encontrar_duplicados(
                    callback_progresso, callback_resultado
                )
                
        except Exception as e:
            print(f"Erro durante a varredura: {e}")
            
        return self.resultados

    def parar(self):
        """Para a varredura em execução"""
        self.parar_varredura = True

    def deletar_pasta(self, caminho):
        """Deleta uma pasta e todo seu conteúdo"""
        try:
            shutil.rmtree(caminho)
            return True, f"EXCLUÍDO: {caminho}"
        except Exception as e:
            return False, f"ERRO: {str(e)}"

    def deletar_arquivo(self, caminho):
        """Deleta um arquivo individual"""
        try:
            os.remove(caminho)
            return True, f"EXCLUÍDO: {caminho}"
        except Exception as e:
            return False, f"ERRO: {str(e)}"

    def mover_para_lixeira(self, caminho):
        """Move um arquivo/pasta para a lixeira (Windows)"""
        try:
            import ctypes
            from ctypes import wintypes

            # Usa a API do Windows para mover para a lixeira
            class SHFILEOPSTRUCTW(ctypes.Structure):
                _fields_ = [
                    ('hwnd', ctypes.c_void_p),
                    ('wFunc', wintypes.UINT),
                    ('pFrom', wintypes.LPCWSTR),
                    ('pTo', wintypes.LPCWSTR),
                    ('fFlags', wintypes.UINT),
                    ('fAnyOperationsAborted', wintypes.BOOL),
                    ('hNameMappings', ctypes.c_void_p),
                    ('lpszProgressTitle', wintypes.LPCWSTR)
                ]
            
            FO_DELETE = 0x0003
            FOF_ALLOWUNDO = 0x0040
            FOF_NOCONFIRMATION = 0x0010
            FOF_SILENT = 0x0004
            
            # Prepara o caminho (deve terminar com dois null terminators)
            caminho_unicode = caminho + '\0\0'
            
            # Cria a estrutura
            operation = SHFILEOPSTRUCTW()
            operation.wFunc = FO_DELETE
            operation.pFrom = caminho_unicode
            operation.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT
            
            # Executa
            result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(operation))
            
            if result == 0:
                return True, f"MOVIDO PARA LIXEIRA: {caminho}"
            else:
                return False, f"ERRO AO MOVER PARA LIXEIRA: {caminho}"
                
        except Exception as e:
            # Fallback para exclusão direta se a lixeira falhar
            return self.deletar_pasta(caminho)