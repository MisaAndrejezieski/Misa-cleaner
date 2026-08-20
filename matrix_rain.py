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
        for _ in range(largura // 10):
            tamanho = random.randint(10, 30)
            self.colunas.append({
                'x': random.randint(0, largura),
                'y': random.randint(-altura, 0),
                'vel': random.uniform(2.5, 5.5),
                'tam': tamanho,
                'chars': [random.choice(self.CARACTERES) for _ in range(tamanho)],
                'itens': []
            })

            col = self.colunas[-1]
            for i in range(30):
                if i == 0:
                    cor, tamanho_fonte = '#00ff41', 14
                elif i == 1:
                    cor, tamanho_fonte = '#00dd33', 13
                elif i == 2:
                    cor, tamanho_fonte = '#00bb22', 12
                else:
                    valor = max(0.1, 1.0 - (i / 30))
                    verde = int(180 * valor)
                    cor, tamanho_fonte = f'#00{verde:02x}00', 11

                item = self.create_text(
                    0, 0,
                    text='',
                    fill=cor,
                    font=('Consolas', tamanho_fonte, 'bold'),
                    state=tk.HIDDEN
                )
                col['itens'].append(item)

    def _animar(self):
        if not self.animando:
            return
        largura = max(self.winfo_width(), 800)
        altura = max(self.winfo_height(), 600)

        for col in self.colunas:
            col['y'] += col['vel']
            if col['y'] > altura + 50:
                col['y'] = random.randint(-100, -20)
                col['x'] = random.randint(0, largura)
                col['vel'] = random.uniform(2.5, 5.5)
                col['tam'] = random.randint(10, 30)
                col['chars'] = [random.choice(self.CARACTERES) for _ in range(col['tam'])]

            for i, item in enumerate(col['itens']):
                y = col['y'] - (i * 11)
                if y < -10 or y > altura:
                    self.itemconfigure(item, state=tk.HIDDEN)
                    continue
                if i >= col['tam']:
                    self.itemconfigure(item, state=tk.HIDDEN)
                    continue

                self.coords(item, col['x'], y)
                self.itemconfigure(item, text=col['chars'][i], state=tk.NORMAL)

        self.after(33, self._animar)

    def parar(self):
        self.animando = False