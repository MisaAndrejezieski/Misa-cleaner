"""
MISA-CLEANER - Efeito Matrix Rain
Puramente visual - cria a icônica chuva de código do filme Matrix
"""
import random
import tkinter as tk
from typing import Dict, List


class MatrixRain(tk.Canvas):
    """
    Efeito de chuva Matrix animada em tela cheia
    """
    
    CARACTERES_MATRIX = [
        '日', '本', '語', 'の', '文', '字', 'を', '使', 'っ', 'て', 'い', 'ま', 'す',
        '漢', '字', '東', '京', '大', '学', '世', '界', '平', '和', '愛', '友', '情',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        '!', '@', '#', '$', '%', '&', '*', '+', '=', '~', '?', '/',
        '├', '┤', '╡', '╢', '╖', '╕', '╣', '║', '╗', '╝', '╜', '╛', '┐',
        '└', '┴', '┬', '├', '┤', '┼', '╞', '╟', '╚', '╔', '╩', '╦', '╠', '═'
    ]
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.configure(
            bg='#000000',
            highlightthickness=0,
            relief='flat'
        )
        
        self.animando = False
        self._destroyed = False
        self.colunas: List[Dict] = []
        self.largura_coluna = 14
        self.altura_caractere = 16
        
        self.bind('<Configure>', self._on_resize)
        self.bind('<Destroy>', self._on_destroy)
        
        # 🌟 FORÇA A ATUALIZAÇÃO DO TAMANHO
        self.update_idletasks()
        self._inicializar_colunas()
        
    def _on_destroy(self, event):
        self._destroyed = True
        self.animando = False
        
    def _on_resize(self, event):
        """🌟 RECALCULA AS COLUNAS QUANDO REDIMENSIONAR"""
        if self.animando:
            self._inicializar_colunas()
    
    def _inicializar_colunas(self):
        """🌟 INICIALIZA COLUNAS OCUPANDO A TELA INTEIRA"""
        # 🌟 FORÇA A OBTENÇÃO DO TAMANHO REAL
        self.update_idletasks()
        largura = self.winfo_width()
        altura = self.winfo_height()
        
        # 🌟 SE O TAMANHO FOR 0, USA UM VALOR PADRÃO GRANDE
        if largura < 10:
            largura = 1200
        if altura < 10:
            altura = 900
        
        num_colunas = max(10, largura // self.largura_coluna)
        
        self.colunas = []
        for i in range(num_colunas):
            x = random.randint(0, largura - self.largura_coluna)
            y = random.randint(-altura, altura)
            velocidade = random.uniform(1.0, 3.5)
            comprimento = random.randint(5, 25)
            
            self.colunas.append({
                'x': x,
                'y': y,
                'velocidade': velocidade,
                'comprimento': comprimento,
                'queda': random.uniform(0.8, 1.2)
            })
    
    def iniciar(self):
        """Inicia a animação"""
        if self._destroyed:
            return
            
        if not self.animando:
            self.animando = True
            # 🌟 GARANTE QUE AS COLUNAS OCUPEM A TELA INTEIRA
            self._inicializar_colunas()
            self._animar()
            
    def parar(self):
        self.animando = False
    
    def _animar(self):
        """Loop principal de animação"""
        if not self.animando or self._destroyed:
            return
            
        self.delete('matrix')
        
        # 🌟 OBTÉM O TAMANHO REAL DA TELA
        self.update_idletasks()
        largura = self.winfo_width()
        altura = self.winfo_height()
        
        # 🌟 SE O TAMANHO FOR 0, USA VALORES PADRÃO
        if largura < 10:
            largura = 1200
        if altura < 10:
            altura = 900
        
        # Atualiza cada coluna
        for coluna in self.colunas:
            coluna['y'] += coluna['velocidade'] * coluna['queda']
            
            if coluna['y'] > altura + 100:
                coluna['y'] = random.randint(-100, -20)
                coluna['x'] = random.randint(0, largura - self.largura_coluna)
                coluna['velocidade'] = random.uniform(1.0, 3.5)
                coluna['comprimento'] = random.randint(5, 25)
                coluna['queda'] = random.uniform(0.8, 1.2)
            
            comprimento = coluna['comprimento']
            x = coluna['x']
            y_base = coluna['y']
            
            for i in range(comprimento):
                y = y_base - (i * self.altura_caractere * 0.9)
                
                if y < -20 or y > altura + 20:
                    continue
                
                char = random.choice(self.CARACTERES_MATRIX)
                
                if i == 0:
                    cor = '#00ff41'
                    tamanho_fonte = 13
                elif i == 1:
                    cor = '#00dd33'
                    tamanho_fonte = 12
                elif i == 2:
                    cor = '#00bb22'
                    tamanho_fonte = 11
                else:
                    intensidade = max(0, 1.0 - (i / comprimento))
                    verde = int(180 * intensidade)
                    cor = f'#00{verde:02x}00'
                    tamanho_fonte = 10
                
                if i == 0 and random.random() < 0.05:
                    cor = '#88ff88'
                
                self.create_text(
                    x, y,
                    text=char,
                    fill=cor,
                    font=('Consolas', tamanho_fonte, 'bold'),
                    tags='matrix'
                )
        
        # Efeito de estática
        if random.random() < 0.02:
            for _ in range(random.randint(1, 5)):
                x = random.randint(0, largura)
                y = random.randint(0, altura)
                char = random.choice(self.CARACTERES_MATRIX)
                cor = random.choice(['#00ff41', '#00dd33', '#88ff88', '#ffffff'])
                self.create_text(
                    x, y,
                    text=char,
                    fill=cor,
                    font=('Consolas', random.randint(8, 14), 'bold'),
                    tags='matrix'
                )
        
        self.after(30, self._animar)


class MatrixOverlay(tk.Frame):
    """
    Sobreposição Matrix com chuva e texto sobreposto
    """
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.configure(bg='#000000')
        
        # 🌟 GARANTE QUE OCUPA TODO O ESPAÇO DISPONÍVEL
        self.rain = MatrixRain(self)
        self.rain.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Área de texto
        self.text_container = tk.Frame(self, bg='#000000')
        self.text_container.place(x=10, y=10, relwidth=0.98, relheight=0.98)
        
        self.text = tk.Text(
            self.text_container,
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
            spacing3=1
        )
        self.text.pack(fill=tk.BOTH, expand=True)
        
        # Tags de cores
        self.text.tag_config('INFO', foreground='#6bcfff')
        self.text.tag_config('SUCESSO', foreground='#6bffb8')
        self.text.tag_config('AVISO', foreground='#ffe66d')
        self.text.tag_config('ERRO', foreground='#ff6b6b')
        self.text.tag_config('CRITICO', foreground='#ff1744', font=('Consolas', 10, 'bold'))
        self.text.tag_config('DEBUG', foreground='#8888aa')
        self.text.tag_config('destaque', foreground='#ff6b9d', font=('Consolas', 10, 'bold'))
        
        self.text.see('end')
        
        self.max_linhas = 500
        self.linhas = 0
        self._destroyed = False
        
        self.bind('<Destroy>', self._on_destroy)
        
        # 🌟 FORÇA A ATUALIZAÇÃO
        self.update_idletasks()
        
    def _on_destroy(self, event):
        self._destroyed = True
        if hasattr(self, 'rain'):
            self.rain.parar()
            
    def escrever(self, texto: str, nivel: str = 'INFO', destaque: bool = False):
        """Escreve texto sobre a chuva Matrix"""
        if self._destroyed:
            return
            
        try:
            self.text.config(state='normal')
            
            if self.linhas > self.max_linhas:
                self.text.delete('1.0', f'{self.linhas - self.max_linhas}.0')
                self.linhas = self.max_linhas
            
            tag = 'destaque' if destaque else nivel
            self.text.insert('end', texto + '\n', tag)
            self.linhas += 1
            
            self.text.see('end')
            self.text.config(state='disabled')
            
        except Exception:
            pass
    
    def iniciar_rain(self):
        """Inicia a chuva Matrix"""
        if hasattr(self, 'rain'):
            # 🌟 GARANTE QUE AS COLUNAS OCUPEM A TELA INTEIRA
            self.rain._inicializar_colunas()
            self.rain.iniciar()
            
    def parar_rain(self):
        """Para a chuva Matrix"""
        if hasattr(self, 'rain'):
            self.rain.parar()