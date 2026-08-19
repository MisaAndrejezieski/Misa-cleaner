"""
Sistema de Logs Profissional para MISA-CLEANER
Gerencia erros, avisos e informações com níveis de severidade
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
    
    PRIORIDADES = {
        DEBUG: 0,
        INFO: 1,
        SUCESSO: 2,
        AVISO: 3,
        ERRO: 4,
        CRITICO: 5
    }


class Logger:
    """
    Sistema centralizado de logs com callback para UI
    """
    
    def __init__(self, callback_ui: Optional[Callable] = None):
        self.callback_ui = callback_ui
        self.logs: List[Dict[str, Any]] = []
        self.erros: List[str] = []
        self.avisos: List[str] = []
        self.contadores = {nivel: 0 for nivel in vars(LogNivel).values() if not nivel.startswith('_')}
        
        # Estatísticas
        self.total_verificados = 0
        self.total_encontrados = 0
        self.pastas_ignoradas = 0
        self.arquivos_ignorados = 0
        
    def log(self, mensagem: str, nivel: str = LogNivel.INFO, exibir_ui: bool = True) -> None:
        """
        Registra uma mensagem com nível de severidade
        
        Args:
            mensagem: Texto da mensagem
            nivel: Nível de severidade (LogNivel.*)
            exibir_ui: Se deve exibir na interface
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        cor = LogNivel.CORES.get(nivel, "#ffffff")
        
        registro = {
            'timestamp': timestamp,
            'nivel': nivel,
            'mensagem': mensagem,
            'cor': cor
        }
        
        self.logs.append(registro)
        self.contadores[nivel] = self.contadores.get(nivel, 0) + 1
        
        # Armazenar erros e avisos separadamente
        if nivel in [LogNivel.ERRO, LogNivel.CRITICO]:
            self.erros.append(mensagem)
        elif nivel == LogNivel.AVISO:
            self.avisos.append(mensagem)
        
        # Exibir na UI se solicitado
        if exibir_ui and self.callback_ui:
            try:
                self.callback_ui(mensagem, nivel)
            except Exception:
                pass  # Evita que erros no callback quebrem o logger
                
    def info(self, mensagem: str, exibir_ui: bool = True) -> None:
        self.log(mensagem, LogNivel.INFO, exibir_ui)
        
    def sucesso(self, mensagem: str, exibir_ui: bool = True) -> None:
        self.log(mensagem, LogNivel.SUCESSO, exibir_ui)
        
    def aviso(self, mensagem: str, exibir_ui: bool = True) -> None:
        self.log(mensagem, LogNivel.AVISO, exibir_ui)
        
    def erro(self, mensagem: str, exibir_ui: bool = True) -> None:
        self.log(mensagem, LogNivel.ERRO, exibir_ui)
        
    def critico(self, mensagem: str, exibir_ui: bool = True) -> None:
        self.log(mensagem, LogNivel.CRITICO, exibir_ui)
        
    def debug(self, mensagem: str, exibir_ui: bool = False) -> None:
        self.log(mensagem, LogNivel.DEBUG, exibir_ui)
    
    def get_resumo(self) -> Dict[str, Any]:
        """
        Retorna resumo completo dos logs para diagnóstico
        """
        return {
            'total_logs': len(self.logs),
            'contadores': self.contadores.copy(),
            'erros': self.erros.copy(),
            'avisos': self.avisos.copy(),
            'total_verificados': self.total_verificados,
            'total_encontrados': self.total_encontrados,
            'pastas_ignoradas': self.pastas_ignoradas,
            'arquivos_ignorados': self.arquivos_ignorados
        }
    
    def get_diagnostico(self) -> str:
        """
        Gera diagnóstico formatado para o usuário
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
        
        # Erros
        if resumo['erros']:
            linhas.append(f"🔴 {len(resumo['erros'])} ERROS encontrados:")
            for erro in resumo['erros'][:10]:  # Mostra até 10
                linhas.append(f"   • {erro}")
            if len(resumo['erros']) > 10:
                linhas.append(f"   ... e mais {len(resumo['erros']) - 10} erros")
            linhas.append("")
            linhas.append("💡 SUGESTÕES PARA RESOLVER ERROS:")
            linhas.append("   • Execute o programa como Administrador")
            linhas.append("   • Feche navegadores (Chrome, Edge, Firefox) durante a varredura")
            linhas.append("   • Desative temporariamente o antivírus ou Windows Defender")
            linhas.append("   • Verifique se os arquivos não estão em uso por outros programas")
        
        # Avisos
        if resumo['avisos']:
            linhas.append("")
            linhas.append(f"🟡 {len(resumo['avisos'])} AVISOS:")
            for aviso in resumo['avisos'][:10]:
                linhas.append(f"   • {aviso}")
            if len(resumo['avisos']) > 10:
                linhas.append(f"   ... e mais {len(resumo['avisos']) - 10} avisos")
        
        linhas.append("")
        linhas.append("═" * 60)
        
        return "\n".join(linhas)
    
    def limpar(self) -> None:
        """Limpa todos os logs"""
        self.logs.clear()
        self.erros.clear()
        self.avisos.clear()
        for nivel in self.contadores:
            self.contadores[nivel] = 0
        self.total_verificados = 0
        self.total_encontrados = 0
        self.pastas_ignoradas = 0
        self.arquivos_ignorados = 0