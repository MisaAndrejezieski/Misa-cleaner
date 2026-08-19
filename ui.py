"""
MISA-CLEANER - Interface Matrix Imersiva
COM EFEITO MATRIX EM TELA CHEIA DURANTE A VARREDURA
"""
import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List, Optional

from logger import Logger, LogNivel
from matrix_rain import MatrixFullscreen  # 🔧 IMPORTADO CORRETAMENTE
from scanner import Scanner
