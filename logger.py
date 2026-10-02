"""
MISA-CLEANER - Sistema de Logs
VERSÃO 4.0 - Contadores corrigidos, diagnóstico separado por tipo
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


class Logger:
    """
    Sistema centralizado de logs com callback para UI.
    Não conhece cores, ícones ou widgets. Só dispara eventos.
    """

    def __init__(self, callback_ui: Optional[Callable] = None):
        self.callback_ui = callback_ui
        self.logs: List[Dict[str, Any]] = []
        self.erros: List[str] = []
        self.avisos: List[str] = []
        self.criticos: List[str] = []

        self.contadores = {
            LogNivel.INFO: 0,
            LogNivel.SUCESSO: 0,
            LogNivel.AVISO: 0,
            LogNivel.ERRO: 0,
            LogNivel.CRITICO: 0,
            LogNivel.DEBUG: 0,
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

        # Resultados por tipo (atualizados pelo scanner)
        self.total_resquicios = 0
        self.total_obsoletos = 0
        self.total_duplicados = 0

        self.modo_debug = False

        # Anti-spam
        self._ultima_mensagem = ""
        self._ultimo_nivel = ""
        self._repeticoes = 0

    def log(self, mensagem: str, nivel: str = LogNivel.INFO, exibir_ui: bool = True) -> None:
        """Registra uma mensagem com nível de severidade"""
        # Anti-spam
        if mensagem == self._ultima_mensagem and nivel == self._ultimo_nivel:
            self._repeticoes += 1
            if self._repeticoes > 5 and self._repeticoes % 10 != 0:
                return
        else:
            self._ultima_mensagem = mensagem
            self._ultimo_nivel = nivel
            self._repeticoes = 1

        timestamp = datetime.now().strftime("%H:%M:%S")

        registro = {
            'timestamp': timestamp,
            'nivel': nivel,
            'mensagem': mensagem,
        }

        self.logs.append(registro)
        self.contadores[nivel] = self.contadores.get(nivel, 0) + 1

        if nivel == LogNivel.ERRO:
            self.erros.append(mensagem)
        elif nivel == LogNivel.CRITICO:
            self.criticos.append(mensagem)
            self.erros.append(mensagem)
        elif nivel == LogNivel.AVISO:
            self.avisos.append(mensagem)

        if exibir_ui and self.callback_ui:
            if nivel == LogNivel.DEBUG and not self.modo_debug:
                return
            try:
                self.callback_ui(mensagem, nivel)
            except Exception:
                pass

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

    def set_modo_debug(self, ativo: bool = True) -> None:
        self.modo_debug = ativo

    def get_resumo(self) -> Dict[str, Any]:
        """Retorna resumo completo dos logs para diagnóstico"""
        return {
            'total_logs': len(self.logs),
            'contadores': self.contadores.copy(),
            'erros': self.erros.copy(),
            'avisos': self.avisos.copy(),
            'criticos': self.criticos.copy(),
            'total_verificados': self.total_verificados,
            'total_encontrados': self.total_encontrados,
            'total_resquicios': self.total_resquicios,
            'total_obsoletos': self.total_obsoletos,
            'total_duplicados': self.total_duplicados,
            'pastas_ignoradas': self.pastas_ignoradas,
            'arquivos_ignorados': self.arquivos_ignorados,
            'ignorados_sistema': self.ignorados_sistema,
            'ignorados_em_uso': self.ignorados_em_uso,
            'ignorados_lista_negra': self.ignorados_lista_negra,
            'ignorados_extensao': self.ignorados_extensao,
            'total_ignorados': (
                self.ignorados_sistema + self.ignorados_em_uso +
                self.ignorados_lista_negra + self.ignorados_extensao
            )
        }

    def get_diagnostico(self) -> str:
        """Gera diagnóstico formatado para o usuário"""
        resumo = self.get_resumo()

        linhas = []
        linhas.append("=" * 60)
        linhas.append("DIAGNOSTICO DA VARREDURA")
        linhas.append("=" * 60)
        linhas.append("")

        # Estatísticas gerais
        linhas.append(f"Pastas/arquivos verificados: {resumo['total_verificados']}")
        linhas.append("")

        # Resultados por tipo (corrigido)
        linhas.append("ITENS ENCONTRADOS POR TIPO:")
        linhas.append(f"  Resquicios: {resumo['total_resquicios']}")
        linhas.append(f"  Obsoletos:  {resumo['total_obsoletos']}")
        linhas.append(f"  Duplicados: {resumo['total_duplicados']}")
        linhas.append(f"  TOTAL:      {resumo['total_encontrados']}")
        linhas.append("")

        # Itens ignorados (corrigido)
        total_ignorados = resumo['total_ignorados']
        if total_ignorados > 0:
            linhas.append("ITENS IGNORADOS AUTOMATICAMENTE:")
            if resumo['ignorados_sistema'] > 0:
                linhas.append(f"  - {resumo['ignorados_sistema']} pastas/arquivos do sistema")
            if resumo['ignorados_em_uso'] > 0:
                linhas.append(f"  - {resumo['ignorados_em_uso']} arquivos em uso")
            if resumo['ignorados_lista_negra'] > 0:
                linhas.append(f"  - {resumo['ignorados_lista_negra']} pastas da lista negra")
            if resumo['ignorados_extensao'] > 0:
                linhas.append(f"  - {resumo['ignorados_extensao']} arquivos com extensao ignorada")
            linhas.append(f"  TOTAL: {total_ignorados} itens ignorados")
        else:
            linhas.append("NENHUM item foi ignorado")
        linhas.append("")

        # Erros
        if resumo['erros']:
            linhas.append(f"{len(resumo['erros'])} ERROS:")
            for erro in resumo['erros'][:10]:
                linhas.append(f"  - {erro}")
            if len(resumo['erros']) > 10:
                linhas.append(f"  ... e mais {len(resumo['erros']) - 10} erros")
            linhas.append("")
            linhas.append("SUGESTOES:")
            linhas.append("  - Execute como Administrador")
            linhas.append("  - Feche navegadores durante a varredura")
            linhas.append("")

        # Avisos
        if resumo['avisos']:
            linhas.append(f"{len(resumo['avisos'])} AVISOS:")
            for aviso in resumo['avisos'][:10]:
                linhas.append(f"  - {aviso}")
            if len(resumo['avisos']) > 10:
                linhas.append(f"  ... e mais {len(resumo['avisos']) - 10} avisos")
            linhas.append("")

        # Contadores por nível (DEBUG só se modo_debug)
        linhas.append("ESTATISTICAS DE LOGS:")
        for nivel, contador in resumo['contadores'].items():
            if contador > 0:
                if nivel == LogNivel.DEBUG and not self.modo_debug:
                    continue
                linhas.append(f"  {nivel}: {contador}")
        linhas.append("")

        linhas.append("=" * 60)
        return "\n".join(linhas)

    def get_diagnostico_rapido(self) -> str:
        resumo = self.get_resumo()
        partes = [
            f"Verificados: {resumo['total_verificados']}",
            f"Encontrados: {resumo['total_encontrados']}",
        ]
        if resumo['total_ignorados'] > 0:
            partes.append(f"Ignorados: {resumo['total_ignorados']}")
        if resumo['erros']:
            partes.append(f"Erros: {len(resumo['erros'])}")
        if resumo['avisos']:
            partes.append(f"Avisos: {len(resumo['avisos'])}")
        return " | ".join(partes)

    def get_ultimos_logs(self, quantidade: int = 20) -> List[Dict[str, Any]]:
        return self.logs[-quantidade:] if self.logs else []

    def get_logs_por_nivel(self, nivel: str) -> List[Dict[str, Any]]:
        return [log for log in self.logs if log['nivel'] == nivel]

    def limpar(self) -> None:
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

        self.ignorados_sistema = 0
        self.ignorados_em_uso = 0
        self.ignorados_lista_negra = 0
        self.ignorados_extensao = 0

        self.total_resquicios = 0
        self.total_obsoletos = 0
        self.total_duplicados = 0

        self._ultima_mensagem = ""
        self._ultimo_nivel = ""
        self._repeticoes = 0

    def atualizar_estatisticas_scanner(self, scanner: Any) -> None:
        """
        Atualiza estatísticas de ignorados E contadores por tipo
        a partir do scanner.
        """
        if hasattr(scanner, 'ignorados_sistema'):
            self.ignorados_sistema = scanner.ignorados_sistema
        if hasattr(scanner, 'ignorados_em_uso'):
            self.ignorados_em_uso = scanner.ignorados_em_uso
        if hasattr(scanner, 'ignorados_lista_negra'):
            self.ignorados_lista_negra = scanner.ignorados_lista_negra
        if hasattr(scanner, 'ignorados_extensao'):
            self.ignorados_extensao = scanner.ignorados_extensao

        if hasattr(scanner, 'resultados') and isinstance(scanner.resultados, dict):
            self.total_resquicios = len(scanner.resultados.get('resquicios', []))
            self.total_obsoletos = len(scanner.resultados.get('obsoletos', []))
            self.total_duplicados = len(scanner.resultados.get('duplicados', []))
            self.total_encontrados = (
                self.total_resquicios + self.total_obsoletos + self.total_duplicados
            )

        if hasattr(scanner, 'total_verificados'):
            self.total_verificados = scanner.total_verificados

    def exportar_logs(self, arquivo: str = "logs_misa_cleaner.txt") -> bool:
        if not self.logs:
            return False
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("MISA-CLEANER - LOGS DE VARREDURA\n")
                f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("=" * 70 + "\n\n")
                for log in self.logs:
                    f.write(f"[{log['timestamp']}] {log['nivel']}: {log['mensagem']}\n")
                f.write("\n" + "=" * 70 + "\n")
                f.write("DIAGNOSTICO:\n")
                f.write(self.get_diagnostico())
            return True
        except Exception:
            return False


def create_console_logger() -> Logger:
    """Cria um logger que exibe mensagens no console (para testes)"""
    def console_callback(mensagem: str, nivel: str) -> None:
        print(f"[{nivel}] {mensagem}")
    return Logger(callback_ui=console_callback)


def create_silent_logger() -> Logger:
    """Cria um logger silencioso (para testes)"""
    return Logger(callback_ui=None)


if __name__ == "__main__":
    logger = create_console_logger()
    logger.info("Sistema inicializado")
    logger.sucesso("Varredura concluída")
    logger.aviso("Aviso: pasta protegida ignorada")
    logger.erro("Erro ao acessar arquivo")
    logger.critico("Erro crítico no sistema")
    logger.debug("Mensagem de debug (não visível por padrão)")

    # Simular resultados
    logger.total_verificados = 1000
    logger.total_resquicios = 5
    logger.total_obsoletos = 10
    logger.total_duplicados = 3
    logger.total_encontrados = 18
    logger.ignorados_sistema = 50
    logger.ignorados_em_uso = 30

    print("\n" + "=" * 70)
    print(logger.get_diagnostico())

    print("\n" + "=" * 70)
    print("Diagnóstico rápido:", logger.get_diagnostico_rapido())