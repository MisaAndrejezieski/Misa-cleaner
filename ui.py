import random
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scanner import Scanner

matplotlib.use('TkAgg')

class MatrixTerminal(tk.Text):
    """Widget que simula um terminal Matrix dentro da interface"""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Configurações do terminal Matrix
        self.config(
            bg='#000000',
            fg='#00ff41',
            font=('Consolas', 10),
            insertbackground='#00ff41',
            relief='flat',
            highlightthickness=0,
            borderwidth=0,
            wrap='word',
            state='disabled'
        )
        
        self.linhas_matrix = []
        self.animacao_ativa = False
        self.caracteres_matrix = ['日','本','語','の','文','字','を','使','っ','て','い','ま','す',
                                  '0','1','!','@','#','$','%','&','*','+','=','~','░','▒','▓']
        
    def escrever_matrix(self, texto, delay=0.02, cor='#00ff41'):
        """Escreve texto com efeito Matrix (digitação)"""
        self.config(state='normal')
        
        # Tags para cores
        self.tag_config('verde_matrix', foreground='#00ff41')
        self.tag_config('verde_claro', foreground='#33ff77')
        self.tag_config('verde_escuro', foreground='#009922')
        self.tag_config('amarelo', foreground='#ffff33')
        self.tag_config('vermelho', foreground='#ff3333')
        self.tag_config('azul', foreground='#33ccff')
        
        cor_tag = 'verde_matrix'
        if cor == 'verde_claro':
            cor_tag = 'verde_claro'
        elif cor == 'verde_escuro':
            cor_tag = 'verde_escuro'
        elif cor == 'amarelo':
            cor_tag = 'amarelo'
        elif cor == 'vermelho':
            cor_tag = 'vermelho'
        elif cor == 'azul':
            cor_tag = 'azul'
        
        # Efeito de digitação
        for char in texto:
            self.insert('end', char, cor_tag)
            self.see('end')
            self.update()
            time.sleep(delay)
        
        self.insert('end', '\n', cor_tag)
        self.see('end')
        self.config(state='disabled')
        self.update()
    
    def exibir_chuva_matrix(self, duracao=3):
        """Exibe a chuva de código Matrix dentro do terminal"""
        if self.animacao_ativa:
            return
        
        self.animacao_ativa = True
        self.config(state='normal')
        self.delete('1.0', 'end')
        
        # Salva o estado atual
        self.config(state='disabled')
        
        # Inicia a animação em uma thread separada
        def animar():
            inicio = time.time()
            largura = self.winfo_width() // 10
            if largura < 20:
                largura = 40
            
            linhas = 15
            
            while time.time() - inicio < duracao:
                self.config(state='normal')
                
                # Gera algumas linhas Matrix
                for _ in range(random.randint(2, 5)):
                    linha = ''.join(random.choice(self.caracteres_matrix) 
                                   for _ in range(random.randint(20, largura)))
                    cores = ['verde_matrix', 'verde_claro', 'verde_escuro']
                    cor = random.choice(cores)
                    
                    # Limpa uma linha aleatória para efeito de "queda"
                    if random.random() < 0.3:
                        pos = random.randint(0, self.count('1.0', 'end', 'lines')[0] - 2)
                        if pos > 0:
                            self.delete(f'{pos}.0', f'{pos+1}.0')
                    
                    self.insert('end', linha + '\n', cor)
                    
                    # Remove linhas antigas para não encher
                    if self.count('1.0', 'end', 'lines')[0] > linhas:
                        self.delete('1.0', '2.0')
                
                self.see('end')
                self.config(state='disabled')
                self.update()
                time.sleep(0.08)
            
            # Limpa e mostra a mensagem de prontidão
            self.config(state='normal')
            self.delete('1.0', 'end')
            self.insert('end', '>> SISTEMA PRONTO. AGUARDANDO COMANDOS...\n', 'verde_matrix')
            self.config(state='disabled')
            self.animacao_ativa = False
        
        thread = threading.Thread(target=animar)
        thread.daemon = True
        thread.start()
    
    def limpar(self):
        """Limpa o terminal"""
        self.config(state='normal')
        self.delete('1.0', 'end')
        self.config(state='disabled')


