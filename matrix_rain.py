"""
MISA-CLEANER - Efeito Matrix Rain
VERSÃO 100% TKINTER - SEM BIBLIOTECAS EXTERNAS
"""
import random
import tkinter as tk


class MatrixRain(tk.Canvas):
    """CHUVA MATRIX - 100% TKINTER"""
    
    CARACTERES = [
        '日','本','語','の','文','字','を','使','っ','て','い','ま','す',
        '0','1','2','3','4','5','6','7','8','9',
        '!','@','#','$','%','&','*','+','=','~',
        '├','┤','╡','╢','╖','╕','╣','║','╗','╝','╜','╛','┐',
        '└','┴','┬','├','┤','┼','╞','╟','╚','╔','╩','╦','╠','═'
    ]
    
    def __init__(self, parent):
        super().__init__(parent, bg='#000000', highlightthickness=0)
        self.animando = False
        self.colunas = []
        
        # OCUPA A TELA INTEIRA
        self.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.bind('<Configure>', self._reinicar)
        self._inicializar()
        
    def _inicializar(self):
        self.update_idletasks()
        largura = max(self.winfo_width(), 800)
        altura = max(self.winfo_height(), 600)
        
        num_colunas = largura // 12
        
        self.colunas = []
        for _ in range(num_colunas):
            tamanho = random.randint(15, 35)
            self.colunas.append({
                'x': random.randint(0, largura),
                'y': random.randint(-altura, altura),
                'vel': 0.6,
                'tam': tamanho,
                'chars': [random.choice(self.CARACTERES) for _ in range(tamanho)]
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
                col['chars'] = [random.choice(self.CARACTERES) for _ in range(col['tam'])]
            
            for i in range(col['tam']):
                y = col['y'] - (i * 16)
                if y < -10 or y > altura:
                    continue
                
                char = col['chars'][i]
                
                if i == 0:
                    cor = '#00ff41'
                    size = 14
                elif i == 1:
                    cor = '#00dd33'
                    size = 13
                elif i == 2:
                    cor = '#00bb22'
                    size = 12
                else:
                    v = max(0, 1.0 - (i / col['tam']))
                    g = int(180 * v)
                    cor = f'#00{g:02x}00'
                    size = 11
                
                if i == 0 and random.random() < 0.08:
                    cor = '#88ff88'
                    size = 16
                
                self.create_text(
                    col['x'], y,
                    text=char,
                    fill=cor,
                    font=('Consolas', size, 'bold')
                )
        
        self.after(50, self._animar)