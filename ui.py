# ============================================
# 🌟 SOMENTE ESTAS DUAS FUNÇÕES IMPORTAM!
# ============================================

def _ativar_matrix(self):
    """🌟 TELA INTEIRA VIROU MATRIX!"""
    # Remove a interface
    self.main_frame.pack_forget()
    
    # Cria a Matrix em tela cheia
    self.matrix = MatrixFullscreen(self.root)
    self.matrix.iniciar()
    
    # Mensagem inicial
    self.matrix.escrever("╔══════════════════════════════════════════════════╗", "INFO")
    self.matrix.escrever("║     🌟 M A T R I X   M O D E   A T I V O     ║", "SUCESSO")
    self.matrix.escrever("╚══════════════════════════════════════════════════╝", "INFO")
    self.matrix.escrever("")
    self.matrix.escrever(">> A CHUVA DE CÓDIGO ESTÁ CAINDO...", "INFO")
    self.matrix.escrever(">> VARREDURA EM ANDAMENTO...", "INFO")

def _desativar_matrix(self):
    """🌟 VOLTA PARA A INTERFACE NORMAL"""
    if hasattr(self, 'matrix'):
        self.matrix.destruir()
        self.matrix = None
    
    # Restaura a interface
    self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
    self.main_frame.lift()
    self.root.update()