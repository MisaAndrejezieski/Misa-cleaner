"""
MISA-CLEANER - Sistema de Logs Profissional
VERSÃO 3.0 - Com diagnóstico detalhado e estatísticas de ignorados

GERENCIAMENTO:
✅ Níveis de severidade (INFO, SUCESSO, AVISO, ERRO, CRITICO, DEBUG)
✅ Callback para UI (exibição em tempo real)
✅ Armazenamento de logs com timestamp
✅ Estatísticas de erros e avisos
✅ Diagnóstico formatado para o usuário
✅ Estatísticas de itens ignorados (sistema, em uso, lista negra)
"""
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class LogNivel:
    """Níveis de severidade dos logs"""
    INFO = "INFO"
    SUCESSO = "SUCESSO"
    AVISO = "AVISO"
    ERRO = "ERRO"
    CRITICO = "CRITICO"
    DEBUG = "DEBUG"
    
    CORES = {
        INFO: "#6bcfff",      # Azul neon
        SUCESSO: "#6bffb8",   # Verde neon
        AVISO: "#ffe66d",     # Amarelo neon
        ERRO: "#ff6b6b",      # Vermelho neon
        CRITICO: "#ff1744",   # Vermelho intenso
        DEBUG: "#8888aa"      # Cinza
    }
    
    # Prioridades para ordenação/filtro
    PRIORIDADES = {
        DEBUG: 0,
        INFO: 1,
        SUCESSO: 2,
        AVISO: 3,
        ERRO: 4,
        CRITICO: 5
    }
    
    # Ícones para cada nível
    ICONES = {
        INFO: "ℹ️",
        SUCESSO: "✅",
        AVISO: "⚠️",
        ERRO: "❌",
        CRITICO: "💥",
        DEBUG: "🔍"
    }


