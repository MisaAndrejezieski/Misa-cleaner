import random
import tkinter as tk


class MatrixRain(tk.Canvas):
    CARACTERES = [
        '0','1','2','3','4','5','6','7','8','9',
        '日','本','語','の','文','字','を','使','っ','て',
        '!','@','#','$','%','&','*','+','=','~'
    ]

    def __init__(self, parent):
        super().__init__(parent, bg='#000000', highlightthickness=0)
        self.animando = True
        self.colunas = []
        self.place(x=0, y=0, relwidth=1, relheight=1)
        self._criar_colunas()
        self._animar()

    def _criar_colunas(self):
        self.update_idletasks()
        largura = max(self.winfo_width(), 800)
        altura = max(self.winfo_height(), 600)
        self.colunas = []
        for _ in range(largura // 14):
            tamanho = random.randint(10, 30)
            self.colunas.append({
                'x': random.randint(0, largura),
                'y': random.randint(-altura, 0),
                'vel': random.uniform(1.5, 4.0),
                'tam': tamanho,
                'chars': [random.choice(self.CARACTERES) for _ in range(tamanho)]
            })

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
                col['y'] = random.randint(-100, -20)
                col['x'] = random.randint(0, largura)
                col['vel'] = random.uniform(1.5, 4.0)
                col['tam'] = random.randint(10, 30)
                col['chars'] = [random.choice(self.CARACTERES) for _ in range(col['tam'])]

            for i in range(col['tam']):
                y = col['y'] - (i * 16)
                if y < -10 or y > altura:
                    continue
                if i == 0:
                    cor, size = '#00ff41', 14
                elif i == 1:
                    cor, size = '#00dd33', 13
                elif i == 2:
                    cor, size = '#00bb22', 12
                else:
                    v = max(0.1, 1.0 - (i / col['tam']))
                    g = int(180 * v)
                    cor, size = f'#00{g:02x}00', 11
                self.create_text(
                    col['x'], y,
                    text=col['chars'][i],
                    fill=cor,
                    font=('Consolas', size, 'bold')
                )
        self.after(50, self._animar)

    def parar(self):
        self.animando = False