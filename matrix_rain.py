"""
MISA-CLEANER - Efeito Matrix Rain
EXATAMENTE IGUAL AO FILME - LENTA, DENSA E FLUIDA
"""
import random
import tkinter as tk


class MatrixRain(tk.Canvas):
    """CHUVA MATRIX - IGUAL AO FILME"""
    
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
        """INICIALIZA A CHUVA - ESTILO FILME"""
        self.update_idletasks()
        largura = max(self.winfo_width(), 800)
        altura = max(self.winfo_height(), 600)
        
        # 🌟 COLUNAS BEM PRÓXIMAS (DENSAS IGUAL AO FILME)
        num_colunas = largura // 12  # BEM DENSAS!
        
        self.colunas = []
        for _ in range(num_colunas):
            # 🌟 TODAS COM A MESMA VELOCIDADE (UNIFORME IGUAL AO FILME)
            velocidade = 0.5  # VELOCIDADE CONSTANTE E LENTA
            
            self.colunas.append({
                'x': random.randint(0, largura),
                'y': random.randint(-altura, altura),
                'vel': velocidade,
                'tam': random.randint(15, 40)  # COLUNAS BEM LONGAS
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
            # 🌟 MOVIMENTO UNIFORME E LENTO
            col['y'] += col['vel']
            
            if col['y'] > altura + 50:
                col['y'] = random.randint(-50, -10)
                col['x'] = random.randint(0, largura)
                col['tam'] = random.randint(15, 40)
            
            # 🌟 DESENHA A COLUNA INTEIRA DE UMA VEZ (CASCATA CONTÍNUA)
            for i in range(col['tam']):
                y = col['y'] - (i * 16)  # ESPAÇAMENTO ENTRE CARACTERES
                if y < -10 or y > altura:
                    continue
                
                char = random.choice(self.CARACTERES)
                
                # 🌟 GRADIENTE DE VERDE (CABEÇA BRILHANTE, CAUSA ESCURA)
                if i == 0:
                    cor = '#00ff41'  # BRILHO MÁXIMO
                    size = 14
                elif i == 1:
                    cor = '#00dd33'
                    size = 13
                elif i == 2:
                    cor = '#00bb22'
                    size = 12
                else:
                    # ESCURECE GRADUALMENTE
                    v = max(0, 1.0 - (i / col['tam']))
                    g = int(180 * v)
                    cor = f'#00{g:02x}00'
                    size = 11
                
                # 🌟 EFEITO DE BRILHO ALEATÓRIO NA CABEÇA (IGUAL AO FILME)
                if i == 0 and random.random() < 0.08:
                    cor = '#88ff88'
                    size = 16
                
                self.create_text(
                    col['x'], y,
                    text=char,
                    fill=cor,
                    font=('Consolas', size, 'bold')
                )
        
        # 🌟 FRAME MAIS LENTO = 60ms (16 FPS) - FLUIDO E CINEMATOGRÁFICO
        self.after(60, self._animar)