class Logger:
    """
    Sistema centralizado de logs com callback para UI
    
    Uso:
        logger = Logger(callback_ui=minha_funcao)
        logger.info("Mensagem de informação")
        logger.sucesso("Operação concluída")
        logger.aviso("Aviso importante")
        logger.erro("Erro ocorreu")
        logger.critico("Erro crítico")
        logger.debug("Mensagem de debug (não exibida na UI)")
    """
    
    def __init__(self, callback_ui: Optional[Callable] = None):
        """
        Inicializa o sistema de logs
        
        Args:
            callback_ui: Função que recebe (mensagem, nivel) para exibir na UI
        """
        self.callback_ui = callback_ui
        self.logs: List[Dict[str, Any]] = []
        self.erros: List[str] = []
        self.avisos: List[str] = []
        self.criticos: List[str] = []
        
        # Contadores por nível
        self.contadores = {
            'INFO': 0,
            'SUCESSO': 0,
            'AVISO': 0,
            'ERRO': 0,
            'CRITICO': 0,
            'DEBUG': 0
        }
        
        # Estatísticas de varredura
        self.total_verificados = 0
        self.total_encontrados = 0
        self.pastas_ignoradas = 0
        self.arquivos_ignorados = 0
        
        # Estatísticas detalhadas de ignorados
        self.ignorados_sistema = 0
        self.ignorados_em_uso = 0
        self.ignorados_lista_negra = 0
        self.ignorados_extensao = 0
        
        # Modo debug (se True, exibe mensagens DEBUG na UI)
        self.modo_debug = False
        
        # Última mensagem (para evitar repetição)
        self._ultima_mensagem = ""
        self._ultimo_nivel = ""
        self._repeticoes = 0
        
    def log(self, mensagem: str, nivel: str = LogNivel.INFO, exibir_ui: bool = True) -> None:
        """
        Registra uma mensagem com nível de severidade
        
        Args:
            mensagem: Texto da mensagem
            nivel: Nível de severidade (LogNivel.*)
            exibir_ui: Se deve exibir na interface
        """
        # Evita repetição excessiva da mesma mensagem
        if mensagem == self._ultima_mensagem and nivel == self._ultimo_nivel:
            self._repeticoes += 1
            if self._repeticoes > 5:
                # Se repetiu muito, mostra apenas a cada 10 vezes
                if self._repeticoes % 10 != 0:
                    return
        else:
            self._ultima_mensagem = mensagem
            self._ultimo_nivel = nivel
            self._repeticoes = 1
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        cor = LogNivel.CORES.get(nivel, "#ffffff")
        icone = LogNivel.ICONES.get(nivel, "")
        
        # Formata a mensagem com ícone se não tiver
        if not mensagem.startswith(icone) and icone:
            mensagem_formatada = f"{icone} {mensagem}"
        else:
            mensagem_formatada = mensagem
        
        registro = {
            'timestamp': timestamp,
            'nivel': nivel,
            'mensagem': mensagem_formatada,
            'cor': cor,
            'icone': icone
        }
        
        self.logs.append(registro)
        self.contadores[nivel] = self.contadores.get(nivel, 0) + 1
        
        # Armazenar separadamente por categoria
        if nivel == LogNivel.ERRO:
            self.erros.append(mensagem_formatada)
        elif nivel == LogNivel.CRITICO:
            self.criticos.append(mensagem_formatada)
            self.erros.append(mensagem_formatada)  # Crítico também é erro
        elif nivel == LogNivel.AVISO:
            self.avisos.append(mensagem_formatada)
        
        # Exibir na UI se solicitado e não for DEBUG (ou se modo_debug estiver ativo)
        exibir = exibir_ui and self.callback_ui
        if exibir:
            # DEBUG só é exibido se modo_debug estiver ativo
            if nivel == LogNivel.DEBUG and not self.modo_debug:
                return
            try:
                self.callback_ui(mensagem_formatada, nivel)
            except Exception:
                pass  # Evita que erros no callback quebrem o logger
                
    def info(self, mensagem: str, exibir_ui: bool = True) -> None:
        """Registra uma mensagem informativa"""
        self.log(mensagem, LogNivel.INFO, exibir_ui)
        
    def sucesso(self, mensagem: str, exibir_ui: bool = True) -> None:
        """Registra uma mensagem de sucesso"""
        self.log(mensagem, LogNivel.SUCESSO, exibir_ui)
        
    def aviso(self, mensagem: str, exibir_ui: bool = True) -> None:
        """Registra um aviso"""
        self.log(mensagem, LogNivel.AVISO, exibir_ui)
        
    def erro(self, mensagem: str, exibir_ui: bool = True) -> None:
        """Registra um erro"""
        self.log(mensagem, LogNivel.ERRO, exibir_ui)
        
    def critico(self, mensagem: str, exibir_ui: bool = True) -> None:
        """Registra um erro crítico"""
        self.log(mensagem, LogNivel.CRITICO, exibir_ui)
        
    def debug(self, mensagem: str, exibir_ui: bool = False) -> None:
        """
        Registra uma mensagem de debug
        
        Args:
            mensagem: Mensagem de debug
            exibir_ui: Se deve exibir na UI (padrão False)
        """
        self.log(mensagem, LogNivel.DEBUG, exibir_ui)
    
    def set_modo_debug(self, ativo: bool = True) -> None:
        """
        Ativa/desativa o modo debug (exibe mensagens DEBUG na UI)
        
        Args:
            ativo: True para ativar, False para desativar
        """
        self.modo_debug = ativo
        if ativo:
            self.info("🔍 Modo DEBUG ativado")
        else:
            self.info("🔍 Modo DEBUG desativado")
    
    def get_resumo(self) -> Dict[str, Any]:
        """
        Retorna resumo completo dos logs para diagnóstico
        
        Returns:
            Dicionário com estatísticas e listas de erros/avisos
        """
        return {
            'total_logs': len(self.logs),
            'contadores': self.contadores.copy(),
            'erros': self.erros.copy(),
            'avisos': self.avisos.copy(),
            'criticos': self.criticos.copy(),
            'total_verificados': self.total_verificados,
            'total_encontrados': self.total_encontrados,
            'pastas_ignoradas': self.pastas_ignoradas,
            'arquivos_ignorados': self.arquivos_ignorados,
            # Estatísticas detalhadas de ignorados
            'ignorados_sistema': self.ignorados_sistema,
            'ignorados_em_uso': self.ignorados_em_uso,
            'ignorados_lista_negra': self.ignorados_lista_negra,
            'ignorados_extensao': self.ignorados_extensao,
            'total_ignorados': (self.ignorados_sistema + self.ignorados_em_uso + 
                               self.ignorados_lista_negra + self.ignorados_extensao)
        }
    
    def get_diagnostico(self) -> str:
        """
        Gera diagnóstico formatado para o usuário
        
        Returns:
            String formatada com diagnóstico completo
        """
        resumo = self.get_resumo()
        
        linhas = []
        linhas.append("═" * 60)
        linhas.append("📊 DIAGNÓSTICO DA VARREDURA")
        linhas.append("═" * 60)
        linhas.append("")
        
        # Estatísticas gerais
        linhas.append(f"📁 Pastas/arquivos verificados: {resumo['total_verificados']}")
        linhas.append(f"📦 Resquícios encontrados: {resumo['total_encontrados']}")
        
        if resumo['pastas_ignoradas'] > 0:
            linhas.append(f"⏭️ Pastas ignoradas: {resumo['pastas_ignoradas']}")
        if resumo['arquivos_ignorados'] > 0:
            linhas.append(f"⏭️ Arquivos ignorados: {resumo['arquivos_ignorados']}")
        
        linhas.append("")
        
        # Itens ignorados automaticamente
        total_ignorados = resumo.get('total_ignorados', 0)
        if total_ignorados > 0:
            linhas.append("🛡️ ITENS IGNORADOS AUTOMATICAMENTE:")
            
            if resumo.get('ignorados_sistema', 0) > 0:
                linhas.append(f"   • {resumo['ignorados_sistema']} pastas/arquivos do sistema protegido")
                
            if resumo.get('ignorados_em_uso', 0) > 0:
                linhas.append(f"   • {resumo['ignorados_em_uso']} arquivos em uso (Edge, Chrome, Java, etc.)")
                
            if resumo.get('ignorados_lista_negra', 0) > 0:
                linhas.append(f"   • {resumo['ignorados_lista_negra']} pastas da lista negra (node_modules, .git, etc.)")
                
            if resumo.get('ignorados_extensao', 0) > 0:
                linhas.append(f"   • {resumo['ignorados_extensao']} arquivos com extensões ignoradas")
                
            linhas.append(f"   ✅ TOTAL: {total_ignorados} itens ignorados com segurança")
            linhas.append("")
        else:
            linhas.append("✅ NENHUM item foi ignorado")
            linhas.append("")
        
        # Erros
        if resumo['erros']:
            linhas.append(f"🔴 {len(resumo['erros'])} ERROS encontrados:")
            # Mostra até 10 erros
            for erro in resumo['erros'][:10]:
                linhas.append(f"   • {erro}")
            if len(resumo['erros']) > 10:
                linhas.append(f"   ... e mais {len(resumo['erros']) - 10} erros")
            linhas.append("")
            
            # Sugestões para resolver erros
            linhas.append("💡 SUGESTÕES PARA RESOLVER ERROS:")
            linhas.append("   • Execute o programa como Administrador")
            linhas.append("   • Feche navegadores (Edge, Chrome, Firefox) durante a varredura")
            linhas.append("   • Desative temporariamente o antivírus ou Windows Defender")
            linhas.append("   • Verifique se os arquivos não estão em uso por outros programas")
            linhas.append("")
        
        # Avisos
        if resumo['avisos']:
            linhas.append(f"🟡 {len(resumo['avisos'])} AVISOS:")
            # Mostra até 10 avisos
            for aviso in resumo['avisos'][:10]:
                linhas.append(f"   • {aviso}")
            if len(resumo['avisos']) > 10:
                linhas.append(f"   ... e mais {len(resumo['avisos']) - 10} avisos")
            linhas.append("")
        
        # Contadores por nível
        linhas.append("📊 ESTATÍSTICAS DE LOGS:")
        for nivel, contador in resumo['contadores'].items():
            if contador > 0:
                icone = LogNivel.ICONES.get(nivel, "")
                linhas.append(f"   {icone} {nivel}: {contador}")
        linhas.append("")
        
        linhas.append("═" * 60)
        
        return "\n".join(linhas)
    
    def get_diagnostico_rapido(self) -> str:
        """
        Gera diagnóstico rápido (versão resumida)
        
        Returns:
            String formatada com diagnóstico resumido
        """
        resumo = self.get_resumo()
        
        linhas = []
        linhas.append(f"📊 Verificados: {resumo['total_verificados']} | ")
        linhas.append(f"📦 Encontrados: {resumo['total_encontrados']}")
        
        if resumo['total_ignorados'] > 0:
            linhas.append(f" | 🛡️ Ignorados: {resumo['total_ignorados']}")
            
        if resumo['erros']:
            linhas.append(f" | 🔴 Erros: {len(resumo['erros'])}")
            
        if resumo['avisos']:
            linhas.append(f" | 🟡 Avisos: {len(resumo['avisos'])}")
            
        return "".join(linhas)
    
    def get_ultimos_logs(self, quantidade: int = 20) -> List[Dict[str, Any]]:
        """
        Retorna os últimos N logs
        
        Args:
            quantidade: Número de logs a retornar
            
        Returns:
            Lista dos últimos logs
        """
        return self.logs[-quantidade:] if self.logs else []
    
    def get_logs_por_nivel(self, nivel: str) -> List[Dict[str, Any]]:
        """
        Retorna logs filtrados por nível
        
        Args:
            nivel: Nível de severidade (LogNivel.*)
            
        Returns:
            Lista de logs do nível especificado
        """
        return [log for log in self.logs if log['nivel'] == nivel]
    
    def limpar(self) -> None:
        """Limpa todos os logs e reseta contadores"""
        self.logs.clear()
        self.erros.clear()
        self.avisos.clear()
        self.criticos.clear()
        
        for nivel in self.contadores:
            self.contadores[nivel] = 0
            
        self.total_verificados = 0
        self.total_encontrados = 0
        self.pastas_ignoradas = 0
        self.arquivos_ignorados = 0
        
        # Reset estatísticas de ignorados
        self.ignorados_sistema = 0
        self.ignorados_em_uso = 0
        self.ignorados_lista_negra = 0
        self.ignorados_extensao = 0
        
        self._ultima_mensagem = ""
        self._ultimo_nivel = ""
        self._repeticoes = 0
    
    def reset_estatisticas_ignorados(self) -> None:
        """Reseta apenas as estatísticas de ignorados"""
        self.ignorados_sistema = 0
        self.ignorados_em_uso = 0
        self.ignorados_lista_negra = 0
        self.ignorados_extensao = 0
    
    def atualizar_estatisticas_ignorados(self, scanner: Any) -> None:
        """
        Atualiza estatísticas de ignorados a partir do scanner
        
        Args:
            scanner: Instância do Scanner com atributos de ignorados
        """
        if hasattr(scanner, 'ignorados_sistema'):
            self.ignorados_sistema = scanner.ignorados_sistema
        if hasattr(scanner, 'ignorados_em_uso'):
            self.ignorados_em_uso = scanner.ignorados_em_uso
        if hasattr(scanner, 'ignorados_lista_negra'):
            self.ignorados_lista_negra = scanner.ignorados_lista_negra
        if hasattr(scanner, 'ignorados_extensao'):
            self.ignorados_extensao = scanner.ignorados_extensao
            
        # Atualiza totais
        self.pastas_ignoradas = self.ignorados_sistema + self.ignorados_lista_negra
        self.arquivos_ignorados = self.ignorados_em_uso + self.ignorados_extensao
    
    def exportar_logs(self, arquivo: str = "logs_misa_cleaner.txt") -> bool:
        """
        Exporta todos os logs para um arquivo de texto
        
        Args:
            arquivo: Nome do arquivo de saída
            
        Returns:
            True se exportado com sucesso, False caso contrário
        """
        if not self.logs:
            return False
            
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write("═" * 70 + "\n")
                f.write("MISA-CLEANER - LOGS DE VARREDURA\n")
                f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("═" * 70 + "\n\n")
                
                for log in self.logs:
                    f.write(f"[{log['timestamp']}] {log['nivel']}: {log['mensagem']}\n")
                
                f.write("\n" + "═" * 70 + "\n")
                f.write("DIAGNÓSTICO:\n")
                f.write(self.get_diagnostico())
                
            return True
        except Exception:
            return False


