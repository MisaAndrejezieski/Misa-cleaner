"""
MISA-CLEANER - Interface Matrix Imersiva
COM EFEITO MATRIX EM TELA CHEIA - USANDO MATRIX_RAIN
"""
import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List, Optional

from logger import Logger, LogNivel
from matrix_rain import MatrixRain  # IMPORTADO AQUI!
from scanner import Scanner


class MisaCleanerUI:
    """Interface Principal do MISA-CLEANER com Efeito Matrix"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        
        # Configurar janela
        self.root.title("MISA-CLEANER - Caçador de Resquícios Digitais")
        self.root.configure(bg='#0a0a0f')
        self.root.geometry("1200x900")
        self.root.minsize(900, 700)
        self.centralizar_janela()
        
        # Cores do tema
        self.cores = {
            'bg': '#0a0a0f',
            'bg_secundario': '#15152a',
            'bg_terciario': '#1a1a2e',
            'neon_azul': '#6bcfff',
            'neon_verde': '#6bffb8',
            'neon_roxo': '#b06bff',
            'neon_rosa': '#ff6b9d',
            'neon_amarelo': '#ffe66d',
            'neon_vermelho': '#ff6b6b',
            'texto': '#e0e0ff',
            'texto_escuro': '#8888aa',
            'verde_matrix': '#00ff41'
        }
        
        # Inicializar componentes
        self.logger = Logger(callback_ui=self._on_log)
        self.scanner = Scanner(self.logger)
        self.resultados: List[Dict] = []
        self.varrendo = False
        self.scanner_thread: Optional[threading.Thread] = None
        
        # Matrix Rain (tela cheia durante varredura)
        self.matrix = None
        
        # Construir interface
        self._setup_ui()
        
        # Configurar fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.fechar)
        
    def centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        largura = self.root.winfo_width()
        altura = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        self.root.geometry(f'{largura}x{altura}+{x}+{y}')
        
    def _on_log(self, mensagem: str, nivel: str = LogNivel.INFO):
        """Callback do logger para exibir na UI"""
        if hasattr(self, 'terminal') and self.terminal:
            destaque = nivel in [LogNivel.SUCESSO, LogNivel.CRITICO]
            self._escrever_terminal(f">> {mensagem}", nivel, destaque)
            
    def _setup_ui(self):
        """Constrói a interface completa"""
        # Frame principal (será ocultado durante a varredura)
        self.main_frame = tk.Frame(self.root, bg=self.cores['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # ===== HEADER =====
        self._criar_header(self.main_frame)
        
        # ===== TERMINAL MATRIX =====
        self._criar_terminal(self.main_frame)
        
        # ===== BOTÕES DE CONTROLE =====
        self._criar_botoes(self.main_frame)
        
        # ===== RESULTADOS =====
        self._criar_resultados(self.main_frame)
        
        # ===== STATUS =====
        self._criar_status(self.main_frame)
        
    def _criar_header(self, parent):
        """Cria o cabeçalho compacto da central de varredura"""
        header_frame = tk.Frame(parent, bg=self.cores['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 8))

        accent = tk.Frame(header_frame, bg=self.cores['verde_matrix'], width=4)
        accent.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))

        intro = tk.Frame(header_frame, bg=self.cores['bg'])
        intro.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            intro,
            text="SYSTEM / SCAN CONSOLE",
            font=('Consolas', 9, 'bold'),
            fg=self.cores['neon_verde'],
            bg=self.cores['bg']
        ).pack(anchor=tk.W)

        tk.Label(
            intro,
            text="Digital residue detection",
            font=('Consolas', 17, 'bold'),
            fg=self.cores['texto'],
            bg=self.cores['bg']
        ).pack(anchor=tk.W, pady=(2, 0))

        tk.Label(
            intro,
            text="Three-layer analysis for files and duplicates",
            font=('Consolas', 9),
            fg=self.cores['texto_escuro'],
            bg=self.cores['bg']
        ).pack(anchor=tk.W, pady=(3, 0))

        status = tk.Frame(
            header_frame,
            bg=self.cores['bg_secundario'],
            highlightbackground=self.cores['bg_terciario'],
            highlightthickness=1,
            padx=14,
            pady=6
        )
        status.pack(side=tk.RIGHT, padx=(14, 0))

        status_line = tk.Frame(status, bg=self.cores['bg_secundario'])
        status_line.pack(anchor=tk.E)

        tk.Label(
            status_line,
            text="●",
            font=('Consolas', 10),
            fg=self.cores['verde_matrix'],
            bg=self.cores['bg_secundario']
        ).pack(side=tk.LEFT, padx=(0, 6))

        tk.Label(
            status_line,
            text="READY",
            font=('Consolas', 9, 'bold'),
            fg=self.cores['neon_verde'],
            bg=self.cores['bg_secundario']
        ).pack(side=tk.LEFT)

        tk.Label(
            status,
            text="3 LAYERS  /  MATRIX MODE",
            font=('Consolas', 8),
            fg=self.cores['texto_escuro'],
            bg=self.cores['bg_secundario']
        ).pack(anchor=tk.E, pady=(5, 0))
        
    def _criar_terminal(self, parent):
        """Cria o terminal Matrix (OCUPA 65% DA TELA)"""
        terminal_container = tk.Frame(parent, bg=self.cores['bg'])
        terminal_container.pack(fill=tk.BOTH, expand=True, pady=6)
        
        terminal_wrapper = tk.Frame(
            terminal_container,
            bg=self.cores['bg_secundario'],
            relief='flat',
            highlightbackground=self.cores['neon_verde'],
            highlightthickness=1
        )
        terminal_wrapper.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Header do terminal
        terminal_header = tk.Frame(terminal_wrapper, bg=self.cores['bg_secundario'])
        terminal_header.pack(fill=tk.X, padx=10, pady=3)
        
        tk.Label(
            terminal_header,
            text="╔══ MATRIX TERMINAL ══",
            font=('Consolas', 9),
            fg=self.cores['neon_roxo'],
            bg=self.cores['bg_secundario']
        ).pack(side=tk.LEFT)
        
        self.status_dots = tk.Label(
            terminal_header,
            text="● ● ●",
            font=('Consolas', 9),
            fg=self.cores['neon_verde'],
            bg=self.cores['bg_secundario']
        )
        self.status_dots.pack(side=tk.RIGHT)
        
        # Terminal (sem a chuva, apenas texto)
        self.terminal = tk.Text(
            terminal_wrapper,
            bg='#000000',
            fg='#00ff41',
            font=('Consolas', 10),
            insertbackground='#00ff41',
            relief='flat',
            highlightthickness=0,
            borderwidth=0,
            wrap='word',
            state='normal',
            spacing1=1,
            spacing2=1,
            spacing3=1,
            height=10
        )
        self.terminal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tags de cores
        self.terminal.tag_config('INFO', foreground='#6bcfff')
        self.terminal.tag_config('SUCESSO', foreground='#6bffb8')
        self.terminal.tag_config('AVISO', foreground='#ffe66d')
        self.terminal.tag_config('ERRO', foreground='#ff6b6b')
        self.terminal.tag_config('CRITICO', foreground='#ff1744', font=('Consolas', 10, 'bold'))
        self.terminal.tag_config('DEBUG', foreground='#8888aa')
        self.terminal.tag_config('destaque', foreground='#ff6b9d', font=('Consolas', 10, 'bold'))
        
        # Mensagem inicial
        self._escrever_terminal("🚀 SISTEMA PRONTO. Clique em [INICIAR] para começar", 'INFO')
        self._escrever_terminal("💡 O terminal exibe todas as ações em tempo real", 'INFO')
        
    def _escrever_terminal(self, texto: str, nivel: str = 'INFO', destaque: bool = False):
        """Escreve no terminal com a cor apropriada"""
        try:
            self.terminal.config(state='normal')
            tag = 'destaque' if destaque else nivel
            self.terminal.insert('end', texto + '\n', tag)
            self.terminal.see('end')
            self.terminal.config(state='disabled')
        except Exception:
            pass
        
    def _criar_botoes(self, parent):
        """Cria os botões de controle"""
        btn_frame = tk.Frame(parent, bg=self.cores['bg'])
        btn_frame.pack(pady=6)
        
        btn_style = {
            'font': ('Consolas', 10, 'bold'),
            'bg': self.cores['bg_secundario'],
            'fg': self.cores['neon_verde'],
            'relief': tk.FLAT,
            'padx': 14,
            'pady': 7,
            'cursor': 'hand2',
            'borderwidth': 1,
            'highlightbackground': self.cores['bg_terciario'],
            'highlightthickness': 1,
            'activebackground': self.cores['bg_terciario'],
            'activeforeground': self.cores['neon_verde']
        }
        
        self.btn_iniciar = tk.Button(
            btn_frame, 
            text="▶ INICIAR VARREDURA", 
            command=self.iniciar_varredura,
            **btn_style
        )
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        
        self.btn_parar = tk.Button(
            btn_frame, 
            text="⏹ PARAR", 
            command=self.parar_varredura,
            state=tk.DISABLED,
            **btn_style
        )
        self.btn_parar.pack(side=tk.LEFT, padx=5)
        
        self.btn_deletar = tk.Button(
            btn_frame, 
            text="🗑 DELETAR SELECIONADOS", 
            command=self.deletar_selecionados,
            state=tk.DISABLED,
            **btn_style
        )
        self.btn_deletar.pack(side=tk.LEFT, padx=5)
        
        btn_diagnostico = tk.Button(
            btn_frame,
            text="📊 DIAGNÓSTICO",
            command=self.mostrar_diagnostico,
            **btn_style
        )
        btn_diagnostico.pack(side=tk.LEFT, padx=5)
        
    def _criar_resultados(self, parent):
        """Cria a tabela de resultados (OCUPA 30% DA TELA)"""
        self.result_frame = tk.Frame(parent, bg=self.cores['bg'])
        self.result_frame.pack(fill=tk.BOTH, expand=False, pady=(10, 0))
        
        header_frame = tk.Frame(self.result_frame, bg=self.cores['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.result_label = tk.Label(
            header_frame,
            text="📋 RESULTADOS ENCONTRADOS",
            font=('Consolas', 10, 'bold'),
            fg=self.cores['neon_amarelo'],
            bg=self.cores['bg']
        )
        self.result_label.pack(side=tk.LEFT)
        
        self.result_count = tk.Label(
            header_frame,
            text="(0)",
            font=('Consolas', 10),
            fg=self.cores['texto_escuro'],
            bg=self.cores['bg']
        )
        self.result_count.pack(side=tk.LEFT, padx=10)
        
        # Treeview estilizada
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Matrix.Treeview',
            background=self.cores['bg_secundario'],
            foreground=self.cores['texto'],
            fieldbackground=self.cores['bg_secundario'],
            borderwidth=0,
            font=('Consolas', 9)
        )
        
        style.configure('Matrix.Treeview.Heading',
            background=self.cores['bg_terciario'],
            foreground=self.cores['neon_azul'],
            borderwidth=0,
            font=('Consolas', 10, 'bold')
        )
        
        style.map('Matrix.Treeview',
            background=[('selected', self.cores['bg_terciario'])],
            foreground=[('selected', self.cores['texto'])]
        )
        
        tree_container = tk.Frame(self.result_frame, bg=self.cores['bg'])
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")
        
        columns = ('Tipo', 'Nome', 'Tamanho', 'Caminho')
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show='headings',
            height=5,
            style='Matrix.Treeview',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        self.tree.heading('Tipo', text='🔍 TIPO')
        self.tree.heading('Nome', text='📄 NOME')
        self.tree.heading('Tamanho', text='📦 TAMANHO')
        self.tree.heading('Caminho', text='📁 CAMINHO')
        
        self.tree.column('Tipo', width=100, anchor='w')
        self.tree.column('Nome', width=200, anchor='w')
        self.tree.column('Tamanho', width=100, anchor='e')
        self.tree.column('Caminho', width=400, anchor='w')
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree.bind("<Double-1>", self.abrir_caminho_selecionado)
        
    def _criar_status(self, parent):
        """Cria a barra de status"""
        status_frame = tk.Frame(parent, bg=self.cores['bg'])
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = tk.Label(
            status_frame,
            text="✅ SISTEMA PRONTO",
            font=('Consolas', 9),
            fg=self.cores['neon_verde'],
            bg=self.cores['bg'],
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT)
        
        tk.Label(
            status_frame,
            text="MISA-CLEANER v3.0 • Matrix Mode",
            font=('Consolas', 8),
            fg=self.cores['texto_escuro'],
            bg=self.cores['bg']
        ).pack(side=tk.RIGHT)

    # ============================================
    # 🌟 MATRIX RAIN - TELA CHEIA (SÓ A CHUVA!)
    # ============================================
    
    def _ativar_matrix(self):
        """🌟 ATIVA A CHUVA MATRIX EM TELA CHEIA"""
        # Remove a interface
        self.main_frame.pack_forget()
        
        # 🌟 CRIA APENAS A CHUVA
        self.matrix = MatrixRain(self.root)
        self.root.update()
        
    def _desativar_matrix(self):
        """🌟 DESATIVA A CHUVA E RESTAURA A INTERFACE"""
        if self.matrix:
            self.matrix.parar()
            self.matrix.destroy()
            self.matrix = None
        
        # Restaura a interface
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        self.main_frame.lift()
        self.root.update()
            
    # ===== LÓGICA DE INTERAÇÃO =====
    
    def adicionar_resultado_tabela(self, item: Dict):
        """Adiciona um resultado à tabela"""
        tipo = item.get('tipo', '').capitalize()
        nome = item.get('programa', '')
        if not nome:
            nome = os.path.basename(item.get('caminho', ''))
        tamanho = item.get('tamanho_mb', 0)
        caminho = item.get('caminho', '')
        
        icones = {
            'resquicio': '🔴',
            'obsoleto': '📂',
            'duplicado': '📎'
        }
        icone = icones.get(item.get('tipo', ''), '📄')
        
        self.tree.insert(
            "", "end",
            values=(f"{icone} {tipo}", nome, f"{tamanho:.1f} MB", caminho)
        )
        
        total = len(self.tree.get_children())
        self.result_count.config(text=f"({total})")
        
    def abrir_caminho_selecionado(self, event):
        """Abre o caminho selecionado no Explorer"""
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        caminho = item['values'][3]
        
        if not caminho or not os.path.exists(caminho):
            messagebox.showwarning(
                "Caminho não encontrado",
                f"O caminho não existe mais:\n{caminho}"
            )
            return
            
        try:
            if os.path.isfile(caminho):
                subprocess.Popen(['explorer', '/select,', caminho])
            else:
                subprocess.Popen(['explorer', caminho])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o caminho:\n{e}")
            
    def iniciar_varredura(self):
        """🌟 INICIA A VARREDURA COM MATRIX EM TELA CHEIA"""
        if self.varrendo:
            return
            
        # Limpar resultados
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.result_count.config(text="(0)")
        self.resultados = []
        
        # 🌟 ATIVA A CHUVA MATRIX (TELA CHEIA)
        self._ativar_matrix()
        
        self.varrendo = True
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_parar.config(state=tk.NORMAL)
        self.btn_deletar.config(state=tk.DISABLED)
        
        # Iniciar thread
        self.scanner_thread = threading.Thread(target=self._executar_varredura)
        self.scanner_thread.daemon = True
        self.scanner_thread.start()
        
    def _executar_varredura(self):
        """Executa a varredura (thread)"""
        try:
            resultados = self.scanner.escanear_tudo(
                callback_progresso=self._atualizar_progresso,
                callback_resultado=self._adicionar_resultado
            )
            
            self.resultados = (
                resultados.get('resquicios', []) +
                resultados.get('obsoletos', []) +
                resultados.get('duplicados', [])
            )
            
            self.root.after(0, self._finalizar_varredura)
            
        except Exception as e:
            self.logger.critico(f"💥 ERRO NA VARREDURA: {str(e)}")
            self.root.after(0, self._finalizar_varredura)
            
    def _atualizar_progresso(self, caminho: str):
        """Mantém o callback disponível sem poluir a interface durante a chuva."""
        return
            
    def _adicionar_resultado(self, item: Dict):
        """Adiciona resultado (callback da thread)"""
        self.root.after(0, lambda: self.adicionar_resultado_tabela(item))
        
    def _finalizar_varredura(self):
        """🌟 FINALIZA A VARREDURA E VOLTA PARA A INTERFACE"""
        self.varrendo = False
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_parar.config(state=tk.DISABLED)
        
        total = len(self.resultados)
        quantidade_resquicios = len(
            [item for item in self.resultados if item.get('tipo') == 'resquicio']
        )
        quantidade_obsoletos = len(
            [item for item in self.resultados if item.get('tipo') == 'obsoleto']
        )
        quantidade_duplicados = len(
            [item for item in self.resultados if item.get('tipo') == 'duplicado']
        )
        
        if total > 0:
            self.btn_deletar.config(state=tk.NORMAL)
            self.status_label.config(
                text=(
                    f"✅ VARREDURA CONCLUÍDA - {total} ITENS ENCONTRADOS "
                    f"(R:{quantidade_resquicios} O:{quantidade_obsoletos} "
                    f"D:{quantidade_duplicados})"
                ),
                fg=self.cores['neon_verde']
            )
        else:
            self.status_label.config(
                text="✅ VARREDURA CONCLUÍDA - SISTEMA LIMPO! NENHUM RESQUÍCIO ENCONTRADO",
                fg=self.cores['neon_verde']
            )
            
        self.result_count.config(text=f"({total})")
        
        # 🌟 DESATIVA A CHUVA MATRIX E RESTAURA A INTERFACE
        self._desativar_matrix()
        
        if total == 0:
            self.logger.sucesso("🧹 SISTEMA LIMPO! NENHUM ITEM ENCONTRADO.")
            
    def parar_varredura(self):
        """Para a varredura em andamento"""
        if not self.varrendo:
            return
            
        self.scanner.parar()
        self.status_label.config(
            text="⏹ VARREDURA INTERROMPIDA PELO USUÁRIO",
            fg=self.cores['neon_amarelo']
        )
        self.btn_parar.config(state=tk.DISABLED)
        self.varrendo = False
        
        # 🌟 DESATIVA A CHUVA MATRIX
        self._desativar_matrix()
        
    def deletar_selecionados(self):
        """Deleta todos os resquícios encontrados"""
        if not self.resultados:
            self.logger.aviso("⚠️ NENHUM RESQUÍCIO PARA DELETAR")
            return
            
        if not messagebox.askyesno(
            "Confirmar Exclusão",
            f"⚠️ Tem certeza que deseja deletar TODOS os {len(self.resultados)} itens encontrados?\n\n"
            "Esta ação não pode ser desfeita!"
        ):
            return
            
        deletados = 0
        erros = 0
        
        self.status_label.config(text="🗑 EXCLUINDO RESQUÍCIOS...", fg=self.cores['neon_amarelo'])
        self.btn_deletar.config(state=tk.DISABLED)
        
        for item in self.resultados:
            caminho = item.get('caminho', '')
            if not caminho:
                continue
                
            is_pasta = item.get('is_pasta', True)
            
            if is_pasta:
                success, msg = self.scanner.deletar_pasta(caminho)
            else:
                success, msg = self.scanner.deletar_arquivo(caminho)
                
            if success:
                deletados += 1
            else:
                erros += 1
                
        # Limpar resultados
        self.resultados = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.result_count.config(text="(0)")
        self.btn_deletar.config(state=tk.DISABLED)
        
        self.logger.sucesso("═" * 60)
        self.logger.sucesso(f"🗑 EXCLUSÃO CONCLUÍDA: {deletados} DELETADOS, {erros} ERROS")
        
        if erros > 0:
            self.status_label.config(
                text=f"⚠️ EXCLUSÃO CONCLUÍDA: {deletados} deletados, {erros} erros",
                fg=self.cores['neon_amarelo']
            )
        else:
            self.status_label.config(
                text=f"✅ EXCLUSÃO CONCLUÍDA: {deletados} resquícios deletados",
                fg=self.cores['neon_verde']
            )
            
    def mostrar_diagnostico(self):
        """Mostra diagnóstico completo da varredura"""
        resumo = self.logger.get_resumo()
        
        if resumo['total_logs'] == 0:
            messagebox.showinfo(
                "Diagnóstico",
                "Nenhuma varredura foi executada ainda.\n\n"
                "Clique em [INICIAR VARREDURA] para começar."
            )
            return
            
        diagnostico = self.logger.get_diagnostico()
        
        # Criar janela de diagnóstico
        diag_window = tk.Toplevel(self.root)
        diag_window.title("📊 Diagnóstico da Varredura")
        diag_window.geometry("700x500")
        diag_window.configure(bg=self.cores['bg'])
        diag_window.minsize(600, 400)
        
        diag_window.update_idletasks()
        x = (self.root.winfo_x() + self.root.winfo_width() // 2) - 350
        y = (self.root.winfo_y() + self.root.winfo_height() // 2) - 250
        diag_window.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(diag_window, bg=self.cores['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        tk.Label(
            main_frame,
            text="📊 DIAGNÓSTICO DA VARREDURA",
            font=('Consolas', 16, 'bold'),
            fg=self.cores['neon_verde'],
            bg=self.cores['bg']
        ).pack(pady=(0, 10))
        
        text_frame = tk.Frame(main_frame, bg=self.cores['bg'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, bg=self.cores['bg'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(
            text_frame,
            bg=self.cores['bg_secundario'],
            fg=self.cores['texto'],
            font=('Consolas', 10),
            relief='flat',
            highlightthickness=0,
            borderwidth=0,
            wrap='word',
            yscrollcommand=scrollbar.set
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        text_widget.insert('1.0', diagnostico)
        
        tk.Button(
            main_frame,
            text="FECHAR",
            command=diag_window.destroy,
            font=('Consolas', 10, 'bold'),
            bg=self.cores['bg_secundario'],
            fg=self.cores['neon_verde'],
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(pady=10)
        
    def fechar(self):
        """Fecha o programa com segurança"""
        if self.varrendo:
            if not messagebox.askyesno("Sair", "⚠️ Varredura em andamento. Deseja sair mesmo assim?"):
                return
            self.scanner.parar()
            
        # Desativa Matrix
        self._desativar_matrix()
            
        # Aguardar thread
        if self.scanner_thread and self.scanner_thread.is_alive():
            self.scanner_thread.join(timeout=1)
            
        self.root.quit()
        self.root.destroy()


def main():
    """Ponto de entrada principal"""
    root = tk.Tk()
    try:
        root.tk.call('tk', 'scaling', 1.5)
    except:
        pass
        
    app = MisaCleanerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()