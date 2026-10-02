"""
MISA-CLEANER - Interface Matrix Imersiva
VERSÃO 4.0 - Thread-safe, sem deleção, exportação de resultados

MUDANÇAS:
- _on_log usa root.after para thread-safety
- Botão "DELETAR SELECIONADOS" substituído por "ABRIR NO EXPLORER"
- Botão "EXPORTAR LISTA" para salvar resultados em .txt
- _atualizar_progresso atualiza status
- Removido main() duplicado
- Matrix Rain usa update_idletasks em vez de update
- Treeview mostra número de cópias
"""
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Optional

from logger import Logger, LogNivel
from matrix_rain import MatrixRain
from scanner import Scanner


class MisaCleanerUI:
    """Interface Principal do MISA-CLEANER"""

    def __init__(self, root: tk.Tk):
        self.root = root

        self.root.title("MISA-CLEANER - Resquicios Digitais")
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

        # Cores por nível de log (antes estavam no logger)
        self.cores_log = {
            LogNivel.INFO: '#6bcfff',
            LogNivel.SUCESSO: '#6bffb8',
            LogNivel.AVISO: '#ffe66d',
            LogNivel.ERRO: '#ff6b6b',
            LogNivel.CRITICO: '#ff1744',
            LogNivel.DEBUG: '#8888aa',
        }

        # Ícones por nível (antes estavam no logger)
        self.icones_log = {
            LogNivel.INFO: 'i',
            LogNivel.SUCESSO: 'OK',
            LogNivel.AVISO: '!',
            LogNivel.ERRO: 'X',
            LogNivel.CRITICO: '!!',
            LogNivel.DEBUG: '?',
        }

        self.logger = Logger(callback_ui=self._on_log)
        self.scanner = Scanner(self.logger)
        self.resultados: List[Dict] = []
        self.varrendo = False
        self.scanner_thread: Optional[threading.Thread] = None
        self.matrix: Optional[MatrixRain] = None

        self._setup_ui()

        self.root.protocol("WM_DELETE_WINDOW", self.fechar)

    def centralizar_janela(self):
        self.root.update_idletasks()
        largura = self.root.winfo_width()
        altura = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        self.root.geometry(f'{largura}x{altura}+{x}+{y}')

    # ============================================
    # LOG CALLBACK (THREAD-SAFE)
    # ============================================

    def _on_log(self, mensagem: str, nivel: str = LogNivel.INFO):
        """
        Callback do logger. Pode ser chamado da thread do scanner.
        NÃO mexe em widgets diretamente. Usa root.after.
        """
        # Agenda a escrita no terminal para a thread principal
        self.root.after(0, lambda m=mensagem, n=nivel: self._escrever_terminal_seguro(m, n))

    def _escrever_terminal_seguro(self, mensagem: str, nivel: str):
        """Escreve no terminal (chamado SEMPRE da thread principal)"""
        if not hasattr(self, 'terminal') or not self.terminal:
            return

        icone = self.icones_log.get(nivel, '')
        texto = f">> [{icone}] {mensagem}" if icone else f">> {mensagem}"

        destaque = nivel in [LogNivel.SUCESSO, LogNivel.CRITICO]
        tag = 'destaque' if destaque else nivel

        try:
            self.terminal.config(state='normal')
            self.terminal.insert('end', texto + '\n', tag)
            self.terminal.see('end')
            self.terminal.config(state='disabled')
        except Exception:
            pass

    # ============================================
    # CONSTRUÇÃO DA UI
    # ============================================

    def _setup_ui(self):
        self.main_frame = tk.Frame(self.root, bg=self.cores['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        self._criar_header(self.main_frame)
        self._criar_terminal(self.main_frame)
        self._criar_botoes(self.main_frame)
        self._criar_resultados(self.main_frame)
        self._criar_status(self.main_frame)

    def _criar_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.cores['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 8))

        accent = tk.Frame(header_frame, bg=self.cores['verde_matrix'], width=4)
        accent.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))

        intro = tk.Frame(header_frame, bg=self.cores['bg'])
        intro.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(intro, text="SYSTEM / SCAN CONSOLE",
                 font=('Consolas', 9, 'bold'),
                 fg=self.cores['neon_verde'],
                 bg=self.cores['bg']).pack(anchor=tk.W)

        tk.Label(intro, text="Digital residue detection",
                 font=('Consolas', 17, 'bold'),
                 fg=self.cores['texto'],
                 bg=self.cores['bg']).pack(anchor=tk.W, pady=(2, 0))

        tk.Label(intro, text="Three-layer analysis for files and duplicates",
                 font=('Consolas', 9),
                 fg=self.cores['texto_escuro'],
                 bg=self.cores['bg']).pack(anchor=tk.W, pady=(3, 0))

        status = tk.Frame(header_frame, bg=self.cores['bg_secundario'],
                         highlightbackground=self.cores['bg_terciario'],
                         highlightthickness=1, padx=14, pady=6)
        status.pack(side=tk.RIGHT, padx=(14, 0))

        status_line = tk.Frame(status, bg=self.cores['bg_secundario'])
        status_line.pack(anchor=tk.E)

        self.header_dot = tk.Label(status_line, text="*",
                                   font=('Consolas', 10),
                                   fg=self.cores['verde_matrix'],
                                   bg=self.cores['bg_secundario'])
        self.header_dot.pack(side=tk.LEFT, padx=(0, 6))

        self.header_status = tk.Label(status_line, text="READY",
                                      font=('Consolas', 9, 'bold'),
                                      fg=self.cores['neon_verde'],
                                      bg=self.cores['bg_secundario'])
        self.header_status.pack(side=tk.LEFT)

        tk.Label(status, text="3 LAYERS  /  SCAN ONLY",
                 font=('Consolas', 8),
                 fg=self.cores['texto_escuro'],
                 bg=self.cores['bg_secundario']).pack(anchor=tk.E, pady=(5, 0))

    def _criar_terminal(self, parent):
        terminal_container = tk.Frame(parent, bg=self.cores['bg'])
        terminal_container.pack(fill=tk.BOTH, expand=True, pady=6)

        terminal_wrapper = tk.Frame(terminal_container,
                                    bg=self.cores['bg_secundario'],
                                    relief='flat',
                                    highlightbackground=self.cores['neon_verde'],
                                    highlightthickness=1)
        terminal_wrapper.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        terminal_header = tk.Frame(terminal_wrapper, bg=self.cores['bg_secundario'])
        terminal_header.pack(fill=tk.X, padx=10, pady=3)

        tk.Label(terminal_header, text=" ",
                 font=('Consolas', 9),
                 fg=self.cores['neon_roxo'],
                 bg=self.cores['bg_secundario']).pack(side=tk.LEFT)

        tk.Label(terminal_header, text="* * *",
                 font=('Consolas', 9),
                 fg=self.cores['neon_verde'],
                 bg=self.cores['bg_secundario']).pack(side=tk.RIGHT)

        self.terminal = tk.Text(terminal_wrapper,
                                bg='#000000', fg='#00ff41',
                                font=('Consolas', 10),
                                insertbackground='#00ff41',
                                relief='flat', highlightthickness=0,
                                borderwidth=0, wrap='word',
                                state='normal',
                                spacing1=1, spacing2=1, spacing3=1,
                                height=10)
        self.terminal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.terminal.tag_config(LogNivel.INFO, foreground=self.cores_log[LogNivel.INFO])
        self.terminal.tag_config(LogNivel.SUCESSO, foreground=self.cores_log[LogNivel.SUCESSO])
        self.terminal.tag_config(LogNivel.AVISO, foreground=self.cores_log[LogNivel.AVISO])
        self.terminal.tag_config(LogNivel.ERRO, foreground=self.cores_log[LogNivel.ERRO])
        self.terminal.tag_config(LogNivel.CRITICO, foreground=self.cores_log[LogNivel.CRITICO],
                                 font=('Consolas', 10, 'bold'))
        self.terminal.tag_config(LogNivel.DEBUG, foreground=self.cores_log[LogNivel.DEBUG])
        self.terminal.tag_config('destaque', foreground=self.cores['neon_rosa'],
                                 font=('Consolas', 10, 'bold'))

        self._escrever_terminal_seguro("SISTEMA PRONTO. Clique em [INICIAR] para comecar", LogNivel.INFO)
        self._escrever_terminal_seguro("Esta ferramenta APENAS ENCONTRA itens. Voce decide o que fazer.", LogNivel.INFO)

    def _criar_botoes(self, parent):
        btn_frame = tk.Frame(parent, bg=self.cores['bg'])
        btn_frame.pack(pady=6)

        btn_style = {
            'font': ('Consolas', 10, 'bold'),
            'bg': self.cores['bg_secundario'],
            'fg': self.cores['neon_verde'],
            'relief': tk.FLAT,
            'padx': 14, 'pady': 7,
            'cursor': 'hand2',
            'borderwidth': 1,
            'highlightbackground': self.cores['bg_terciario'],
            'highlightthickness': 1,
            'activebackground': self.cores['bg_terciario'],
            'activeforeground': self.cores['neon_verde']
        }

        self.btn_iniciar = tk.Button(btn_frame, text="INICIAR VARREDURA",
                                     command=self.iniciar_varredura, **btn_style)
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)

        self.btn_parar = tk.Button(btn_frame, text="PARAR",
                                   command=self.parar_varredura,
                                   state=tk.DISABLED, **btn_style)
        self.btn_parar.pack(side=tk.LEFT, padx=5)

        self.btn_abrir = tk.Button(btn_frame, text="ABRIR NO EXPLORER",
                                   command=self.abrir_selecionado,
                                   state=tk.DISABLED, **btn_style)
        self.btn_abrir.pack(side=tk.LEFT, padx=5)

        self.btn_exportar = tk.Button(btn_frame, text="EXPORTAR LISTA",
                                      command=self.exportar_lista,
                                      state=tk.DISABLED, **btn_style)
        self.btn_exportar.pack(side=tk.LEFT, padx=5)

        btn_diagnostico = tk.Button(btn_frame, text="DIAGNOSTICO",
                                    command=self.mostrar_diagnostico, **btn_style)
        btn_diagnostico.pack(side=tk.LEFT, padx=5)

    def _criar_resultados(self, parent):
        self.result_frame = tk.Frame(parent, bg=self.cores['bg'])
        self.result_frame.pack(fill=tk.BOTH, expand=False, pady=(10, 0))

        header_frame = tk.Frame(self.result_frame, bg=self.cores['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 5))

        self.result_label = tk.Label(header_frame, text="RESULTADOS ENCONTRADOS",
                                     font=('Consolas', 10, 'bold'),
                                     fg=self.cores['neon_amarelo'],
                                     bg=self.cores['bg'])
        self.result_label.pack(side=tk.LEFT)

        self.result_count = tk.Label(header_frame, text="(0)",
                                     font=('Consolas', 10),
                                     fg=self.cores['texto_escuro'],
                                     bg=self.cores['bg'])
        self.result_count.pack(side=tk.LEFT, padx=10)

        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Matrix.Treeview',
                        background=self.cores['bg_secundario'],
                        foreground=self.cores['texto'],
                        fieldbackground=self.cores['bg_secundario'],
                        borderwidth=0,
                        font=('Consolas', 9))

        style.configure('Matrix.Treeview.Heading',
                        background=self.cores['bg_terciario'],
                        foreground=self.cores['neon_azul'],
                        borderwidth=0,
                        font=('Consolas', 10, 'bold'))

        style.map('Matrix.Treeview',
                  background=[('selected', self.cores['bg_terciario'])],
                  foreground=[('selected', self.cores['texto'])])

        tree_container = tk.Frame(self.result_frame, bg=self.cores['bg'])
        tree_container.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")

        columns = ('Tipo', 'Nome', 'Tamanho', 'Caminho')
        self.tree = ttk.Treeview(tree_container, columns=columns,
                                 show='headings', height=5,
                                 style='Matrix.Treeview',
                                 selectmode='extended',
                                 yscrollcommand=vsb.set,
                                 xscrollcommand=hsb.set)

        self.tree.heading('Tipo', text='TIPO')
        self.tree.heading('Nome', text='NOME')
        self.tree.heading('Tamanho', text='TAMANHO')
        self.tree.heading('Caminho', text='CAMINHO')

        self.tree.column('Tipo', width=100, anchor='w')
        self.tree.column('Nome', width=250, anchor='w')
        self.tree.column('Tamanho', width=100, anchor='e')
        self.tree.column('Caminho', width=400, anchor='w')

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", lambda e: self.abrir_selecionado())

    def _criar_status(self, parent):
        status_frame = tk.Frame(parent, bg=self.cores['bg'])
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = tk.Label(status_frame, text="SISTEMA PRONTO",
                                     font=('Consolas', 9),
                                     fg=self.cores['neon_verde'],
                                     bg=self.cores['bg'], anchor=tk.W)
        self.status_label.pack(side=tk.LEFT)

        tk.Label(status_frame, text="MISA-CLEANER v4.0  /  Scan Only",
                 font=('Consolas', 8),
                 fg=self.cores['texto_escuro'],
                 bg=self.cores['bg']).pack(side=tk.RIGHT)

    # ============================================
    # MATRIX RAIN
    # ============================================

    def _ativar_matrix(self):
        self.main_frame.pack_forget()
        self.matrix = MatrixRain(self.root)
        self.root.update_idletasks()

    def _desativar_matrix(self):
        if self.matrix:
            self.matrix.parar()
            self.matrix.destroy()
            self.matrix = None
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        self.main_frame.lift()
        self.root.update_idletasks()

    # ============================================
    # RESULTADOS
    # ============================================

    def adicionar_resultado_tabela(self, item: Dict):
        """Adiciona um resultado à tabela"""
        tipo = item.get('tipo', '').capitalize()
        nome = item.get('programa', '')
        if not nome:
            nome = os.path.basename(item.get('caminho', ''))

        # Para duplicados, indicar número de cópias
        if item.get('tipo') == 'duplicado':
            num = item.get('num_copias', len(item.get('arquivos', [])))
            if num > 1:
                nome = f"{nome}  ({num} copias)"

        # Usar tamanho_mb (agora duplicados também têm essa chave)
        tamanho = item.get('tamanho_mb', 0)
        caminho = item.get('caminho', '')

        icones = {'resquicio': '[R]', 'obsoleto': '[O]', 'duplicado': '[D]'}
        icone = icones.get(item.get('tipo', ''), '[?]')

        self.tree.insert("", "end",
                         values=(f"{icone} {tipo}", nome, f"{tamanho:.1f} MB", caminho))

        total = len(self.tree.get_children())
        self.result_count.config(text=f"({total})")

    def _item_dict_do_treeview(self, tree_item_id: str) -> Optional[Dict]:
        """Localiza o dict original correspondente a um item da Treeview"""
        valores = self.tree.item(tree_item_id)['values']
        if not valores:
            return None
        caminho = valores[3]
        for item in self.resultados:
            if item.get('caminho') == caminho:
                return item
        return None

    def abrir_selecionado(self):
        """Abre o caminho do item selecionado no Explorer"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Nenhum item",
                                "Selecione um item na tabela primeiro.")
            return

        # Abrir apenas o primeiro selecionado
        item_dict = self._item_dict_do_treeview(selected[0])
        if not item_dict:
            return

        caminho = item_dict.get('caminho', '')
        if not caminho or not os.path.exists(caminho):
            messagebox.showwarning("Caminho nao encontrado",
                                   f"O caminho nao existe mais:\n{caminho}")
            return

        import subprocess
        try:
            if os.path.isfile(caminho):
                subprocess.Popen(['explorer', '/select,', os.path.normpath(caminho)])
            else:
                subprocess.Popen(['explorer', os.path.normpath(caminho)])
        except Exception as e:
            messagebox.showerror("Erro", f"Nao foi possivel abrir:\n{e}")

    def exportar_lista(self):
        """Exporta a lista de resultados para um arquivo .txt"""
        if not self.resultados:
            messagebox.showinfo("Nada para exportar",
                                "Nenhum resultado para exportar.")
            return

        arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt")],
            initialfile=f"misa_cleaner_resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if not arquivo:
            return

        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("MISA-CLEANER - RESULTADOS DA VARREDURA\n")
                f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Total de itens: {len(self.resultados)}\n")
                f.write("=" * 70 + "\n\n")

                for i, item in enumerate(self.resultados, 1):
                    tipo = item.get('tipo', '').upper()
                    caminho = item.get('caminho', '')
                    tamanho = item.get('tamanho_mb', 0)

                    f.write(f"[{i}] {tipo}  ({tamanho:.1f} MB)\n")
                    f.write(f"    Caminho: {caminho}\n")

                    if tipo == 'DUPLICADO':
                        for arq in item.get('arquivos', []):
                            f.write(f"    - {arq}\n")

                    f.write("\n")

                f.write("=" * 70 + "\n")
                f.write("NOTA: Esta lista nao deleta nada. Voce decide o que fazer.\n")
                f.write("=" * 70 + "\n")

            self.logger.sucesso(f"Lista exportada: {arquivo}")
            messagebox.showinfo("Exportado",
                                f"Lista salva em:\n{arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Nao foi possivel exportar:\n{e}")

    # ============================================
    # VARREDURA
    # ============================================

    def iniciar_varredura(self):
        if self.varrendo:
            return

        for item in self.tree.get_children():
            self.tree.delete(item)
        self.result_count.config(text="(0)")
        self.resultados = []

        self._ativar_matrix()

        self.varrendo = True
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_parar.config(state=tk.NORMAL)
        self.btn_abrir.config(state=tk.DISABLED)
        self.btn_exportar.config(state=tk.DISABLED)

        self.scanner_thread = threading.Thread(target=self._executar_varredura)
        self.scanner_thread.daemon = True
        self.scanner_thread.start()

    def _executar_varredura(self):
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
            self.logger.critico(f"ERRO NA VARREDURA: {str(e)}")
            self.root.after(0, self._finalizar_varredura)

    def _atualizar_progresso(self, caminho: str):
        """Callback de progresso (chamado da thread do scanner)"""
        # Atualiza contador no status de forma thread-safe
        self.root.after(0, lambda: self.status_label.config(
            text=f"Verificados: {self.scanner.total_verificados} itens",
            fg=self.cores['neon_azul']
        ))

    def _adicionar_resultado(self, item: Dict):
        """Callback de resultado (chamado da thread do scanner)"""
        self.root.after(0, lambda: self.adicionar_resultado_tabela(item))

    def _finalizar_varredura(self):
        self.varrendo = False
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_parar.config(state=tk.DISABLED)

        total = len(self.resultados)

        if total > 0:
            self.btn_abrir.config(state=tk.NORMAL)
            self.btn_exportar.config(state=tk.NORMAL)

        qtd_r = len([i for i in self.resultados if i.get('tipo') == 'resquicio'])
        qtd_o = len([i for i in self.resultados if i.get('tipo') == 'obsoleto'])
        qtd_d = len([i for i in self.resultados if i.get('tipo') == 'duplicado'])

        if total > 0:
            self.status_label.config(
                text=f"VARREDURA CONCLUIDA - {total} itens (R:{qtd_r} O:{qtd_o} D:{qtd_d})",
                fg=self.cores['neon_verde']
            )
        else:
            self.status_label.config(
                text="VARREDURA CONCLUIDA - SISTEMA LIMPO",
                fg=self.cores['neon_verde']
            )

        self.result_count.config(text=f"({total})")

        self._desativar_matrix()

    def parar_varredura(self):
        if not self.varrendo:
            return
        self.scanner.parar()
        self.status_label.config(
            text="VARREDURA INTERROMPIDA PELO USUARIO",
            fg=self.cores['neon_amarelo']
        )
        self.btn_parar.config(state=tk.DISABLED)
        self.varrendo = False
        self._desativar_matrix()

    # ============================================
    # DIAGNÓSTICO
    # ============================================

    def mostrar_diagnostico(self):
        resumo = self.logger.get_resumo()

        if resumo['total_logs'] == 0:
            messagebox.showinfo("Diagnostico",
                                "Nenhuma varredura executada ainda.")
            return

        diagnostico = self.logger.get_diagnostico()

        diag_window = tk.Toplevel(self.root)
        diag_window.title("Diagnostico da Varredura")
        diag_window.geometry("700x500")
        diag_window.configure(bg=self.cores['bg'])
        diag_window.minsize(600, 400)

        diag_window.update_idletasks()
        x = (self.root.winfo_x() + self.root.winfo_width() // 2) - 350
        y = (self.root.winfo_y() + self.root.winfo_height() // 2) - 250
        diag_window.geometry(f"+{x}+{y}")

        main_frame = tk.Frame(diag_window, bg=self.cores['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        tk.Label(main_frame, text="DIAGNOSTICO DA VARREDURA",
                 font=('Consolas', 16, 'bold'),
                 fg=self.cores['neon_verde'],
                 bg=self.cores['bg']).pack(pady=(0, 10))

        text_frame = tk.Frame(main_frame, bg=self.cores['bg'])
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame, bg=self.cores['bg'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(text_frame,
                              bg=self.cores['bg_secundario'],
                              fg=self.cores['texto'],
                              font=('Consolas', 10),
                              relief='flat', highlightthickness=0,
                              borderwidth=0, wrap='word',
                              yscrollcommand=scrollbar.set)
        text_widget.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)

        text_widget.insert('1.0', diagnostico)

        tk.Button(main_frame, text="FECHAR",
                  command=diag_window.destroy,
                  font=('Consolas', 10, 'bold'),
                  bg=self.cores['bg_secundario'],
                  fg=self.cores['neon_verde'],
                  relief=tk.FLAT, padx=20, pady=8,
                  cursor='hand2').pack(pady=10)

    # ============================================
    # FECHAMENTO
    # ============================================

    def fechar(self):
        if self.varrendo:
            if not messagebox.askyesno("Sair",
                                       "Varredura em andamento. Sair mesmo assim?"):
                return
            self.scanner.parar()

        self._desativar_matrix()

        if self.scanner_thread and self.scanner_thread.is_alive():
            self.scanner_thread.join(timeout=1)

        self.root.quit()
        self.root.destroy()