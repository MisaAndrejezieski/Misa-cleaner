import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, scrolledtext, ttk

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scanner import Scanner

matplotlib.use('TkAgg')  # Garante compatibilidade com Tkinter

import os

class MisaCleanerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Misa-cleaner")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        
        # Modo atual (padrão: escuro)
        self.modo_escuro = True
        
        # Paleta de cores neon pastel (modo escuro)
        self.cores_escuro = {
            'bg': '#1a1a2e',           # Azul escuro profundo
            'frame': '#16213e',        # Azul marinho
            'primary': '#e8a87c',      # Pêssego pastel
            'secondary': '#c38d9e',    # Rosa pastel
            'accent': '#85cdca',       # Turquesa pastel
            'text': '#f5e6cc',         # Creme
            'success': '#a8e6cf',      # Verde menta pastel
            'danger': '#f8a5c2',       # Rosa choque pastel
            'warning': '#f7dc6f',      # Amarelo pastel
            'chart_bg': '#2d2d44',     # Fundo do gráfico
            'log_bg': '#0f0f1a',       # Fundo do log
        }
        
        # Paleta de cores neon pastel (modo claro)
        self.cores_claro = {
            'bg': '#f5f0eb',           # Bege claro
            'frame': '#e8e0d8',        # Bege médio
            'primary': '#d4816e',      # Terracota pastel
            'secondary': '#b5828a',    # Rosa suave
            'accent': '#6ba3a0',       # Turquesa suave
            'text': '#2d2d2d',         # Cinza escuro
            'success': '#7cb342',      # Verde suave
            'danger': '#e57373',       # Vermelho suave
            'warning': '#f9a825',      # Amarelo suave
            'chart_bg': '#f5f0eb',     # Fundo do gráfico
            'log_bg': '#ffffff',       # Fundo do log
        }
        
        self.cores = self.cores_escuro
        self.scanner = Scanner()
        self.resultados = []
        self.varredura_ativa = False
        
        self._configurar_estilos()
        self._criar_interface()
        
    def _configurar_estilos(self):
        self.root.configure(bg=self.cores['bg'])
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background=self.cores['bg'])
        style.configure('TLabel', background=self.cores['bg'], foreground=self.cores['text'], font=('Segoe UI', 10))
        style.configure('TButton', background=self.cores['primary'], foreground=self.cores['bg'], 
                       font=('Segoe UI', 10, 'bold'), borderwidth=0, padding=10)
        style.map('TButton', 
                 background=[('active', self.cores['secondary'])],
                 foreground=[('active', self.cores['bg'])])
        
        style.configure('Accent.TButton', background=self.cores['accent'])
        style.map('Accent.TButton', 
                 background=[('active', self.cores['success'])])
        
        style.configure('Danger.TButton', background=self.cores['danger'])
        style.map('Danger.TButton', 
                 background=[('active', '#ff6b6b')])
        
    def _criar_interface(self):
        # Cabeçalho
        header_frame = tk.Frame(self.root, bg=self.cores['bg'])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        titulo = tk.Label(header_frame, text="✨ Misa-cleaner", 
                         font=('Segoe UI', 28, 'bold'), 
                         bg=self.cores['bg'], fg=self.cores['primary'])
        titulo.pack(side='left')
        
        # Botão de alternar tema
        self.btn_tema = ttk.Button(header_frame, text="🌙 Modo Escuro", 
                                  command=self.alternar_tema, style='TButton')
        self.btn_tema.pack(side='right', padx=10)
        
        subtitulo = tk.Label(header_frame, text="Encontre e remova pastas obsoletas com mais de 1 ano de inatividade",
                            font=('Segoe UI', 12), bg=self.cores['bg'], fg=self.cores['text'])
        subtitulo.pack(fill='x', pady=5)
        
        # Frame principal (dividido em 2 colunas)
        main_frame = tk.Frame(self.root, bg=self.cores['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Coluna esquerda (controles + tabela)
        left_frame = tk.Frame(main_frame, bg=self.cores['bg'])
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Controles
        controls_frame = tk.Frame(left_frame, bg=self.cores['bg'])
        controls_frame.pack(fill='x', pady=10)
        
        self.btn_escanear = ttk.Button(controls_frame, text="🔍 Iniciar Varredura", 
                                      command=self.iniciar_varredura, style='TButton')
        self.btn_escanear.pack(side='left', padx=5)
        
        self.btn_parar = ttk.Button(controls_frame, text="⏹️ Parar", 
                                   command=self.parar_varredura, style='TButton')
        self.btn_parar.pack(side='left', padx=5)
        self.btn_parar.config(state='disabled')
        
        self.btn_deletar = ttk.Button(controls_frame, text="🗑️ Deletar Selecionados", 
                                     command=self.deletar_selecionados, style='Danger.TButton')
        self.btn_deletar.pack(side='left', padx=5)
        self.btn_deletar.config(state='disabled')
        
        # Progresso
        progress_frame = tk.Frame(left_frame, bg=self.cores['bg'])
        progress_frame.pack(fill='x', pady=10)
        
        self.lbl_progresso = tk.Label(progress_frame, text="Pronto para escanear",
                                     bg=self.cores['bg'], fg=self.cores['text'],
                                     font=('Segoe UI', 9))
        self.lbl_progresso.pack(side='left')
        
        self.progress = ttk.Progressbar(progress_frame, length=400, mode='indeterminate')
        self.progress.pack(side='right')
        
        # Tabela de resultados
        table_frame = tk.Frame(left_frame, bg=self.cores['bg'])
        table_frame.pack(fill='both', expand=True, pady=10)
        
        columns = ('Caminho', 'Tamanho (MB)', 'Último Acesso')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'Caminho':
                self.tree.column(col, width=500)
            else:
                self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Coluna direita (gráfico + log)
        right_frame = tk.Frame(main_frame, bg=self.cores['bg'])
        right_frame.pack(side='right', fill='y', padx=(10, 0))
        
        # Gráfico de pizza
        chart_frame = tk.Frame(right_frame, bg=self.cores['bg'])
        chart_frame.pack(fill='both', expand=True, pady=10)
        
        tk.Label(chart_frame, text="📊 Top 5 Maiores Pastas", 
                bg=self.cores['bg'], fg=self.cores['text'],
                font=('Segoe UI', 11, 'bold')).pack()
        
        self.fig, self.ax = plt.subplots(figsize=(5, 4), facecolor=self.cores['chart_bg'])
        self.fig.patch.set_facecolor(self.cores['chart_bg'])
        self.ax.set_facecolor(self.cores['chart_bg'])
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, pady=5)
        
        # Área de log
        log_frame = tk.Frame(right_frame, bg=self.cores['bg'])
        log_frame.pack(fill='x', pady=10)
        
        tk.Label(log_frame, text="📋 Log:", bg=self.cores['bg'], fg=self.cores['text']).pack(anchor='w')
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=6, wrap='word',
                                                 bg=self.cores['log_bg'], fg=self.cores['text'],
                                                 font=('Consolas', 9), insertbackground=self.cores['text'])
        self.log_area.pack(fill='x')
        
    def alternar_tema(self):
        """Alterna entre modo escuro e claro"""
        self.modo_escuro = not self.modo_escuro
        self.cores = self.cores_escuro if self.modo_escuro else self.cores_claro
        
        # Atualiza botão
        if self.modo_escuro:
            self.btn_tema.config(text="🌙 Modo Escuro")
        else:
            self.btn_tema.config(text="☀️ Modo Claro")
        
        # Reaplica estilos
        self._configurar_estilos()
        self.root.configure(bg=self.cores['bg'])
        
        # Atualiza widgets
        for widget in self.root.winfo_children():
            self._atualizar_cores_widget(widget)
        
        # Atualiza gráfico
        self.atualizar_grafico(self.resultados)
        
    def _atualizar_cores_widget(self, widget):
        """Recursivamente atualiza cores dos widgets"""
        try:
            if isinstance(widget, (tk.Frame, tk.LabelFrame)):
                widget.configure(bg=self.cores['bg'])
            elif isinstance(widget, tk.Label):
                widget.configure(bg=self.cores['bg'], fg=self.cores['text'])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=self.cores['primary'], fg=self.cores['bg'])
            elif isinstance(widget, scrolledtext.ScrolledText):
                widget.configure(bg=self.cores['log_bg'], fg=self.cores['text'])
            
            # Recurse
            for child in widget.winfo_children():
                self._atualizar_cores_widget(child)
        except:
            pass
        
        # Atualiza gráfico
        self.fig.patch.set_facecolor(self.cores['chart_bg'])
        self.ax.set_facecolor(self.cores['chart_bg'])
        self.canvas.draw()
        
    def log(self, mensagem, tipo='info'):
        """Adiciona mensagem ao log com formatação"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        cores = {
            'info': self.cores['accent'],
            'warning': self.cores['warning'],
            'success': self.cores['success'],
            'error': self.cores['danger']
        }
        
        cor = cores.get(tipo, self.cores['text'])
        self.log_area.insert('end', f"[{timestamp}] ", 'timestamp')
        self.log_area.insert('end', mensagem + '\n', f'{tipo}_msg')
        
        self.log_area.tag_config('timestamp', foreground=self.cores['secondary'])
        self.log_area.tag_config('info_msg', foreground=cor)
        self.log_area.tag_config('warning_msg', foreground=cor)
        self.log_area.tag_config('success_msg', foreground=cor)
        self.log_area.tag_config('error_msg', foreground=cor)
        
        self.log_area.see('end')
        self.root.update_idletasks()
        
    def atualizar_progresso(self, caminho):
        if not self.varredura_ativa:
            return
        self.lbl_progresso.config(text=f"Escaneando: {caminho[:60]}...")
        self.root.update_idletasks()
        
    def adicionar_resultado(self, resultado):
        self.resultados.append(resultado)
        tamanho_str = f"{resultado['tamanho_mb']:.1f}"
        ultimo_acesso = resultado['ultimo_acesso'].strftime("%d/%m/%Y %H:%M")
        
        self.tree.insert('', 'end', values=(
            resultado['caminho'],
            tamanho_str,
            ultimo_acesso
        ))
        
        self.log(f"📂 Encontrado: {resultado['caminho']} ({tamanho_str} MB)", 'warning')
        
        # Atualiza gráfico a cada 10 resultados
        if len(self.resultados) % 10 == 0:
            self.atualizar_grafico(self.resultados)
        
    def atualizar_grafico(self, resultados):
        """Atualiza o gráfico de pizza com os 5 maiores"""
        self.ax.clear()
        
        if not resultados:
            self.ax.text(0.5, 0.5, "Nenhum dado ainda", 
                        ha='center', va='center', fontsize=12,
                        color=self.cores['text'])
            self.canvas.draw()
            return
            
        # Pega os 5 maiores
        top5 = sorted(resultados, key=lambda x: x['tamanho_mb'], reverse=True)[:5]
        
        labels = [os.path.basename(r['caminho']) for r in top5]
        sizes = [r['tamanho_mb'] for r in top5]
        
        # Cores pastel para o gráfico
        cores_pizza = ['#e8a87c', '#c38d9e', '#85cdca', '#f7dc6f', '#a8e6cf']
        
        self.ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                   colors=cores_pizza, startangle=90,
                   textprops={'color': self.cores['text']})
        self.ax.axis('equal')
        self.canvas.draw()
        
    def iniciar_varredura(self):
        if self.varredura_ativa:
            return
            
        self.varredura_ativa = True
        self.resultados = []
        self.tree.delete(*self.tree.get_children())
        self.log_area.delete('1.0', 'end')
        self.ax.clear()
        self.canvas.draw()
        
        self.btn_escanear.config(state='disabled')
        self.btn_parar.config(state='normal')
        self.btn_deletar.config(state='disabled')
        self.progress.start(10)
        
        self.log("🚀 Iniciando varredura completa do sistema...", 'info')
        
        thread = threading.Thread(target=self._executar_varredura, daemon=True)
        thread.start()
        
    def _executar_varredura(self):
        try:
            self.scanner.escanear_tudo(
                callback_progresso=self.atualizar_progresso,
                callback_resultado=self.adicionar_resultado
            )
        except Exception as e:
            self.log(f"❌ Erro durante a varredura: {e}", 'error')
        finally:
            self.finalizar_varredura()
            
    def parar_varredura(self):
        self.scanner.parar()
        self.log("⏹️ Varredura interrompida pelo usuário", 'warning')
        self.finalizar_varredura()
        
    def finalizar_varredura(self):
        self.varredura_ativa = False
        self.progress.stop()
        self.btn_escanear.config(state='normal')
        self.btn_parar.config(state='disabled')
        self.lbl_progresso.config(text="Varredura concluída")
        
        if self.resultados:
            self.btn_deletar.config(state='normal')
            self.log(f"✅ Varredura concluída! {len(self.resultados)} pastas obsoletas encontradas.", 'success')
            self.atualizar_grafico(self.resultados)
        else:
            self.log("🎉 Nenhuma pasta obsoleta encontrada! Seu sistema está limpo.", 'success')
            
    def deletar_selecionados(self):
        selecionados = self.tree.selection()
        if not selecionados:
            messagebox.showwarning("Nada selecionado", "Selecione pelo menos uma pasta para deletar.")
            return
            
        confirm = messagebox.askyesno("Confirmar exclusão", 
                                     f"Tem certeza que deseja deletar {len(selecionados)} pasta(s) selecionada(s)?\n\nEsta ação é IRREVERSÍVEL!")
        if not confirm:
            return
            
        deletados = 0
        erros = 0
        
        for item in selecionados:
            valores = self.tree.item(item)['values']
            caminho = valores[0]
            
            sucesso, mensagem = self.scanner.deletar_pasta(caminho)
            if sucesso:
                self.tree.delete(item)
                self.log(mensagem, 'success')
                deletados += 1
                # Remove dos resultados para atualizar gráfico
                self.resultados = [r for r in self.resultados if r['caminho'] != caminho]
            else:
                self.log(mensagem, 'error')
                erros += 1
                
        messagebox.showinfo("Resultado", 
                           f"✅ {deletados} pasta(s) deletada(s) com sucesso.\n"
                           f"❌ {erros} erro(s) encontrado(s).\n\n"
                           f"Os erros foram registrados no log.")
        
        self.atualizar_grafico(self.resultados)
        
        if not self.tree.get_children():
            self.btn_deletar.config(state='disabled')