# Função auxiliar para criar um logger com callback padrão (print)
def create_console_logger() -> Logger:
    """
    Cria um logger que exibe mensagens no console (para testes)
    
    Returns:
        Logger configurado para console
    """
    def console_callback(mensagem: str, nivel: str) -> None:
        cor = LogNivel.CORES.get(nivel, "")
        print(f"{cor}{mensagem}\033[0m")
    
    return Logger(callback_ui=console_callback)


# Função auxiliar para criar um logger silencioso (para testes)
def create_silent_logger() -> Logger:
    """
    Cria um logger silencioso (não exibe nada)
    
    Returns:
        Logger sem callback
    """
    return Logger(callback_ui=None)


# Exemplo de uso
if __name__ == "__main__":
    # Teste do logger
    logger = create_console_logger()
    
    logger.info("Sistema inicializado")
    logger.sucesso("Varredura concluída")
    logger.aviso("Aviso: pasta protegida ignorada")
    logger.erro("Erro ao acessar arquivo")
    logger.critico("Erro crítico no sistema")
    logger.debug("Mensagem de debug (não visível por padrão)")
    
    # Ativar modo debug
    logger.set_modo_debug(True)
    logger.debug("Mensagem de debug (visível agora)")
    
    # Estatísticas
    logger.total_verificados = 1000
    logger.total_encontrados = 25
    logger.ignorados_sistema = 50
    logger.ignorados_em_uso = 30
    
    print("\n" + "=" * 70)
    print(logger.get_diagnostico())
    
    print("\n" + "=" * 70)
    print("Diagnóstico rápido:", logger.get_diagnostico_rapido())
    
    print("\n" + "=" * 70)
    print("Últimos 5 logs:")
    for log in logger.get_ultimos_logs(5):
        print(f"  {log['timestamp']} [{log['nivel']}] {log['mensagem']}")