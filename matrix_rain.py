"""
MISA-CLEANER - Efeito Matrix Rain
VERSÃO 4.0 - Cancelamento correto de after, sem fallback hardcoded,
             sem place() no __init__, responde a resize.
"""
import random
import tkinter as tk


class MatrixRain(tk.Canvas):
    # Constantes (antes eram números mágicos espalhados)
    CARACTERES = [
        'A','B','C','D','E','F','G','H','I','J','K','L','M',
        'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
        'a','b','c','d','e','f','g','h','i','j','k','l','m',
        'n','o','p','q','r','s','t','u','v','w','x','y','z',
        '0','1','2','3','4','5','6','7','8','9',
        '日','本','語','の','文','字','を','使','っ','て',
        '!','@','#','$','%','&','*','+','=','~'
    ]

    LARGURA_CARACTERE = 8       # px entre colunas
    ESPACAMENTO_VERTICAL = 8    # px entre caracteres na coluna
    MAX_CARACTERES_COLUNA = 30  # caracteres máximos por coluna
    INTERVALO_FRAME_MS = 25     # ~40 FPS
    TAMANHO_MIN_COLUNA = 10
    TAMANHO_MAX_COLUNA = 30
    VELOCIDADE_MIN = 4.0
    VELOCIDADE_MAX = 8.0
    CHANCE_TROCA_CARACTERE = 0.04

    def __init__(self, parent, **kwargs):
        kwargs.setdefault('bg', '#000000')
        kwargs.setdefault('highlightthickness', 0)
        super().__init__(parent, **kwargs)

        self.animando = True
        self.colunas = []
        self.quadro = 0
        self._after_id = None
        self._ultimo_tamanho = (0, 0)

        self.bind('<Configure>', self._on_configure)

        self.after(50, self._primeira_criacao)
        self._animar()

    def _primeira_criacao(self):
        if not self.colunas and self.animando:
            self._criar_colunas()

    def _on_configure(self, event):
        novo_tamanho = (event.width, event.height)
        if novo_tamanho != self._ultimo_tamanho and event.width > 1 and event.height > 1:
            self._ultimo_tamanho = novo_tamanho
            self._criar_colunas()

    def _criar_colunas(self):
        largura = self.winfo_width()
        altura = self.winfo_height()

        if largura <= 1 or altura <= 1:
            return

        self.delete('all')
        self.colunas = []

        num_colunas = max(1, largura // self.LARGURA_CARACTERE)

        for _ in range(num_colunas):
            tamanho = random.randint(self.TAMANHO_MIN_COLUNA, self.TAMANHO_MAX_COLUNA)
            col = {
                'x': random.randint(0, largura),
                'y': random.randint(-altura, 0),
                'vel': random.uniform(self.VELOCIDADE_MIN, self.VELOCIDADE_MAX),
                'tam': tamanho,
                'chars': [random.choice(self.CARACTERES) for _ in range(tamanho)],
                'itens': [],
                'visiveis': [False] * self.MAX_CARACTERES_COLUNA
            }

            for i in range(self.MAX_CARACTERES_COLUNA):
                if i == 0:
                    cor, tamanho_fonte = '#00ff41', 14
                elif i == 1:
                    cor, tamanho_fonte = '#00dd33', 13
                elif i == 2:
                    cor, tamanho_fonte = '#00bb22', 12
                else:
                    valor = max(0.1, 1.0 - (i / self.MAX_CARACTERES_COLUNA))
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

            self.colunas.append(col)

    def _animar(self):
        if not self.animando:
            return

        self.quadro += 1
        largura = self.winfo_width()
        altura = self.winfo_height()

        if largura <= 1 or altura <= 1:
            self._after_id = self.after(self.INTERVALO_FRAME_MS, self._animar)
            return

        for col in self.colunas:
            col['y'] += col['vel']

            if col['y'] > altura + 50:
                col['y'] = random.randint(-100, -20)
                col['x'] = random.randint(0, largura)
                col['vel'] = random.uniform(self.VELOCIDADE_MIN, self.VELOCIDADE_MAX)
                col['tam'] = random.randint(self.TAMANHO_MIN_COLUNA, self.TAMANHO_MAX_COLUNA)
                col['chars'] = [random.choice(self.CARACTERES) for _ in range(col['tam'])]
                col['visiveis'] = [False] * self.MAX_CARACTERES_COLUNA
                for item in col['itens']:
                    self.itemconfigure(item, state=tk.HIDDEN)

            for i, item in enumerate(col['itens']):
                y = col['y'] - (i * self.ESPACAMENTO_VERTICAL)

                if y < -10 or y > altura:
                    if col['visiveis'][i]:
                        self.itemconfigure(item, state=tk.HIDDEN)
                        col['visiveis'][i] = False
                    continue

                if i >= col['tam']:
                    if col['visiveis'][i]:
                        self.itemconfigure(item, state=tk.HIDDEN)
                        col['visiveis'][i] = False
                    continue

                if not col['visiveis'][i]:
                    self.coords(item, col['x'], y)
                    self.itemconfigure(item, text=col['chars'][i], state=tk.NORMAL)
                    col['visiveis'][i] = True
                else:
                    self.move(item, 0, col['vel'])

                if self.quadro % 4 == 0 and random.random() < self.CHANCE_TROCA_CARACTERE:
                    col['chars'][i] = random.choice(self.CARACTERES)
                    self.itemconfigure(item, text=col['chars'][i])

        self._after_id = self.after(self.INTERVALO_FRAME_MS, self._animar)

    def parar(self):
        """Para a animação e cancela o after pendente"""
        self.animando = False
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None