class MisaCleanerUI:
    def __init__(self, root):
        self.root = root
        
        # Configura a janela sem bordas padrão
        self.root.overrideredirect(True)  # Remove bordas padrão
        self.root.configure(bg='#0a0a0f')
        
        # Permite arrastar a janela
        self.root.bind('<Button-1>', self.iniciar_arraste)
        self.root.bind('<B1-Motion>', self.arrastar)
        self.root.bind('<ButtonRelease-1>', self.parar_arraste)
        
        # Tamanho da janela
        self.root.geometry("1200x800")
        
        # Centraliza a janela
        self.centralizar_janela()
        
        # Cores Neon Pastel
        self.cores = {
            'bg': '#0a0a0f',
            'bg_secundario': '#0f0f1a',
            'neon_rosa': '#ff6b9d',
            'neon_azul': '#6bcfff',
            'neon_roxo': '#b06bff',
            'neon_verde': '#6bffb8',
            'neon_amarelo': '#ffe66d',
            'pastel_rosa': '#ffb3c6',
            'pastel_azul': '#b3d9ff',
            'pastel_roxo': '#d4b3ff',
            'texto': '#e0e0ff',
            'verde_terminal': '#00ff41'
        }
        
        self.scanner = Scanner()
        self.resultados = []
        self.selecionados = set()
        self.varrendo = False
        
        # Bind para fechar com ESC
        self.root.bind('<Escape>', lambda e: self.fechar())
        
        self.setup_ui()
        
    def centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        largura = self.root.winfo_width()
        altura = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        self.root.geometry(f'{largura}x{altura}+{x}+{y}')
    
    def iniciar_arraste(self, event):
        self.x_inicio = event.x
        self.y_inicio = event.y
    
    def arrastar(self, event):
        x = self.root.winfo_x() + event.x - self.x_inicio
        y = self.root.winfo_y() + event.y - self.y_inicio
        self.root.geometry(f'+{x}+{y}')
    
    def parar_arraste(self, event):
        pass
    
    def fechar(self):
        """Fecha a aplicação"""
        if self.varrendo:
            if not messagebox.askyesno("Sair", "Varredura em andamento. Deseja sair mesmo assim?"):
                return
            self.scanner.parar()
        self.root.quit()
        self.root.destroy()
    
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.cores['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # ===== CABEÇALHO =====
        header_frame = tk.Frame(main_frame, bg=self.cores['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título ASCII Art com efeito neon
        titulo = tk.Label(
            header_frame,
            text="""
╔══════════════════════════════════════════════════════════════╗
║  ███╗   ███╗██╗███████╗ █████╗     ██████╗██╗              ║
║  ████╗ ████║██║██╔════╝██╔══██╗   ██╔════╝██║              ║
║  ██╔████╔██║██║███████╗███████║   ██║     ██║              ║
║  ██║╚██╔╝██║██║╚════██║██╔══██║   ██║     ██║              ║
║  ██║ ╚═╝ ██║██║███████║██║  ██║   ╚██████╗███████╗         ║
║  ╚═╝     ╚═╝╚═╝╚══════╝╚═╝  ╚═╝    ╚═════╝╚══════╝         ║
║        ── Caçador de Resquícios Digitais ──                 ║
╚══════════════════════════════════════════════════════════════╝
""",
            font=('Consolas', 8),
            fg=self.cores['neon_azul'],
            bg=self.cores['bg'],
            justify=tk.CENTER
        )
        titulo.pack()
        
        # ===== BOTÕES =====
        btn_frame = tk.Frame(main_frame, bg=self.cores['bg'])
        btn_frame.pack(pady=(0, 10))
        
        # Estilo dos botões
        btn_style = {
            'font': ('Consolas', 10, 'bold'),
            'bg': self.cores['bg'],
            'fg': self.cores['neon_verde'],
            'relief': tk.FLAT,
            'padx': 20,
            'pady': 8,
            'cursor': 'hand2',
            'borderwidth': 0
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
        
        # ===== TERMINAL MATRIX =====
        terminal_frame = tk.Frame(main_frame, bg=self.cores['bg'])
        terminal_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Label do terminal
        terminal_label = tk.Label(
            terminal_frame,
            text="╔══════════ TERMINAL MATRIX ══════════╗",
            font=('Consolas', 8),
            fg=self.cores['neon_roxo'],
            bg=self.cores['bg']
        )
        terminal_label.pack(anchor=tk.W)
        
        # O terminal Matrix
        self.terminal = MatrixTerminal(
            terminal_frame,
            height=12
        )
        self.terminal.pack(fill=tk.BOTH, expand=True)
        
        # Exibe a chuva Matrix ao iniciar
        self.terminal.exibir_chuva_matrix(duracao=3)
        
        # ===== PROGRESS BAR =====
        progress_frame = tk.Frame(main_frame, bg=self.cores['bg'])
        progress_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=200,
            style='Matrix.Horizontal.TProgressbar'
        )
        
        # Estilo da progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Matrix.Horizontal.TProgressbar',
                       background='#00ff41',
                       troughcolor='#0a0a0f',
                       bordercolor='#0a0a0f',
                       lightcolor='#00ff41',
                       darkcolor='#00cc33')
        
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # ===== STATUS =====
        self.status_label = tk.Label(
            main_frame,
            text="SISTEMA PRONTO. DIGITE 'INICIAR' PARA COMEÇAR",
            font=('Consolas', 9),
            fg=self.cores['neon_verde'],
            bg=self.cores['bg'],
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, pady=(5, 0))
        
        # ===== BOTÃO FECHAR (custom) =====
        close_frame = tk.Frame(main_frame, bg=self.cores['bg'])
        close_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            close_frame,
            text="✕ FECHAR",
            command=self.fechar,
            font=('Consolas', 9),
            bg=self.cores['bg'],
            fg=self.cores['neon_rosa'],
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.RIGHT)
    
    def adicionar_log(self, mensagem, cor='verde_matrix'):
        """Adiciona mensagem ao terminal Matrix"""
        self.terminal.escrever_matrix(mensagem, delay=0.01, cor=cor)
    
    def iniciar_varredura(self):
        if self.varrendo:
            return
        
        self.varrendo = True
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_parar.config(state=tk.NORMAL)
        self.progress_var.set(0)
        
        self.adicionar_log(">> INICIANDO PROTOCOLO MISA-CLEANER...", 'verde_matrix')
        self.adicionar_log(">> ATIVANDO 3 CAMADAS DE ANÁLISE:", 'azul')
        self.adicionar_log("   1. RESQUÍCIOS DE PROGRAMAS DELETADOS", 'verde_claro')
        self.adicionar_log("   2. ARQUIVOS OBSOLETOS", 'verde_claro')
        self.adicionar_log("   3. ARQUIVOS DUPLICADOS", 'verde_claro')
        self.adicionar_log("")
        
        self.status_label.config(text="VARRENDO SISTEMA...")
        
        # Inicia em thread separada
        thread = threading.Thread(target=self.executar_varredura)
        thread.daemon = True
        thread.start()
    
    def executar_varredura(self):
        try:
            resultados = self.scanner.escanear_tudo(
                callback_progresso=self.atualizar_progresso,
                callback_resultado=self.adicionar_resultado
            )
            
            self.resultados = (
                resultados.get('resquicios', []) +
                resultados.get('obsoletos', []) +
                resultados.get('duplicados', [])
            )
            
            self.root.after(0, self.finalizar_varredura)
            
        except Exception as e:
            self.root.after(0, lambda: self.adicionar_log(f">> ERRO: {str(e)}", 'vermelho'))
            self.root.after(0, self.finalizar_varredura)
    
    def atualizar_progresso(self, caminho):
        """Atualiza a barra de progresso e mostra no terminal"""
        # Atualiza progresso (simulado)
        progresso_atual = self.progress_var.get()
        if progresso_atual < 95:
            self.root.after(0, lambda: self.progress_var.set(progresso_atual + 0.5))
        
        # Mostra no terminal
        self.root.after(0, lambda: self.adicionar_log(f"   🟢 {caminho[:60]}...", 'verde_escuro'))
    
    def adicionar_resultado(self, item):
        """Adiciona um resultado encontrado"""
        tipo = item.get('tipo', '')
        caminho = item.get('caminho', '')
        tamanho = item.get('tamanho_mb', 0)
        programa = item.get('programa', '')
        
        if tipo == 'resquicio':
            mensagem = f"   🔍 RESQUÍCIO: {programa} - {caminho} ({tamanho:.1f} MB)"
            cor = 'amarelo'
        elif tipo == 'obsoleto':
            mensagem = f"   📂 OBSOLETO: {caminho} ({tamanho:.1f} MB)"
            cor = 'verde_claro'
        elif tipo == 'duplicado':
            mensagem = f"   📎 DUPLICADO: {caminho} ({tamanho:.1f} MB)"
            cor = 'azul'
        else:
            mensagem = f"   📄 ENCONTRADO: {caminho} ({tamanho:.1f} MB)"
            cor = 'verde_matrix'
        
        self.root.after(0, lambda: self.adicionar_log(mensagem, cor))
    
    def finalizar_varredura(self):
        self.varrendo = False
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_parar.config(state=tk.DISABLED)
        self.progress_var.set(100)
        
        total = len(self.resultados)
        self.status_label.config(text=f"✅ VARREDURA CONCLUÍDA - {total} RESQUÍCIOS ENCONTRADOS")
        self.adicionar_log("")
        self.adicionar_log(f">> VARREDURA CONCLUÍDA! {total} RESQUÍCIOS ENCONTRADOS.", 'verde_matrix')
        
        if total == 0:
            self.adicionar_log(">> SISTEMA LIMPO. NENHUM FANTASMA DIGITAL ENCONTRADO.", 'verde_claro')
    
    def parar_varredura(self):
        self.scanner.parar()
        self.adicionar_log(">> PARANDO VARREDURA...", 'amarelo')
        self.status_label.config(text="⏹ VARREDURA INTERROMPIDA")
        self.btn_parar.config(state=tk.DISABLED)
        self.varrendo = False
    
    def deletar_selecionados(self):
        # Simula deleção (não temos lista para selecionar no terminal)
        if not self.resultados:
            self.adicionar_log(">> NENHUM RESQUÍCIO PARA DELETAR.", 'amarelo')
            return
        
        if not messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja deletar TODOS os {len(self.resultados)} resquícios encontrados?"
        ):
            return
        
        deletados = 0
        for item in self.resultados[:10]:  # Limita a 10 para teste
            caminho = item.get('caminho', '')
            success, msg = self.scanner.deletar_pasta(caminho)
            if success:
                deletados += 1
                self.adicionar_log(f"   🗑 DELETADO: {caminho}", 'verde_claro')
            else:
                self.adicionar_log(f"   ❌ ERRO: {msg}", 'vermelho')
        
        self.adicionar_log(f">> {deletados} RESQUÍCIOS DELETADOS.", 'verde_matrix')


def main():
    root = tk.Tk()
    app = MisaCleanerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()