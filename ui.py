import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from scanner import Scanner


class MisaCleanerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Misa-cleaner")
        self.root.geometry("950x650")
        self.root.minsize(900, 600)
        
        # Cores Matrix
        self.cores = {
            'bg': '#000000',
            'frame': '#000000',
            'primary': '#00ff41',
            'secondary': '#008f11',
            'text': '#00ff41',
            'danger': '#ff0000',
            'warning': '#ffff00',
            'log_bg': '#000000',
            'tree_bg': '#000000',     # Fundo da tabela preto
            'tree_fg': '#00ff41',     # Texto da tabela verde
            'tree_sel_bg': '#00ff41', # Selecionado verde
            'tree_sel_fg': '#000000', # Texto selecionado preto
        }
        
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
        style.configure('TLabel', background=self.cores['bg'], foreground=self.cores['text'], font=('Consolas', 10))
        
        # Botões Matrix
        style.configure('TButton', background=self.cores['bg'], foreground=self.cores['primary'], 
                       font=('Consolas', 10, 'bold'), borderwidth=2, padding=8, relief='ridge')
        style.map('TButton', 
                 background=[('active', self.cores['primary'])],
                 foreground=[('active', self.cores['bg'])])
        
        style.configure('Danger.TButton', background=self.cores['bg'], foreground=self.cores['danger'])
        style.map('Danger.TButton', 
                 background=[('active', self.cores['danger'])],
                 foreground=[('active', self.cores['bg'])])
        
        # Estilo da Treeview (Tabela) - PARA FICAR BONITA
        style.configure("Treeview", 
                        background=self.cores['tree_bg'], 
                        foreground=self.cores['tree_fg'], 
                        fieldbackground=self.cores['tree_bg'],
                        font=('Consolas', 10),
                        rowheight=25,
                        borderwidth=0)
        style.configure("Treeview.Heading", 
                        background=self.cores['bg'], 
                        foreground=self.cores['primary'], 
                        font=('Consolas', 10, 'bold'),
                        relief='flat')
        style.map("Treeview", 
                  background=[('selected', self.cores['tree_sel_bg'])],
                  foreground=[('selected', self.cores['tree_sel_fg'])])
        
    def _criar_interface(self):
        header = tk.Frame(self.root, bg=self.cores['bg'])
        header.pack(fill='x', padx=20, pady=15)
        tk.Label(header, text="MISA-CLEANER", font=('Consolas', 22, 'bold'), 
                bg=self.cores['bg'], fg=self.cores['primary']).pack()
        
        main = tk.Frame(self.root, bg=self.cores['bg'])
        main.pack(fill='both', expand=True, padx=20, pady=10)
        
        controls = tk.Frame(main, bg=self.cores['bg'])
        controls.pack(fill='x', pady=10)
        
        self.btn_escanear = ttk.Button(controls, text="> INICIAR VARREDURA", command=self.iniciar_varredura)
        self.btn_escanear.pack(side='left', padx=5)
        
        self.btn_parar = ttk.Button(controls, text="> PARAR", command=self.parar_varredura, style='Danger.TButton')
        self.btn_parar.pack(side='left', padx=5)
        self.btn_parar.config(state='disabled')
        
        self.btn_deletar = ttk.Button(controls, text="> DELETAR SELECIONADOS", command=self.deletar_selecionados, style='Danger.TButton')
        self.btn_deletar.pack(side='left', padx=5)
        self.btn_deletar.config(state='disabled')
        
        # Área de Log Matrix
        log_frame = tk.Frame(main, bg=self.cores['bg'])
        log_frame.pack(fill='x', pady=5)
        
        self.log_area = tk.Text(log_frame, height=6, wrap='word', 
                                bg=self.cores['log_bg'], fg=self.cores['text'], 
                                font=('Consolas', 9), relief='sunken', borderwidth=2)
        self.log_area.pack(fill='x')
        self.log_area.insert('end', ">> SISTEMA PRONTO.\n")
        
        # Tabela Matrix (Treeview)
        table_frame = tk.Frame(main, bg=self.cores['bg'])
        table_frame.pack(fill='both', expand=True, pady=5)
        
        columns = ('Caminho', 'Tamanho (MB)', 'Último Acesso')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'Caminho':
                self.tree.column(col, width=500)
            else:
                self.tree.column(col, width=150)
        
        # Estilo da barra de rolagem para ficar verde
        scrollbar = tk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview, 
                                 bg=self.cores['bg'], troughcolor=self.cores['bg'],
                                 activebackground=self.cores['primary'], 
                                 highlightbackground=self.cores['primary'])
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def log(self, mensagem, tipo='info'):
        cor = {'info': self.cores['text'], 'warning': self.cores['warning'], 'success': self.cores['text'], 'error': self.cores['danger']}.get(tipo, self.cores['text'])
        self.log_area.insert('end', f">> {mensagem}\n", tipo)
        self.log_area.tag_config('info', foreground=self.cores['text'])
        self.log_area.tag_config('warning', foreground=self.cores['warning'])
        self.log_area.tag_config('success', foreground=self.cores['text'])
        self.log_area.tag_config('error', foreground=self.cores['danger'])
        self.log_area.see('end')
        self.root.update_idletasks()
        
    def iniciar_varredura(self):
        if self.varredura_ativa: return
        self.varredura_ativa = True
        self.resultados = []
        self.tree.delete(*self.tree.get_children())
        self.log_area.delete('1.0', 'end')
        
        self.log("INICIANDO VARREDURA...", 'info')
        self.btn_escanear.config(state='disabled')
        self.btn_parar.config(state='normal')
        self.btn_deletar.config(state='disabled')
        
        thread = threading.Thread(target=self._executar_varredura, daemon=True)
        thread.start()
        
    def _executar_varredura(self):
        try:
            self.scanner.escanear(
                callback_progresso=self.atualizar_progresso,
                callback_resultado=self.adicionar_resultado
            )
        except Exception as e:
            self.log(f"ERRO: {e}", 'error')
        finally:
            self.finalizar_varredura()
            
    def atualizar_progresso(self, caminho):
        # Função que roda durante a varredura para não travar a tela
        if not self.varredura_ativa: return
        self.root.update_idletasks() # Garante que a interface continue responsiva
            
    def adicionar_resultado(self, resultado):
        self.resultados.append(resultado)
        tamanho_str = f"{resultado['tamanho_mb']:.1f}"
        data_str = resultado['ultimo_acesso'].strftime("%d/%m/%Y %H:%M")
        
        self.tree.insert('', 'end', values=(resultado['caminho'], tamanho_str, data_str))
        self.log(f"ENCONTRADO: {resultado['caminho']}", 'warning')
        
    def parar_varredura(self):
        self.scanner.parar()
        self.log("VARREDURA INTERROMPIDA PELO USUÁRIO.", 'error')
        self.finalizar_varredura()
        
    def finalizar_varredura(self):
        self.varredura_ativa = False
        self.btn_escanear.config(state='normal')
        self.btn_parar.config(state='disabled')
        
        if self.resultados:
            self.btn_deletar.config(state='normal')
            self.log(f"CONCLUÍDO. {len(self.resultados)} RESQUÍCIOS ENCONTRADOS.", 'success')
        else:
            self.log("CONCLUÍDO. NENHUM RESQUÍCIO ENCONTRADO.", 'success')
            
    def deletar_selecionados(self):
        selecionados = self.tree.selection()
        if not selecionados:
            messagebox.showwarning("", "Selecione ao menos um item.")
            return
        if not messagebox.askyesno("", "Deletar os selecionados?"): return
        
        for item in selecionados:
            caminho = self.tree.item(item)['values'][0]
            sucesso, msg = self.scanner.deletar_pasta(caminho)
            if sucesso:
                self.tree.delete(item)
                self.log(f"DELETADO: {caminho}", 'success')
                self.resultados = [r for r in self.resultados if r['caminho'] != caminho]
            else:
                self.log(f"ERRO AO DELETAR: {msg}", 'error')
                
        if not self.tree.get_children():
            self.btn_deletar.config(state='disabled')