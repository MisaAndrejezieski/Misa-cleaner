import hashlib
import os
import shutil
from datetime import datetime, timedelta

from matrix_style import (AMARELO, VERDE_ESCURO, VERDE_MATRIX, VERMELHO,
                          imprimir_matrix)


class Scanner:
    def __init__(self):
        self.resultados = {
            'resquicios': [],
            'obsoletos': [],
            'duplicados': []
        }
        self.parar_varredura = False
        
        # Pastas comuns de programas para verificar
        self.pastas_sistema = [
            os.environ.get('APPDATA', ''),
            os.environ.get('LOCALAPPDATA', ''),
            os.environ.get('PROGRAMFILES', ''),
            os.environ.get('PROGRAMFILES(X86)', ''),
            os.path.expanduser('~')
        ]
        
        # Programas conhecidos (para verificar se ainda existem)
        self.programas_conhecidos = [
            'Adobe', 'Spotify', 'Steam', 'Discord', 'Slack',
            'Zoom', 'Teams', 'Notion', 'Obsidian', 'VSCode',
            'Git', 'Node.js', 'Python', 'Anaconda', 'Chrome',
            'Firefox', 'Edge', 'Opera', 'Brave', 'Vivaldi'
        ]

    def verificar_se_programa_existe(self, nome_programa):
        """Verifica se um programa ainda está instalado"""
        # Verifica nas pastas de programas
        for pasta in self.pastas_sistema[:3]:
            if not pasta:
                continue
            caminho_programa = os.path.join(pasta, nome_programa)
            if os.path.exists(caminho_programa):
                return True
        return False

    def encontrar_resquicios_programas(self, callback_progresso=None):
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
                        
                    # Verifica se o item está na lista de programas conhecidos
                    for programa in self.programas_conhecidos:
                        if programa.lower() in item.lower():
                            if not self.verificar_se_programa_existe(programa):
                                tamanho = self.calcular_tamanho(caminho_item)
                                if tamanho > 1:  # Mais de 1MB
                                    resultados.append({
                                        'caminho': caminho_item,
                                        'tamanho_mb': tamanho,
                                        'tipo': 'resquicio',
                                        'programa': programa,
                                        'ultimo_acesso': self.obter_ultimo_acesso(caminho_item)
                                    })
                                    imprimir_matrix(
                                        f"🔍 RESQUÍCIO ENCONTRADO: {programa} - {caminho_item}",
                                        cor=AMARELO
                                    )
                            break
                    
                    if callback_progresso:
                        callback_progresso(caminho_item)
                        
            except (PermissionError, OSError):
                pass
                
        return resultados

    def encontrar_obsoletos(self, callback_progresso=None):
        """Encontra arquivos e pastas não acessados há mais de 1 ano"""
        resultados = []
        um_ano_atras = datetime.now() - timedelta(days=365)
        
        # Pastas a serem varridas
        pastas_para_varer = [p for p in self.pastas_sistema if p and os.path.exists(p)]
        
        for pasta in pastas_para_varer:
            if self.parar_varredura:
                return resultados
            try:
                self._escavar_obsoletos(pasta, um_ano_atras, resultados, callback_progresso)
            except (PermissionError, OSError):
                continue
                
        return resultados

    def _escavar_obsoletos(self, caminho, data_limite, resultados, callback_progresso):
        """Função recursiva para encontrar arquivos obsoletos"""
        if self.parar_varredura:
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
                                resultados.append({
                                    'caminho': item_path,
                                    'tamanho_mb': tamanho,
                                    'tipo': 'obsoleto',
                                    'ultimo_acesso': ultimo_acesso
                                })
                                imprimir_matrix(
                                    f"📂 OBSOLETO: {os.path.basename(item_path)} - {tamanho:.1f}MB",
                                    cor=VERDE_ESCURO
                                )
                    
                    if os.path.isdir(item_path):
                        self._escavar_obsoletos(item_path, data_limite, resultados, callback_progresso)
                        
                except (PermissionError, OSError):
                    continue
                    
            if callback_progresso:
                callback_progresso(caminho)
                
        except (PermissionError, OSError):
            pass

    def encontrar_duplicados(self, callback_progresso=None):
        """Encontra arquivos duplicados baseado no hash MD5"""
        resultados = []
        hash_map = {}
        pastas_para_varer = [p for p in self.pastas_sistema if p and os.path.exists(p)]
        
        for pasta in pastas_para_varer:
            if self.parar_varredura:
                return resultados
            try:
                self._escavar_duplicados(pasta, hash_map, callback_progresso)
            except (PermissionError, OSError):
                continue
                
        # Identifica duplicados
        for file_hash, arquivos in hash_map.items():
            if len(arquivos) > 1:
                # Só considera duplicados se todos forem > 1MB
                tamanho_total = sum(self.calcular_tamanho_arquivo(a) for a in arquivos)
                if tamanho_total > 1:
                    resultados.append({
                        'hash': file_hash,
                        'arquivos': arquivos,
                        'tamanho_total_mb': tamanho_total
                    })
                    
        return resultados

    def _escavar_duplicados(self, caminho, hash_map, callback_progresso):
        """Função recursiva para encontrar arquivos duplicados"""
        if self.parar_varredura:
            return
            
        try:
            for item in os.listdir(caminho):
                if self.parar_varredura:
                    return
                    
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
                    except (PermissionError, OSError):
                        pass
                elif os.path.isdir(item_path):
                    self._escavar_duplicados(item_path, hash_map, callback_progresso)
                    
            if callback_progresso:
                callback_progresso(caminho)
                
        except (PermissionError, OSError):
            pass

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
        imprimir_matrix(">> INICIANDO VARREDURA MATRIX...", delay=0.03)
        imprimir_matrix(">> 3 CAMADAS DE ANÁLISE:", delay=0.02)
        imprimir_matrix("   1. RESQUÍCIOS DE PROGRAMAS DELETADOS", delay=0.02)
        imprimir_matrix("   2. ARQUIVOS OBSOLETOS", delay=0.02)
        imprimir_matrix("   3. ARQUIVOS DUPLICADOS", delay=0.02)
        
        self.resultados = {
            'resquicios': [],
            'obsoletos': [],
            'duplicados': []
        }
        self.parar_varredura = False
        
        # 1. Resquícios
        imprimir_matrix("\n>> CAMADA 1: CAÇANDO RESQUÍCIOS...", cor=VERDE_MATRIX)
        self.resultados['resquicios'] = self.encontrar_resquicios_programas(callback_progresso)
        
        # 2. Obsoletos
        if not self.parar_varredura:
            imprimir_matrix("\n>> CAMADA 2: COLETANDO OBSOLETOS...", cor=VERDE_MATRIX)
            self.resultados['obsoletos'] = self.encontrar_obsoletos(callback_progresso)
        
        # 3. Duplicados
        if not self.parar_varredura:
            imprimir_matrix("\n>> CAMADA 3: DETECTANDO DUPLICADOS...", cor=VERDE_MATRIX)
            self.resultados['duplicados'] = self.encontrar_duplicados(callback_progresso)
        
        total = (len(self.resultados['resquicios']) + 
                len(self.resultados['obsoletos']) + 
                len(self.resultados['duplicados']))
        
        imprimir_matrix(f"\n>> VARREDURA CONCLUÍDA! {total} RESQUÍCIOS ENCONTRADOS.", cor=VERDE_MATRIX)
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
            imprimir_matrix(f">> ERRO NA EXCLUSÃO: {caminho}", cor=VERMELHO)
            return False, f"ERRO: {str(e)}"

    def deletar_arquivo(self, caminho):
        try:
            os.remove(caminho)
            imprimir_matrix(f">> ARQUIVO EXCLUÍDO: {caminho}", cor=VERDE_ESCURO)
            return True, f"EXCLUÍDO: {caminho}"
        except Exception as e:
            imprimir_matrix(f">> ERRO NA EXCLUSÃO: {caminho}", cor=VERMELHO)
            return False, f"ERRO: {str(e)}"