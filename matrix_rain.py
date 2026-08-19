"""
MISA-CLEANER - Efeito Matrix Rain
Puramente visual - cria a icônica chuva de código do filme Matrix

CARACTERÍSTICAS:
✅ Chuva de caracteres estilo Matrix (Kanji + números + símbolos)
✅ Gradiente de cores (verde brilhante no topo, escuro na base)
✅ Velocidade variável para efeito orgânico
✅ Ocupa a tela inteira
✅ Leve e otimizado (usa Canvas do Tkinter)
"""
import random
import tkinter as tk
from typing import Dict, List, Optional


class MatrixRain(tk.Canvas):
    """
    Efeito de chuva Matrix animada em tela cheia
    
    Inspirado no filme "The Matrix" (1999)
    """
    
    # Caracteres estilo Matrix (Kanji + símbolos + números)
    CARACTERES_MATRIX = [
        # Kanji (ideogramas japoneses)
        '日', '本', '語', 'の', '文', '字', 'を', '使', 'っ', 'て', 'い', 'ま', 'す',
        '漢', '字', '日', '本', '語', '学', '習', '者', '東', '京', '大', '学',
        '世', '界', '平', '和', '愛', '友', '情', '夢', '希', '望', '光', '影',
        
        # Números
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        
        # Símbolos Matrix
        '!', '@', '#', '$', '%', '&', '*', '+', '=', '~', '?', '/', '\\',
        '|', ':', ';', '"', "'", '<', '>', '.', ',', '-', '_',
        
        # Caracteres especiais (estilo Matrix)
        '├', '┤', '╡', '╢', '╖', '╕', '╣', '║', '╗', '╝', '╜', '╛', '┐',
        '└', '┴', '┬', '├', '┤', '┼', '╞', '╟', '╚', '╔', '╩', '╦', '╠', '═',
        '╬', '╧', '╨', '╤', '╥', '╙', '╘', '╒', '╓', '╫', '╪', '┘', '┌'
    ]
    
    # Cores do Matrix (gradiente de verde)
    CORES_VERDE = [
        '#00ff41',  # Verde Matrix brilhante (cabeça)
        '#00dd33',  # Verde claro
        '#00bb22',  # Verde médio
        '#009911',  # Verde escuro
        '#007700',  # Verde muito escuro (cauda)
        '#005500',  # Verde quase preto
        '#003300',  # Verde muito escuro
    ]
    
    def __init__(self, parent, *args, **kwargs):
        """
        Inicializa a chuva Matrix
        
        Args:
            parent: Widget pai (tk.Frame ou tk.Tk)
        """
        super().__init__(parent, *args, **kwargs)
        
        # Configuração do Canvas
        self.configure(
            bg='#000000',          # Fundo preto
            highlightthickness=0,   # Sem borda
            relief='flat'          # Sem relevo
        )
        
        # Estado da animação
        self.animando = False
        self._destroyed = False
        
        # Colunas da chuva
        self.colunas: List[Dict] = []
        self.largura_coluna = 14    # Largura de cada caractere
        self.altura_caractere = 16  # Altura de cada caractere
        
        # Configuração da fonte
        self.fonte_tamanho = 11
        self.fonte = ('Consolas', self.fonte_tamanho, 'bold')
        
        # Bind para redimensionamento
        self.bind('<Configure>', self._on_resize)
        self.bind('<Destroy>', self._on_destroy)
        
        # Inicializar colunas
        self._inicializar_colunas()
        
    def _on_destroy(self, event):
        """Lida com destruição do widget"""
        self._destroyed = True
        self.animando = False
        
    def _on_resize(self, event):
        """Reinicia colunas ao redimensionar"""
        if self.animando:
            self._inicializar_colunas()
    
    def _inicializar_colunas(self):
        """Inicializa todas as colunas da chuva"""
        largura = self.winfo_width() or 800
        altura = self.winfo_height() or 600
        
        if largura < 10 or altura < 10:
            return
            
        # Calcula número de colunas
        num_colunas = max(10, largura // self.largura_coluna)
        
        self.colunas = []
        for i in range(num_colunas):
            # Posição X da coluna
            x = random.randint(0, largura - self.largura_coluna)
            
            # Posição Y inicial (distribuição aleatória)
            y = random.randint(-altura, altura)
            
            # Velocidade variável para efeito orgânico
            velocidade = random.uniform(1.0, 3.5)
            
            # Comprimento da coluna (quantos caracteres)
            comprimento = random.randint(5, 25)
            
            # Queda variável
            queda = random.uniform(0.8, 1.2)
            
            self.colunas.append({
                'x': x,
                'y': y,
                'velocidade': velocidade,
                'comprimento': comprimento,
                'queda': queda,
                'caracteres': []  # Será preenchido durante a animação
            })
    
    def iniciar(self):
        """Inicia a animação da chuva Matrix"""
        if self._destroyed:
            return
            
        if not self.animando:
            self.animando = True
            self._inicializar_colunas()
            self._animar()
            
    def parar(self):
        """Para a animação da chuva Matrix"""
        self.animando = False
    
    def _animar(self):
        """Loop principal de animação (chamado recursivamente)"""
        if not self.animando or self._destroyed:
            return
            
        # Limpa o canvas
        self.delete('matrix')
        
        largura = self.winfo_width() or 800
        altura = self.winfo_height() or 600
        
        # Atualiza cada coluna
        for coluna in self.colunas:
            # Move a coluna para baixo
            coluna['y'] += coluna['velocidade'] * coluna['queda']
            
            # Se saiu da tela, reposiciona no topo
            if coluna['y'] > altura + 100:
                coluna['y'] = random.randint(-100, -20)
                coluna['x'] = random.randint(0, largura - self.largura_coluna)
                coluna['velocidade'] = random.uniform(1.0, 3.5)
                coluna['comprimento'] = random.randint(5, 25)
                coluna['queda'] = random.uniform(0.8, 1.2)
            
            # Desenha a coluna (cabeça mais brilhante, cauda mais escura)
            comprimento = coluna['comprimento']
            x = coluna['x']
            y_base = coluna['y']
            
            for i in range(comprimento):
                y = y_base - (i * self.altura_caractere * 0.9)
                
                # Só desenha se estiver visível
                if y < -20 or y > altura + 20:
                    continue
                
                # Escolhe um caractere aleatório
                char = random.choice(self.CARACTERES_MATRIX)
                
                # Gradiente de cor: cabeça (i=0) mais brilhante, cauda mais escura
                if i == 0:
                    # Cabeça da coluna: verde Matrix brilhante
                    cor = '#00ff41'
                    tamanho_fonte = self.fonte_tamanho + 2
                elif i == 1:
                    cor = '#00dd33'
                    tamanho_fonte = self.fonte_tamanho + 1
                elif i == 2:
                    cor = '#00bb22'
                    tamanho_fonte = self.fonte_tamanho
                else:
                    # Escurece gradualmente
                    intensidade = max(0, 1.0 - (i / comprimento))
                    # Mapeia para valores de verde (0-180)
                    verde = int(180 * intensidade)
                    cor = f'#00{verde:02x}00'
                    tamanho_fonte = self.fonte_tamanho
                
                # Pequeno brilho aleatório na cabeça
                if i == 0 and random.random() < 0.05:
                    cor = '#88ff88'  # Brilho intenso raro
                
                # Desenha o caractere
                self.create_text(
                    x, y,
                    text=char,
                    fill=cor,
                    font=('Consolas', tamanho_fonte, 'bold'),
                    tags='matrix'
                )
        
        # Pequeno efeito de "estática" (caracteres piscando aleatoriamente)
        if random.random() < 0.02:  # 2% de chance por frame
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
        
        # Próximo frame (~30 FPS)
        self.after(30, self._animar)


class MatrixOverlay(tk.Frame):
    """
    Sobreposição Matrix com chuva e texto sobreposto
    
    Combina:
    1. Fundo: Chuva Matrix animada
    2. Primeiro plano: Texto de logs com fundo semi-transparente
    """
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.configure(bg='#000000')
        
        # 1. Fundo: Chuva Matrix
        self.rain = MatrixRain(self)
        self.rain.place(x=0, y=0, relwidth=1, relheight=1)
        
        # 2. Área de texto (com fundo semi-transparente para legibilidade)
        # Usamos um frame com cor escura e transparência simulada
        self.text_container = tk.Frame(
            self,
            bg='#000000'
        )
        self.text_container.place(
            x=10, y=10,
            relwidth=0.98, relheight=0.98
        )
        
        # 3. Widget de texto com fundo escuro semi-transparente
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
        
        # Scroll para acompanhar o texto
        self.text.see('end')
        
        # Limite de linhas
        self.max_linhas = 500
        self.linhas = 0
        
        self._destroyed = False
        self.bind('<Destroy>', self._on_destroy)
        
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
            
            # Remove linhas antigas
            if self.linhas > self.max_linhas:
                self.text.delete('1.0', f'{self.linhas - self.max_linhas}.0')
                self.linhas = self.max_linhas
            
            # Insere com a tag apropriada
            tag = 'destaque' if destaque else nivel
            self.text.insert('end', texto + '\n', tag)
            self.linhas += 1
            
            # Auto-scroll
            self.text.see('end')
            self.text.config(state='disabled')
            
        except Exception:
            pass
    
    def iniciar_rain(self):
        """Inicia a chuva Matrix"""
        if hasattr(self, 'rain'):
            self.rain.iniciar()
            
    def parar_rain(self):
        """Para a chuva Matrix"""
        if hasattr(self, 'rain'):
            self.rain.parar()