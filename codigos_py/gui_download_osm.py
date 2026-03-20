import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import sys
import os
from download_osm_data import download_osm_transport_data

class RedirectText:
    """Redireciona o stdout para um widget de texto do Tkinter."""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

def browse_output(entry):
    """Abre o seletor de arquivos para escolher o local e nome de saída."""
    filename = filedialog.asksaveasfilename(
        defaultextension="",
        initialfile="osm_data",
        title="Escolha onde salvar os arquivos",
        filetypes=[("Todos os arquivos", "*.*")]
    )
    if filename:
        entry.delete(0, tk.END)
        entry.insert(0, filename)

def start_download(place, output, category, log_widget, btn):
    """Executa o download em uma thread separada."""
    btn.config(state=tk.DISABLED)
    log_widget.delete(1.0, tk.END)
    
    # Redireciona o print para o log da interface
    old_stdout = sys.stdout
    sys.stdout = RedirectText(log_widget)
    
    def task():
        try:
            download_osm_transport_data(place, output, category)
            messagebox.showinfo("Sucesso", f"Download concluído!\nArquivos salvos com base em: {output}")
        except Exception as e:
            print(f"\nErro inesperado: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        finally:
            sys.stdout = old_stdout
            btn.config(state=tk.NORMAL)

    threading.Thread(target=task).start()

def create_gui():
    root = tk.Tk()
    root.title("OSM Transport Downloader")
    root.geometry("640x550")
    root.configure(padx=20, pady=20)

    # Estilo
    style = ttk.Style()
    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("TButton", font=("Segoe UI", 10, "bold"))

    # Campos de Entrada
    ttk.Label(root, text="Local (Ex: Rio de Janeiro):").pack(anchor=tk.W, pady=(0, 5))
    entry_place = ttk.Entry(root, width=75)
    entry_place.insert(0, "Rio de Janeiro")
    entry_place.pack(pady=(0, 15))

    ttk.Label(root, text="Onde salvar os arquivos (Nome Base):").pack(anchor=tk.W, pady=(0, 5))
    output_frame = ttk.Frame(root)
    output_frame.pack(fill=tk.X, pady=(0, 15))
    
    entry_output = ttk.Entry(output_frame, width=62)
    entry_output.insert(0, "osm_data")
    entry_output.pack(side=tk.LEFT, padx=(0, 5))
    
    btn_browse = ttk.Button(output_frame, text="Procurar...", command=lambda: browse_output(entry_output))
    btn_browse.pack(side=tk.LEFT)

    ttk.Label(root, text="Categoria de Dados:").pack(anchor=tk.W, pady=(0, 5))
    cat_var = tk.StringVar(value="all")
    categories = [
        ("Tudo", "all"),
        ("Pontos de Parada/Estações", "stops"),
        ("Rotas de Transporte", "routes"),
        ("Infraestrutura Cicloviária", "cycling"),
        ("Corredores BRT/Ônibus", "corridors")
    ]
    
    combo_category = ttk.Combobox(root, values=[c[0] for c in categories], state="readonly", width=72)
    combo_category.set("Tudo")
    combo_category.pack(pady=(0, 20))

    # Log/Status
    ttk.Label(root, text="Status do Processamento:").pack(anchor=tk.W, pady=(0, 5))
    log_text = tk.Text(root, height=10, width=75, font=("Consolas", 9))
    log_text.pack(pady=(0, 20))

    # Botão de Ação
    def on_click():
        place = entry_place.get()
        output = entry_output.get()
        # Mapeia o nome amigável para a chave da categoria
        selected_name = combo_category.get()
        category = next(c[1] for c in categories if c[0] == selected_name)
        
        if not place or not output:
            messagebox.showwarning("Aviso", "Por favor, preencha o Local e o local de salvamento.")
            return
            
        start_download(place, output, category, log_text, btn_download)

    btn_download = ttk.Button(root, text="BAIXAR DADOS OSM", command=on_click)
    btn_download.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
