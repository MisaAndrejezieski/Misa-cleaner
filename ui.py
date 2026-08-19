import os
import random
import subprocess
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from scanner import Scanner


class MatrixTerminal(tk.Text):
    """Widget terminal Matrix otimizado"""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.config(
            bg='#000000',
            fg='#00ff41',
            font=('Consolas', 9),
            insertbackground='#00ff41',
            relief='flat',
            highlightthickness=0,
            borderwidth=0,
            wrap='word',
            state='normal'
        )
        
        self._destroyed = False
        
        # Tags de cores
        self.tag_config('verde_matrix', foreground='#00ff41')
        self.tag_config('verde_claro', foreground='#33ff77')
        self.tag_config('verde_escuro', foreground='#009922')
        self.tag_config('amarelo', foreground='#ffff33')
        self.tag_config('vermelho', foreground='#ff3333')
        self.tag_config('azul', foreground='#33ccff')
        self.tag_config('branco', foreground='#ffffff')
        
        self.bind('<Destroy>', self._on_destroy)
        
    def _on_destroy(self, event):
        self._destroyed = True
        
    def escrever_matrix(self, texto, delay=0.005, cor='verde_matrix'):
        """Escreve texto com efeito de digitação (mais rápido)"""
        if self._destroyed:
            return
            
        try:
            self.config(state='normal')
            self.insert('end', texto + '\n', cor)
            self.see('end')
            self.config(state='disabled')
            self.update_idletasks()
        except:
            pass


