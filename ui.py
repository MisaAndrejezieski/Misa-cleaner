import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, scrolledtext, ttk

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scanner import Scanner

matplotlib.use('TkAgg')

class MisaCleanerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MISA-CLEANER - Caçador de Resquícios Digitais")
        self.root.geometry("1000x700")
        self.root.configure(bg='#0a0a0f')
        
        self.scanner = Scanner()
        self.resultados = []
        self.selecionados = set()
        self.varrendo = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Cores Neon Pastel
        cores = {
            'bg': '#0a0a0f',
            'neon_rosa': '#ff6b9d',
            'neon_azul': '#6bcfff',
            'neon_roxo': '#b06bff',
            'neon_verde': '#6bffb8',
            'pastel_rosa': '#ffb3c6',
            'pastel_azul': '#b3d9ff',
            'pastel_roxo': '#d4b3ff',
            'texto': '#e0e0ff'
        }
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg=cores['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título com efeito neon
        titulo = tk.Label(
            main_frame,
            text="╔══════════════════════════════════════════╗\n"
                 "║          MISA-CLEANER v1.0             ║\n"
                 "║   ── Caçador de Resquícios Digitais ── ║\n"
                 "╚══════════════════════════════════════════╝",
            font=('Consolas', 12),
            fg=cores['neon_azul'],
            bg=cores['bg'],
            justify=tk.CENTER
        )
        titulo.pack(pady=(0, 20))
        
        # Frame dos botões
        btn_frame = tk.Frame(main_frame, bg=cores['bg'])
        btn_frame.pack(pady=(0, 15))
        
        # Botões estilizados
        style = {
            'font': ('Consolas', 10, 'bold'),
            'bg': cores['bg'],
            'fg': cores['neon_verde'],
            'relief': tk.FLAT,
            'padx': 20,
            'pady': 10,
            'cursor': 'hand2'
        }
        
        self.btn_iniciar = tk.Button(
            btn_frame,
            text="▶ INICIAR VARREDURA",
            command=self.iniciar_varredura,
            **style
        )
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        
        self.btn_parar = tk.Button(
            btn_frame,
            text="⏹ PARAR",
            command=self.parar_varredura,
            state=tk.DISABLED,
            **style
        )
        self.btn_parar.pack(side=tk.LEFT, padx=5)
        
        self.btn_deletar = tk.Button(
            btn_frame,
            text="🗑 DELETAR SELECIONADOS",
            command=self.deletar_selecionados,
            **style
        )
        self.btn_deletar.pack(side=tk.LEFT, padx=5)
        
        # Frame da lista (com scroll)
        list_frame = tk.Frame(main_frame, bg=cores['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview com estilo neon
        style_tree = ttk.Style()
        style_tree.theme_use('clam')
        style_tree.configure('Treeview', 
                           background='#0a0a0f',
                           foreground=cores['texto'],
                           rowheight=25,
                           fieldbackground='#0a0a0f',
                           borderwidth=0)
        style_tree.configure('Treeview.Heading',
                           background='#1a1a2e',
                           foreground=cores['neon_azul'],
                           font=('Consolas', 9, 'bold'))
        style_tree.map('Treeview', 
                      background=[('selected', '#2a2a4e')])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            list_frame,
            columns=('caminho', 'tamanho', 'ultimo_acesso', 'tipo'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading('caminho', text='Caminho', anchor=tk.W)
        self.tree.heading('tamanho', text='Tamanho (MB)', anchor=tk.E)
        self.tree.heading('ultimo_acesso', text='Último Acesso', anchor=tk.W)
        self.tree.heading('tipo', text='Tipo', anchor=tk.W)
        
        self.tree.column('caminho', width=450, anchor=tk.W)
        self.tree.column('tamanho', width=100, anchor=tk.E)
        self.tree.column('ultimo_acesso', width=150, anchor=tk.W)
        self.tree.column('tipo', width=120, anchor=tk.W)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind para seleção
        self.tree.bind('<<TreeviewSelect>>', self.on_selecionar)
        
        # Frame do log
        log_label = tk.Label(
            main_frame,
            text="─── LOG DO SISTEMA ───",
            font=('Consolas', 9),
            fg=cores['neon_roxo'],
            bg=cores['bg']
        )
        log_label.pack(pady=(10, 2), anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(
            main_frame,
            height=6,
            font=('Consolas', 8),
            bg='#0a0a0f',
            fg=cores['texto'],
            insertbackground=cores['neon_azul']
        )
        self.log_text.pack(fill=tk.X, pady=(0, 5))
        self.log_text.config(state=tk.DISABLED)
        
        # Status bar
        self.status_label = tk.Label(
            main_frame,
            text="SISTEMA PRONTO AGUARDANDO VARREDURA",
            font=('Consolas', 8),
            fg=cores['neon_verde'],
            bg=cores['bg'],
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, pady=(5, 0))
        
        # Adicionar log inicial
        self.adicionar_log(">> SISTEMA INICIADO. AGUARDANDO COMANDOS...")
        self.adicionar_log(">> DIGITE 'INICIAR VARREDURA' PARA COMEÇAR")

    def adicionar_log(self, mensagem):
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {mensagem}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def iniciar_varredura(self):
        if self.varrendo:
            return
            
        self.varrendo = True
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_parar.config(state=tk.NORMAL)
        
        # Limpa a lista anterior
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.selecionados.clear()
        self.resultados = []
        
        self.adicionar_log(">> INICIANDO VARREDURA MATRIX...")
        self.status_label.config(text="VARRENDO SISTEMA...")
        
        # Inicia a varredura em uma thread separada
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
            
            # Atualiza a interface
            self.root.after(0, self.finalizar_varredura)
            
        except Exception as e:
            self.root.after(0, lambda: self.adicionar_log(f">> ERRO: {str(e)}"))
            self.root.after(0, self.finalizar_varredura)

    def atualizar_progresso(self, caminho):
        self.root.after(0, lambda: self.status_label.config(
            text=f"ESCANEANDO: {caminho[:60]}..."
        ))

    def adicionar_resultado(self, item):
        self.root.after(0, lambda: self.inserir_item_na_lista(item))

    def inserir_item_na_lista(self, item):
        try:
            caminho = item.get('caminho', '')
            tamanho = f"{item.get('tamanho_mb', 0):.1f}"
            ultimo_acesso = item.get('ultimo_acesso', '')
            if ultimo_acesso:
                ultimo_acesso = ultimo_acesso.strftime("%Y-%m-%d %H:%M")
            
            tipo = item.get('tipo', 'desconhecido')
            if tipo == 'resquicio':
                programa = item.get('programa', '')
                tipo = f"Resquício: {programa}"
            elif tipo == 'obsoleto':
                tipo = "Obsoleto"
            elif tipo == 'duplicado':
                tipo = "Duplicado"
            else:
                tipo = "Outro"
            
            self.tree.insert('', tk.END, values=(caminho, tamanho, ultimo_acesso, tipo))
            
            # Scroll para o último item
            self.tree.yview_moveto(1)
            
        except Exception as e:
            self.adicionar_log(f">> ERRO AO INSERIR ITEM: {str(e)}")

    def finalizar_varredura(self):
        self.varrendo = False
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_parar.config(state=tk.DISABLED)
        
        total = len(self.tree.get_children())
        self.status_label.config(text=f"VARREDURA CONCLUÍDA. {total} RESQUÍCIOS ENCONTRADOS.")
        self.adicionar_log(f">> VARREDURA CONCLUÍDA. {total} RESQUÍCIOS ENCONTRADOS.")

    def parar_varredura(self):
        self.scanner.parar()
        self.adicionar_log(">> PARANDO VARREDURA...")
        self.status_label.config(text="VARREDURA INTERROMPIDA PELO USUÁRIO")
        self.btn_parar.config(state=tk.DISABLED)
        self.varrendo = False

    def on_selecionar(self, event):
        selection = self.tree.selection()
        self.selecionados = set(selection)
        
        if selection:
            self.btn_deletar.config(state=tk.NORMAL)
        else:
            self.btn_deletar.config(state=tk.DISABLED)

    def deletar_selecionados(self):
        if not self.selecionados:
            return
            
        if not messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja deletar {len(self.selecionados)} item(ns)?\n"
            "Esta ação NÃO pode ser desfeita!"
        ):
            return
        
        deletados = 0
        erros = 0
        
        for item in self.selecionados:
            valores = self.tree.item(item, 'values')
            caminho = valores[0]
            
            # Verifica se é arquivo ou pasta
            success, msg = self.scanner.deletar_pasta(caminho)
            if success:
                self.tree.delete(item)
                deletados += 1
                self.adicionar_log(f">> DELETADO: {caminho}")
            else:
                erros += 1
                self.adicionar_log(f">> ERRO AO DELETAR: {caminho}")
        
        self.selecionados.clear()
        self.btn_deletar.config(state=tk.DISABLED)
        
        self.adicionar_log(f">> EXCLUSÃO CONCLUÍDA: {deletados} deletados, {erros} erros")

def main():
    root = tk.Tk()
    app = MisaCleanerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()