"""
MISA-CLEANER - Efeito Matrix Rain - TELA CHEIA
SOMENTE A CHUVA DE CÓDIGO! NADA MAIS!
"""
import random
import tkinter as tk
from typing import Dict, List


class MatrixRain(tk.Canvas):
    """CHUVA MATRIX - TELA INTEIRA"""
    
    CARACTERES = [
        '日','本','語','の','文','字','を','使','っ','て','い','ま','す',
        '漢','字','東','京','大','学','世','界','平','和','愛','友','情',
        '0','1','2','3','4','5','6','7','8','9',
        '!','@','#','$','%','&','*','+','=','~','?','/',
        '├','┤','╡','╢','╖','╕','╣','║','╗','╝','╜','╛','┐',
        '└','┴','┬','├','┤','┼','╞','╟','╚','╔','╩','╦','╠','═'
    ]
    
    def __init__(self, parent):
        super().__init__(parent, bg='#000000', highlightthickness=0)
        self.animando = False
        self.colunas = []
        self.parent = parent
        
        # 🌟 OCUPA A TELA INTEIRA
        self.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.bind('<Configure>', self._reinicar)
        self._inicializar()
        
    def _inicializar(self):
        """INICIALIZA A CHUVA OCUPANDO A TELA INTEIRA"""
        self.update_idletasks()
        largura = max(self.winfo_width(), 800)
        altura = max(self.winfo_height(), 600)
        
        num_colunas = largura // 14
        
        self.colunas = []
        for _ in range(num_colunas):
            self.colunas.append({
                'x': random.randint(0, largura),
                'y': random.randint(-altura, altura),
                'vel': random.uniform(1.0, 3.5),
                'tam': random.randint(5, 25)
            })
    
    def _reinicar(self, event):
        if self.animando:
            self._inicializar()
    
    def iniciar(self):
        if not self.animando:
            self.animando = True
            self._inicializar()
            self._animar()
    
    def parar(self):
        self.animando = False
    
    def _animar(self):
        if not self.animando:
            return
        
        self.delete('all')
        
        self.update_idletasks()
        largura = max(self.winfo_width(), 800)
        altura = max(self.winfo_height(), 600)
        
        for col in self.colunas:
            col['y'] += col['vel']
            
            if col['y'] > altura + 50:
                col['y'] = random.randint(-50, -10)
                col['x'] = random.randint(0, largura)
                col['vel'] = random.uniform(1.0, 3.5)
                col['tam'] = random.randint(5, 25)
            
            for i in range(col['tam']):
                y = col['y'] - (i * 15)
                if y < -10 or y > altura:
                    continue
                
                char = random.choice(self.CARACTERES)
                
                if i == 0:
                    cor = '#00ff41'
                    size = 13
                elif i == 1:
                    cor = '#00dd33'
                    size = 12
                elif i == 2:
                    cor = '#00bb22'
                    size = 11
                else:
                    v = max(0, 1.0 - (i / col['tam']))
                    g = int(180 * v)
                    cor = f'#00{g:02x}00'
                    size = 10
                
                self.create_text(
                    col['x'], y,
                    text=char,
                    fill=cor,
                    font=('Consolas', size, 'bold')
                )
        
        self.after(30, self._animar)


class MatrixFullscreen:
    """TELA CHEIA APENAS COM A CHUVA MATRIX E LOGS"""
    
    def __init__(self, parent):
        self.parent = parent
        
        # 🌟 CRIA A CHUVA OCUPANDO A TELA INTEIRA
        self.rain = MatrixRain(parent)
        
        # 🌟 TEXTO SOBREPOSTO (COM FUNDO PRETO PARA LEGIBILIDADE)
        self.text = tk.Text(
            parent,
            bg='#000000',
            fg='#00ff41',
            font=('Consolas', 11),
            insertbackground='#00ff41',
            relief='flat',
            highlightthickness=0,
            borderwidth=0,
            wrap='word',
            state='normal',
            spacing1=2,
            spacing2=2
        )
        # 🌟 TEXTO OCUPA A TELA INTEIRA (COM UMA BORDA PARA NÃO FICAR COLADO)
        self.text.place(x=20, y=20, relwidth=0.96, relheight=0.96)
        
        # CORES
        self.text.tag_config('INFO', foreground='#6bcfff')
        self.text.tag_config('SUCESSO', foreground='#6bffb8')
        self.text.tag_config('AVISO', foreground='#ffe66d')
        self.text.tag_config('ERRO', foreground='#ff6b6b')
        self.text.tag_config('CRITICO', foreground='#ff1744', font=('Consolas', 11, 'bold'))
        self.text.tag_config('destaque', foreground='#ff6b9d', font=('Consolas', 11, 'bold'))
        
        self.linhas = 0
        self.max_linhas = 200
        
        self.parent.update_idletasks()
        
    def escrever(self, texto: str, nivel: str = 'INFO', destaque: bool = False):
        """ESCREVE TEXTO SOBRE A CHUVA"""
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
            
        except:
            pass
    
    def iniciar(self):
        self.rain.iniciar()
    
    def parar(self):
        self.rain.parar()
    
    def destruir(self):
        self.parar()
        self.rain.destroy()
        self.text.destroy()