import tkinter as tk
from tkinter import filedialog, messagebox

class GUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Processamento de listas")

        self.path_var1 = tk.StringVar(value="")
        self.path_var2 = tk.StringVar(value="")
        self.path_var3 = tk.StringVar(value="")

        self.create_widgets()

    def create_widgets(self):
        description1 = tk.Label(self.root, text="Lista (formato xls):")
        description1.pack()

        self.path_entry1 = tk.Entry(self.root, textvariable=self.path_var1)
        self.path_entry1.pack(fill=tk.X, padx=10)

        browse_button1 = tk.Button(self.root, text="Buscar", command=self.browse_path1)
        browse_button1.pack()

        description2 = tk.Label(self.root, text="Destino dos arquivos:")
        description2.pack()

        self.path_entry2 = tk.Entry(self.root, textvariable=self.path_var2)
        self.path_entry2.pack(fill=tk.X, padx=10)

        browse_button2 = tk.Button(self.root, text="Buscar", command=self.browse_path2)
        browse_button2.pack()

        description3 = tk.Label(self.root, text="Data (dd/mm/aaaa):")
        description3.pack()
        self.path_entry3 = tk.Entry(self.root, textvariable=self.path_var3)
        self.path_entry3.pack(fill=tk.X, padx=10)
        browse_button3 = tk.Button(self.root, text="Buscar", command=self.browse_path3)
        browse_button3.pack()

        run_button = tk.Button(self.root, text="Rodar", command=self.run_program)
        run_button.pack()

    def browse_path1(self):
        path = filedialog.askopenfilename()
        # Lista
        self.path_var1.set(path)

    def browse_path2(self):
        path = filedialog.askdirectory()
        # Destino
        self.path_var2.set(path)

    def browse_path3(self):
        path = filedialog.askdirectory()
        # Acervo
        self.path_var3.set(path)

    def run_program(self):
        if not self.path_var1.get() or not self.path_var2.get() or not self.path_var3.get():
            messagebox.showerror("Input inválido!", "Por favor, preencha todos os campos!")
            return
        print("Iniciando procedimento.")
        self.root.destroy()

    def get_paths(self):
        return self.path_var1.get(), self.path_var2.get(), self.path_var3.get()

def abrir_GUI():
    root = tk.Tk()
    gui = GUI(root)
    root.title("Gerador de adesivos")
    root.geometry("400x300")
    root.mainloop()
    lista, destino, data = gui.get_paths()
    return lista, destino, data