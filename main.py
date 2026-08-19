import tkinter as tk
from ui import MisaCleanerUI

def main():
    root = tk.Tk()
    app = MisaCleanerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()