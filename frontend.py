import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from code_smells_detection import CodeSmellDetector

class CodeSmellApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Smell Detector")
        self.root.geometry("600x450")

        # Style Configuration
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 10), padding=5)
        style.configure("TLabel", font=("Helvetica", 11))
        style.configure("TEntry", font=("Helvetica", 10))

        # Main Frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Directory Selection Section
        dir_frame = ttk.LabelFrame(main_frame, text="Directory Selection", padding="10")
        dir_frame.pack(fill=tk.X, padx=5, pady=5)

        self.label = ttk.Label(dir_frame, text="Select a directory to scan for code smells:")
        self.label.pack(anchor=tk.W, pady=5)

        dir_entry_frame = ttk.Frame(dir_frame)
        dir_entry_frame.pack(fill=tk.X, pady=5)

        self.directory_entry = ttk.Entry(dir_entry_frame, width=50)
        self.directory_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.browse_button = ttk.Button(dir_entry_frame, text="Browse", command=self.browse_directory)
        self.browse_button.pack(side=tk.RIGHT)

        # Scan Button
        self.scan_button = ttk.Button(main_frame, text="Scan for Smells", command=self.scan_smells)
        self.scan_button.pack(pady=10)

        # Results Section
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.result_text = tk.Text(results_frame, wrap=tk.WORD, height=15, font=("Helvetica", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Clear Button
        self.clear_button = ttk.Button(main_frame, text="Clear Results", command=self.clear_results)
        self.clear_button.pack(pady=10)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, directory)

    def scan_smells(self):
        directory = self.directory_entry.get().strip()
        if not directory:
            messagebox.showerror("Error", "Please select a directory to scan.")
            return

        try:
            detector = CodeSmellDetector(directory)
            smells, code_smell_count = detector.scan_for_smells()  # Capture smells and count

            self.result_text.delete(1.0, tk.END)
            if smells:
                self.result_text.insert(tk.END, "Code smells detected:\n\n")
                for smell in smells:
                    self.result_text.insert(tk.END, f"{smell}\n")
            else:
                self.result_text.insert(tk.END, "No code smells detected.\n")
            self.result_text.insert(tk.END, f"\nTotal code smells detected: {code_smell_count}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def clear_results(self):
        self.result_text.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeSmellApp(root)
    root.mainloop()