class MisaCleanerUI:
    def __init__(self, root):
        self.root = root
        
        # Remove bordas padrão
        self.root.overrideredirect(True)
        self.root.configure(bg='#0a0a0f')
        
        # Tamanho da janela
        self.root.geometry("1100x850")
        self.centralizar_janela()
        
        # Cores
        self.cores = {
            'bg': '#0a0a0f',
            'bg_secundario': '#15152a',
            'neon_azul': '#6bcfff',
            'neon_verde': '#6bffb8',
            'neon_roxo': '#b06bff',
            'neon_rosa': '#ff6b9d',
            'neon_amarelo': '#ffe66d',
            'texto': '#e0e0ff',
            'verde_terminal': '#00ff41'
        }
        
        self.scanner = Scanner()
        self.resultados = []
        self.varrendo = False
        self.scanner_thread = None
        
        self.setup_ui()
        
    def centralizar_janela(self):
        self.root.update_idletasks()
        largura = self.root.winfo_width()
        altura = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        self.root.geometry(f'{largura}x{altura}+{x}+{y}')
    
    # ===== CONTROLES DA JANELA (Arrastar, Minimizar, Fechar) =====
    def iniciar_arraste(self, event):
        self.x_inicio = event.x
        self.y_inicio = event.y
    
    def arrastar(self, event):
        x = self.root.winfo_x() + event.x - self.x_inicio
        y = self.root.winfo_y() + event.y - self.y_inicio
        self.root.geometry(f'+{x}+{y}')
    
    def minimizar_janela(self):
        self.root.iconify()
    
    def maximizar_janela(self):
        if self.root.winfo_width() == self.root.winfo_screenwidth():
            self.root.geometry("1100x850")
            self.centralizar_janela()
        else:
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
    
    def fechar(self):
        if self.varrendo:
            if not messagebox.askyesno("Sair", "Varredura em andamento. Deseja sair?"):
                return
            self.scanner.parar()
        self.root.quit()
        self.root.destroy()
    
    # ===== CONSTRUÇÃO DA INTERFACE =====
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg=self.cores['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # ===== BARRA DE TÍTULO CUSTOMIZADA =====
        title_bar = tk.Frame(main_frame, bg='#0f0f1a', height=30)
        title_bar.pack(fill=tk.X, side=tk.TOP)
        title_bar.pack_propagate(False)
        
        # Bind para arrastar a janela pela barra de título
        title_bar.bind('<Button-1>', self.iniciar_arraste)
        title_bar.bind('<B1-Motion>', self.arrastar)
        
        tk.Label(
            title_bar, 
            text="MISA-CLEANER", 
            font=('Consolas', 10, 'bold'),
            fg=self.cores['neon_azul'],
            bg='#0f0f1a'
        ).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Botões de controle da janela
        btn_controles = tk.Frame(title_bar, bg='#0f0f1a')
        btn_controles.pack(side=tk.RIGHT)
        
        tk.Button(btn_controles, text="─", command=self.minimizar_janela,
                  bg='#0f0f1a', fg='white', relief=tk.FLAT, bd=0, font=('Arial', 12),
                  activebackground='#2a2a3a', activeforeground='white', cursor='hand2').pack(side=tk.LEFT, padx=5)
        tk.Button(btn_controles, text="□", command=self.maximizar_janela,
                  bg='#0f0f1a', fg='white', relief=tk.FLAT, bd=0, font=('Arial', 10),
                  activebackground='#2a2a3a', activeforeground='white', cursor='hand2').pack(side=tk.LEFT, padx=5)
        tk.Button(btn_controles, text="✕", command=self.fechar,
                  bg='#0f0f1a', fg='#ff3333', relief=tk.FLAT, bd=0, font=('Arial', 12),
                  activebackground='#ff3333', activeforeground='white', cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # ===== CONTEÚDO PRINCIPAL =====
        content_frame = tk.Frame(main_frame, bg=self.cores['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # ===== CABEÇALHO (Limpo e Elegante) =====
        header_frame = tk.Frame(content_frame, bg=self.cores['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            header_frame,
            text="MISA-CLEANER",
            font=('Consolas', 24, 'bold'),
            fg=self.cores['neon_azul'],
            bg=self.cores['bg']
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header_frame,
            text="v1.0 • Caçador de Resquícios Digitais",
            font=('Consolas', 10),
            fg=self.cores['neon_verde'],
            bg=self.cores['bg']
        ).pack(side=tk.LEFT, padx=15, pady=10)
        
        # ===== BOTÕES =====
        btn_frame = tk.Frame(content_frame, bg=self.cores['bg'])
        btn_frame.pack(pady=10)
        
        btn_style = {
            'font': ('Consolas', 10, 'bold'),
            'bg': '#0f0f1a',
            'fg': self.cores['neon_verde'],
            'relief': tk.FLAT,
            'padx': 20,
            'pady': 8,
            'cursor': 'hand2',
            'borderwidth': 1,
            'highlightbackground': '#1a1a2e',
            'highlightthickness': 1
        }
        
        self.btn_iniciar = tk.Button(btn_frame, text="▶ INICIAR VARREDURA", command=self.iniciar_varredura, **btn_style)
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        
        self.btn_parar = tk.Button(btn_frame, text="⏹ PARAR", command=self.parar_varredura, state=tk.DISABLED, **btn_style)
        self.btn_parar.pack(side=tk.LEFT, padx=5)
        
        self.btn_deletar = tk.Button(btn_frame, text="🗑 DELETAR SELECIONADOS", command=self.deletar_selecionados, state=tk.DISABLED, **btn_style)
        self.btn_deletar.pack(side=tk.LEFT, padx=5)
        
        # ===== TERMINAL MATRIX =====
        terminal_frame = tk.Frame(content_frame, bg=self.cores['bg'])
        terminal_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        terminal_label = tk.Label(terminal_frame, text="╔══════════ TERMINAL MATRIX ══════════╗", font=('Consolas', 8), fg=self.cores['neon_roxo'], bg=self.cores['bg'])
        terminal_label.pack(anchor=tk.W)
        
        terminal_container = tk.Frame(terminal_frame, bg=self.cores['bg'])
        terminal_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(terminal_container, bg='#0a0a0f')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.terminal = MatrixTerminal(terminal_container, height=6, yscrollcommand=scrollbar.set)
        self.terminal.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar.config(command=self.terminal.yview)
        
        # Mensagem inicial
        self.terminal.escrever_matrix(">> SISTEMA PRONTO. DIGITE 'INICIAR' PARA COMEÇAR.", 'verde_matrix')
        self.terminal.escrever_matrix(">> MISA-CLEANER V1.0 - CAÇADOR DE RESQUÍCIOS DIGITAIS", 'azul')
        
        # ===== LISTA DE RESULTADOS (Tabela Clicável) =====
        list_frame = tk.Frame(content_frame, bg=self.cores['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        tk.Label(list_frame, text="📋 RESULTADOS ENCONTRADOS (Duplo clique para abrir a pasta)", 
                 font=('Consolas', 9), fg=self.cores['neon_amarelo'], bg=self.cores['bg']).pack(anchor=tk.W)
        
        # Treeview (Tabela)
        columns = ('#1', '#2', '#3')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        self.tree.heading('#1', text='Tipo')
        self.tree.heading('#2', text='Nome / Programa')
        self.tree.heading('#3', text='Caminho')
        self.tree.column('#1', width=100, anchor='w')
        self.tree.column('#2', width=200, anchor='w')
        self.tree.column('#3', width=500, anchor='w')
        
        # Scrollbar da tabela
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 🟢 Duplo clique para abrir o explorador de arquivos
        self.tree.bind("<Double-1>", self.abrir_caminho_selecionado)
        
        # ===== STATUS =====
        self.status_label = tk.Label(content_frame, text="SISTEMA PRONTO.", font=('Consolas', 9), fg=self.cores['neon_verde'], bg=self.cores['bg'], anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=5)
        
        # ===== BARRA DE PROGRESSO =====
        progress_frame = tk.Frame(content_frame, bg=self.cores['bg'])
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_var = tk.DoubleVar()
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Matrix.Horizontal.TProgressbar', background='#00ff41', troughcolor='#0a0a0f', bordercolor='#0a0a0f', lightcolor='#00ff41', darkcolor='#00cc33')
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, style='Matrix.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=5)
    
    # ===== Lógica de Interação =====
    def adicionar_log(self, mensagem, cor='verde_matrix'):
        if not self.terminal._destroyed:
            try:
                self.root.after(0, lambda: self.terminal.escrever_matrix(mensagem, 0.005, cor))
            except:
                pass
    
    def abrir_caminho_selecionado(self, event):
        """Abre o explorador de arquivos na pasta do item selecionado"""
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        caminho = item['values'][2]  # A coluna 2 é o caminho completo
        
        if os.path.exists(caminho):
            # Abre a pasta no explorador do Windows e seleciona o arquivo/pasta
            try:
                subprocess.run(['explorer', '/select,', caminho])
            except:
                # Fallback: abre apenas a pasta pai se o comando acima falhar
                subprocess.run(['explorer', os.path.dirname(caminho)])
        else:
            messagebox.showwarning("Caminho não encontrado", f"O caminho não existe mais:\n{caminho}")
    
    def adicionar_resultado_tabela(self, item):
        """Adiciona uma linha na tabela de resultados"""
        tipo = item.get('tipo', '').capitalize()
        nome = item.get('programa', '') if item.get('programa') else os.path.basename(item.get('caminho', ''))
        caminho = item.get('caminho', '')
        
        # Insere na tabela
        self.tree.insert("", "end", values=(tipo, nome, caminho))
    
    def iniciar_varredura(self):
        if self.varrendo:
            return
        
        # Limpa a tabela anterior
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.varrendo = True
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_parar.config(state=tk.NORMAL)
        self.btn_deletar.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.resultados = []
        
        self.adicionar_log("")
        self.adicionar_log(">> INICIANDO PROTOCOLO MISA-CLEANER...", 'verde_matrix')
        self.adicionar_log(">> ATIVANDO 3 CAMADAS DE ANÁLISE:", 'azul')
        self.adicionar_log("   1. RESQUÍCIOS DE PROGRAMAS DELETADOS", 'verde_claro')
        self.adicionar_log("   2. ARQUIVOS OBSOLETOS", 'verde_claro')
        self.adicionar_log("   3. ARQUIVOS DUPLICADOS", 'verde_claro')
        self.adicionar_log("")
        
        self.status_label.config(text="🔄 VARRENDO SISTEMA...")
        
        self.scanner_thread = threading.Thread(target=self.executar_varredura)
        self.scanner_thread.daemon = True
        self.scanner_thread.start()
    
    def executar_varredura(self):
        try:
            resultados = self.scanner.escanear_tudo(
                callback_progresso=lambda caminho: self.atualizar_progresso(caminho),
                callback_resultado=lambda item: self.adicionar_resultado(item)
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
        progresso_atual = self.progress_var.get()
        if progresso_atual < 95:
            novo_progresso = min(progresso_atual + 0.3, 95)
            self.root.after(0, lambda: self.progress_var.set(novo_progresso))
        
        if random.random() < 0.05:
            nome = os.path.basename(caminho) if caminho else "?"
            self.root.after(0, lambda: self.adicionar_log(f"   🔍 {nome[:40]}...", 'verde_escuro'))
    
    def adicionar_resultado(self, item):
        tipo = item.get('tipo', '')
        caminho = item.get('caminho', '')
        tamanho = item.get('tamanho_mb', 0)
        programa = item.get('programa', '')
        nome = os.path.basename(caminho) if caminho else "?"
        
        if tipo == 'resquicio':
            mensagem = f"   🔍 RESQUÍCIO: {programa} - {nome} ({tamanho:.1f} MB)"
            cor = 'amarelo'
        elif tipo == 'obsoleto':
            mensagem = f"   📂 OBSOLETO: {nome} ({tamanho:.1f} MB)"
            cor = 'verde_claro'
        elif tipo == 'duplicado':
            mensagem = f"   📎 DUPLICADO: {nome} ({tamanho:.1f} MB)"
            cor = 'azul'
        else:
            mensagem = f"   📄 ENCONTRADO: {nome} ({tamanho:.1f} MB)"
            cor = 'verde_matrix'
        
        self.root.after(0, lambda: self.adicionar_log(mensagem, cor))
        self.root.after(0, lambda: self.adicionar_resultado_tabela(item))
    
    def finalizar_varredura(self):
        self.varrendo = False
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_parar.config(state=tk.DISABLED)
        self.progress_var.set(100)
        
        total = len(self.resultados)
        
        if total > 0:
            self.btn_deletar.config(state=tk.NORMAL)
        
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
        if not self.resultados:
            self.adicionar_log(">> NENHUM RESQUÍCIO PARA DELETAR.", 'amarelo')
            return
        
        if not messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja deletar TODOS os {len(self.resultados)} resquícios encontrados?"):
            return
        
        deletados = 0
        erros = 0
        
        for item in self.resultados:
            caminho = item.get('caminho', '')
            if not caminho:
                continue
                
            success, msg = self.scanner.deletar_pasta(caminho)
            if success:
                deletados += 1
                self.adicionar_log(f"   🗑 DELETADO: {os.path.basename(caminho)}", 'verde_claro')
            else:
                erros += 1
                self.adicionar_log(f"   ❌ ERRO: {msg}", 'vermelho')
        
        self.resultados = []
        self.btn_deletar.config(state=tk.DISABLED)
        # Limpa a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.adicionar_log("")
        self.adicionar_log(f">> EXCLUSÃO CONCLUÍDA: {deletados} DELETADOS, {erros} ERROS", 'verde_matrix')


def main():
    root = tk.Tk()
    app = MisaCleanerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()