import csv
import os
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import shutil
import logging
import re

logging.basicConfig(
    filename='optic_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def check_file_size(filepath):
    try:
        size = os.path.getsize(filepath)
        return size <= MAX_FILE_SIZE
    except Exception as e:
        logging.error(f"Σφάλμα κατά τον έλεγχο μεγέθους αρχείου: {str(e)}")
        return False

def create_backup(filepath):
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"{os.path.basename(filepath)}_{timestamp}")
        shutil.copy2(filepath, backup_path)
        logging.info(f"Δημιουργήθηκε αντίγραφο ασφαλείας: {backup_path}")
        return True
    except Exception as e:
        logging.error(f"Σφάλμα κατά τη δημιουργία αντιγράφου ασφαλείας: {str(e)}")
        return False

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def open_file_safely(filepath):
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError("Το αρχείο δεν βρέθηκε!")
        os.startfile(filepath)
        return True
    except Exception as e:
        logging.error(f"Σφάλμα κατά το άνοιγμα του αρχείου {filepath}: {str(e)}")
        raise

def validate_phone(phone):
    phone = ''.join(filter(str.isdigit, phone))
    if len(phone) == 10 and (phone.startswith('2') or phone.startswith('6')):
        return True
    return False

def validate_email(email):
    if not email:
        return True
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

FILE_NAME = "πελάτες.csv"
INVENTORY_FILE = "αποθήκη.csv"
DOCUMENTS_DIR = "έγγραφα πελατών"
BACKUP_DIR = "backup"
MAX_FILE_SIZE = 10 * 1024 * 1024  

CUSTOMER_HEADERS = ["Όνομα", "Επώνυμο", "Τηλέφωνο", "Email", "Διεύθυνση", "Έγγραφα"]
INVENTORY_HEADERS = ["Όνομα Προϊόντος", "Κατηγορία", "Ποσότητα", "Τιμή"]

for file_name, headers in [(FILE_NAME, CUSTOMER_HEADERS),
                         (INVENTORY_FILE, INVENTORY_HEADERS)]:
    if not os.path.exists(file_name):
        with open(file_name, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)

class OpticalSystem:
    def __init__(self):
        try:
            if not os.path.exists(DOCUMENTS_DIR):
                os.makedirs(DOCUMENTS_DIR)
                logging.info(f"Δημιουργήθηκε ο φάκελος {DOCUMENTS_DIR}")

            if not os.path.exists(FILE_NAME):
                with open(FILE_NAME, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(CUSTOMER_HEADERS)
                logging.info(f"Δημιουργήθηκε το αρχείο {FILE_NAME}")

            if not os.path.exists(INVENTORY_FILE):
                with open(INVENTORY_FILE, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(INVENTORY_HEADERS)
                logging.info(f"Δημιουργήθηκε το αρχείο {INVENTORY_FILE}")

            logging.info("Εκκίνηση του συστήματος")
        except Exception as e:
            logging.error(f"Σφάλμα κατά την αρχικοποίηση: {str(e)}")
            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την αρχικοποίηση: {str(e)}")
            raise

        self.root = tk.Tk()
        self.root.title("Σύστημα Διαχείρισης Οπτικών")
        self.root.state('zoomed')  
        
        self.create_customer_section()
        self.create_inventory_section()
        
        self.fortose_kai_emfanise()
        self.fortose_apothiki()

    def create_customer_section(self):
        label_pelates = tk.Label(self.root, text="\n--- Διαχείριση Πελατών ---", font=("Arial", 14, "bold"))
        label_pelates.pack()

        frame_pelates = tk.Frame(self.root)
        frame_pelates.pack(pady=10)

        tk.Button(frame_pelates, text="Καταχώρηση Πελάτη", command=self.kataxwrisi_pelati).grid(row=0, column=0, padx=5)
        tk.Button(frame_pelates, text="Αναζήτηση Πελάτη", command=self.anazitisi_pelati).grid(row=0, column=1, padx=5)
        tk.Button(frame_pelates, text="Διόρθωση Πελάτη", command=self.diorthosi_pelati).grid(row=0, column=2, padx=5)
        tk.Button(frame_pelates, text="Διαγραφή Πελάτη", command=self.diagrafi_pelati).grid(row=0, column=3, padx=5)
        tk.Button(frame_pelates, text="Ανανέωση Λίστας", command=self.fortose_kai_emfanise).grid(row=0, column=4, padx=5)

        self.btn_open_doc = tk.Button(frame_pelates, text="Άνοιγμα Εγγράφου", command=self.anigma_egrafou, state='disabled')
        self.btn_open_doc.grid(row=0, column=5, padx=5)

        cols = ("Όνομα", "Επώνυμο", "Τηλέφωνο", "Email", "Διεύθυνση", "Έγγραφα")
        self.tree_pelates = ttk.Treeview(self.root, columns=cols, show='headings')
        
        col_widths = {
            "Όνομα": 120,
            "Επώνυμο": 120,
            "Τηλέφωνο": 100,
            "Email": 180,
            "Διεύθυνση": 200,
            "Έγγραφα": 250
        }
        
        for col in cols:
            self.tree_pelates.heading(col, text=col)
            self.tree_pelates.column(col, width=col_widths[col])
        
        self.tree_pelates.pack(expand=True, fill='both', padx=10)

        self.tree_pelates.bind('<<TreeviewSelect>>', self.on_select_customer)

    def create_inventory_section(self):
        label_apothiki = tk.Label(self.root, text="\n--- Διαχείριση Αποθήκης ---", font=("Arial", 14, "bold"))
        label_apothiki.pack()

        frame_apothiki = tk.Frame(self.root)
        frame_apothiki.pack(pady=10)

        tk.Button(frame_apothiki, text="Καταχώρηση Προϊόντος", command=self.prosthiki_proiontos).grid(row=0, column=0, padx=5)
        tk.Button(frame_apothiki, text="Πώληση Προϊόντος", command=self.pwlisi_proiontos).grid(row=0, column=1, padx=5)
        tk.Button(frame_apothiki, text="Διαγραφή Προϊόντος", command=self.diagrafi_proiontos).grid(row=0, column=2, padx=5)
        tk.Button(frame_apothiki, text="Ανανέωση Αποθήκης", command=self.fortose_apothiki).grid(row=0, column=3, padx=5)

        cols_apothiki = ("Όνομα Προϊόντος", "Κατηγορία", "Ποσότητα", "Τιμή")
        self.tree_apothiki = ttk.Treeview(self.root, columns=cols_apothiki, show='headings')
        for col in cols_apothiki:
            self.tree_apothiki.heading(col, text=col)
            self.tree_apothiki.column(col, width=200)
        self.tree_apothiki.pack(expand=True, fill='both', padx=10)

    def kataxwrisi_pelati(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Καταχώρηση Πελάτη")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.focus_set()
        center_window(dialog)

        input_frame = tk.Frame(dialog)
        input_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(input_frame, text="Όνομα:").pack(pady=5)
        onoma = tk.Entry(input_frame, width=40)
        onoma.pack()

        tk.Label(input_frame, text="Επώνυμο:").pack(pady=5)
        eponimo = tk.Entry(input_frame, width=40)
        eponimo.pack()

        tk.Label(input_frame, text="Τηλέφωνο:").pack(pady=5)
        tilefono = tk.Entry(input_frame, width=40)
        tilefono.pack()

        tk.Label(input_frame, text="Email:").pack(pady=5)
        email = tk.Entry(input_frame, width=40)
        email.pack()

        tk.Label(input_frame, text="Διεύθυνση:").pack(pady=5)
        dieuthinsi = tk.Entry(input_frame, width=40)
        dieuthinsi.pack()

        docs_frame = tk.Frame(dialog)
        docs_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(docs_frame, text="Έγγραφα:").pack(pady=5)
        docs_listbox = tk.Listbox(docs_frame, height=5, width=50)
        docs_listbox.pack()

        def check_duplicate_customer(name, surname, phone, email_val):
            with open(FILE_NAME, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if (row[0].lower() == name.lower() and row[1].lower() == surname.lower()) or \
                       row[2] == phone or \
                       (email_val and row[3] and row[3].lower() == email_val.lower()):
                        return True
            return False

        def open_document(event):
            selected = docs_listbox.curselection()
            if selected:
                doc_name = docs_listbox.get(selected[0])
                try:
                    doc_path = os.path.join(DOCUMENTS_DIR, doc_name)
                    if not os.path.exists(doc_path):
                        messagebox.showerror("Σφάλμα", "Το αρχείο δεν βρέθηκε!")
                        return
                    
                    if not os.access(doc_path, os.R_OK):
                        messagebox.showerror("Σφάλμα", "Δεν έχετε δικαιώματα πρόσβασης στο αρχείο!")
                        return
                        
                    try:
                        with open(doc_path, 'rb') as f:
                            pass
                    except PermissionError:
                        messagebox.showerror("Σφάλμα", "Το αρχείο είναι κλειδωμένο από άλλο πρόγραμμα!")
                        return
                        
                    os.startfile(doc_path)
                except Exception as e:
                    messagebox.showerror("Σφάλμα", f"Δεν ήταν δυνατό το άνοιγμα του εγγράφου: {str(e)}")

        docs_listbox.bind('<Double-Button-1>', open_document)

        def add_document(self):
            file_path = filedialog.askopenfilename(
                title="Επιλογή Εγγράφου",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    if not check_file_size(file_path):
                        messagebox.showerror("Σφάλμα", 
                            f"Το αρχείο είναι πολύ μεγάλο!\nΜέγιστο επιτρεπτό μέγεθος: {MAX_FILE_SIZE/1024/1024:.1f}MB")
                        return
                        
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(DOCUMENTS_DIR, filename)
                    
                    if os.path.exists(dest_path):
                        if not messagebox.askyesno("Επιβεβαίωση", 
                            "Το αρχείο υπάρχει ήδη. Θέλετε να το αντικαταστήσετε;"):
                            return
                    
                    shutil.copy2(file_path, dest_path)
                    docs_listbox.insert(tk.END, filename)
                except Exception as e:
                    messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την προσθήκη του εγγράφου: {str(e)}")

        def save():
            try:
                name = onoma.get().strip()
                surname = eponimo.get().strip()
                phone = tilefono.get().strip()
                email_val = email.get().strip()
                address = dieuthinsi.get().strip()

                if not name or not phone:
                    logging.warning("Προσπάθεια αποθήκευσης πελάτη χωρίς υποχρεωτικά πεδία")
                    messagebox.showerror("Σφάλμα", "Το όνομα και το τηλέφωνο είναι υποχρεωτικά!")
                    return

                if not validate_phone(phone):
                    logging.warning(f"Προσπάθεια αποθήκευσης πελάτη με μη έγκυρο τηλέφωνο: {phone}")
                    messagebox.showerror("Σφάλμα", 
                        "Το τηλέφωνο πρέπει να είναι 10 ψηφία και να ξεκινάει:\n" + 
                        "- με 69 για κινητό\n" + 
                        "- με 2 για σταθερό")
                    return

                if email_val and not validate_email(email_val):
                    logging.warning(f"Προσπάθεια αποθήκευσης πελάτη με μη έγκυρο email: {email_val}")
                    messagebox.showerror("Σφάλμα", "Το email πρέπει να έχει τη μορφή: onoma@domain.com")
                    return

                if check_duplicate_customer(name, surname, phone, email_val):
                    logging.warning(f"Προσπάθεια διπλής καταχώρησης πελάτη: {name} {surname}")
                    messagebox.showerror("Σφάλμα", 
                        "Υπάρχει ήδη πελάτης με τα ίδια στοιχεία!\n" +
                        "(έλεγχος για ίδιο όνομα/επώνυμο, τηλέφωνο ή email)")
                    return

                documents = []
                for i in range(docs_listbox.size()):
                    documents.append(docs_listbox.get(i))
                documents_str = ", ".join(documents) if documents else ""

                with open(FILE_NAME, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([name, surname, phone, email_val, address, documents_str])

                logging.info(f"Προστέθηκε νέος πελάτης: {name} {surname}")
                messagebox.showinfo("Επιτυχία", "Ο πελάτης καταχωρήθηκε επιτυχώς!")
                dialog.destroy()
                self.fortose_kai_emfanise()
            except Exception as e:
                logging.error(f"Σφάλμα κατά την αποθήκευση πελάτη: {str(e)}")
                messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την αποθήκευση: {str(e)}")

        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(pady=10, padx=10)

        tk.Button(buttons_frame, text="Προσθήκη Εγγράφου", command=add_document, bg='blue', fg='white', width=20).pack(pady=5)
        tk.Button(buttons_frame, text="Αποθήκευση", command=save, bg='green', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Ακύρωση", command=dialog.destroy, bg='red', fg='white', width=15).pack(side=tk.LEFT, padx=5)

    def diagrafi_pelati(self):
        try:
            selected = self.tree_pelates.selection()
            if not selected:
                logging.warning("Προσπάθεια διαγραφής χωρίς επιλεγμένο πελάτη")
                messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε έναν πελάτη για διαγραφή")
                return

            item = self.tree_pelates.item(selected[0])
            values = item['values']

            if messagebox.askyesno("Επιβεβαίωση", f"Είστε σίγουροι ότι θέλετε να διαγράψετε τον πελάτη {values[0]} {values[1]}?"):
                if not create_backup(FILE_NAME):
                    if not messagebox.askyesno("Προειδοποίηση", 
                        "Δεν ήταν δυνατή η δημιουργία αντιγράφου ασφαλείας.\nΘέλετε να συνεχίσετε με τη διαγραφή;"):
                        return
                
                if len(values) > 5 and values[5]:
                    docs = values[5].split(", ")
                    missing_docs = []
                    for doc in docs:
                        try:
                            doc_path = os.path.join(DOCUMENTS_DIR, doc)
                            if os.path.exists(doc_path):
                                os.remove(doc_path)
                                logging.info(f"Διαγράφηκε το έγγραφο: {doc}")
                            else:
                                missing_docs.append(doc)
                                logging.warning(f"Το έγγραφο {doc} δεν βρέθηκε κατά τη διαγραφή του πελάτη {values[0]} {values[1]}")
                        except Exception as e:
                            logging.error(f"Σφάλμα κατά τη διαγραφή εγγράφου {doc}: {str(e)}")
                            missing_docs.append(doc)
                    
                    if missing_docs:
                        messagebox.showwarning("Προειδοποίηση", 
                            f"Τα παρακάτω έγγραφα δεν βρέθηκαν ή δεν μπόρεσαν να διαγραφούν:\n" + 
                            "\n".join(missing_docs))

                rows = []
                with open(FILE_NAME, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    header = next(reader)
                    for row in reader:
                        if row[0] != values[0] or row[1] != values[1]:
                            rows.append(row)

                with open(FILE_NAME, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(header)
                    writer.writerows(rows)

                logging.info(f"Διαγράφηκε ο πελάτης: {values[0]} {values[1]}")
                messagebox.showinfo("Επιτυχία", "Ο πελάτης διαγράφηκε επιτυχώς!")
                self.fortose_kai_emfanise()
        except Exception as e:
            logging.error(f"Σφάλμα κατά τη διαγραφή πελάτη: {str(e)}")
            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά τη διαγραφή: {str(e)}")

    def diorthosi_pelati(self):
        selected = self.tree_pelates.selection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε έναν πελάτη για διόρθωση")
            return

        item = self.tree_pelates.item(selected[0])
        values = item['values']

        dialog = tk.Toplevel(self.root)
        dialog.title("Διόρθωση Πελάτη")
        dialog.geometry("400x600")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.focus_set()

        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

        input_frame = tk.Frame(dialog)
        input_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(input_frame, text="Όνομα:").pack(pady=5)
        onoma = tk.Entry(input_frame, width=40)
        onoma.insert(0, values[0])
        onoma.pack()

        tk.Label(input_frame, text="Επώνυμο:").pack(pady=5)
        eponimo = tk.Entry(input_frame, width=40)
        eponimo.insert(0, values[1])
        eponimo.pack()

        tk.Label(input_frame, text="Τηλέφωνο:").pack(pady=5)
        tilefono = tk.Entry(input_frame, width=40)
        tilefono.insert(0, values[2])
        tilefono.pack()

        tk.Label(input_frame, text="Email:").pack(pady=5)
        email = tk.Entry(input_frame, width=40)
        email.insert(0, values[3] if len(values) > 3 else "")
        email.pack()

        tk.Label(input_frame, text="Διεύθυνση:").pack(pady=5)
        dieuthinsi = tk.Entry(input_frame, width=40)
        dieuthinsi.insert(0, values[4] if len(values) > 4 else "")
        dieuthinsi.pack()

        docs_frame = tk.Frame(dialog)
        docs_frame.pack(pady=10, fill='x')
        
        tk.Label(docs_frame, text="Έγγραφα Πελάτη:", font=("Arial", 10, "bold")).pack()
        
        docs_listbox = tk.Listbox(docs_frame, height=5)
        docs_listbox.pack(fill='x', padx=5)
        
        if len(values) > 5 and values[5]:
            for doc in values[5].split(", "):
                if doc:
                    docs_listbox.insert(tk.END, doc)

        def open_document(event):
            selection = docs_listbox.curselection()
            if selection:
                doc_name = docs_listbox.get(selection[0])
                try:
                    doc_path = os.path.join(DOCUMENTS_DIR, doc_name)
                    open_file_safely(doc_path)
                except Exception as e:
                    messagebox.showerror("Σφάλμα", str(e))

        docs_listbox.bind('<Double-Button-1>', open_document)

        def add_document():
            file_path = filedialog.askopenfilename(
                title="Επιλέξτε έγγραφο",
                filetypes=[("PDF files", "*.pdf"), ("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
            )
            if file_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{onoma.get()}_{timestamp}_{os.path.basename(file_path)}"
                shutil.copy2(file_path, os.path.join(DOCUMENTS_DIR, filename))
                docs_listbox.insert(tk.END, filename)
                messagebox.showinfo("Επιτυχία", f"Το έγγραφο {os.path.basename(file_path)} προστέθηκε επιτυχώς!")

        def remove_document():
            selection = docs_listbox.curselection()
            if not selection:
                messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε ένα έγγραφο για αφαίρεση")
                return
        
            doc_name = docs_listbox.get(selection[0])
            if messagebox.askyesno("Επιβεβαίωση", f"Είστε σίγουροι ότι θέλετε να αφαιρέσετε το έγγραφο {doc_name}?"):
                try:
                    doc_path = os.path.join(DOCUMENTS_DIR, doc_name)
                    if os.path.exists(doc_path):
                        os.remove(doc_path)
                        docs_listbox.delete(selection[0])
                        messagebox.showinfo("Επιτυχία", "Το έγγραφο αφαιρέθηκε επιτυχώς!")
                    else:
                        messagebox.showerror("Σφάλμα", "Το αρχείο δεν βρέθηκε!")
                except Exception as e:
                    messagebox.showerror("Σφάλμα", f"Δεν ήταν δυνατή η αφαίρεση του εγγράφου: {str(e)}")

        docs_buttons_frame = tk.Frame(docs_frame)
        docs_buttons_frame.pack(pady=5)
        
        tk.Button(docs_buttons_frame, text="Προσθήκη Εγγράφου", command=add_document).pack(side=tk.LEFT, padx=5)
        tk.Button(docs_buttons_frame, text="Αφαίρεση Εγγράφου", command=remove_document).pack(side=tk.LEFT, padx=5)

        def save():
            if not onoma.get() or not tilefono.get():
                messagebox.showerror("Σφάλμα", "Το όνομα και το τηλέφωνο είναι υποχρεωτικά!")
                return

            if not validate_phone(tilefono.get()):
                messagebox.showerror("Σφάλμα", "Το τηλέφωνο πρέπει να έχει 10 ψηφία και να ξεκινάει με 2 ή 6!")
                return

            if email.get() and not validate_email(email.get()):
                messagebox.showerror("Σφάλμα", "Το email δεν είναι έγκυρο!")
                return

            customer_docs = list(docs_listbox.get(0, tk.END))

            rows = []
            with open(FILE_NAME, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                try:
                    header = next(reader)
                    for row in reader:
                        if row[0] != values[0] or row[1] != values[1]:
                            rows.append(row)
                        else:
                            rows.append([
                                onoma.get(),
                                eponimo.get(),
                                tilefono.get(),
                                email.get(),
                                dieuthinsi.get(),
                                ", ".join(customer_docs) if customer_docs else ""
                            ])
                except StopIteration:
                    messagebox.showerror("Σφάλμα", "Το αρχείο πελατών είναι κενό!")
                    return

            with open(FILE_NAME, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(header)
                writer.writerows(rows)

            messagebox.showinfo("Επιτυχία", "Οι αλλαγές αποθηκεύτηκαν επιτυχώς!")
            dialog.destroy()
            self.fortose_kai_emfanise()

        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(pady=10, padx=10)

        tk.Button(buttons_frame, text="Αποθήκευση", command=save, bg='green', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Ακύρωση", command=dialog.destroy, bg='red', fg='white', width=15).pack(side=tk.LEFT, padx=5)

    def anazitisi_pelati(self):
        search_dialog = tk.Toplevel(self.root)
        search_dialog.title("Αναζήτηση Πελάτη")
        search_dialog.geometry("400x200")
        search_dialog.transient(self.root)
        search_dialog.grab_set()
        center_window(search_dialog)

        tk.Label(search_dialog, text="Αναζήτηση με:", font=("Arial", 10, "bold")).pack(pady=5)
        
        search_frame = tk.Frame(search_dialog)
        search_frame.pack(pady=5)
        
        search_type = tk.StringVar(value="name")
        tk.Radiobutton(search_frame, text="Όνομα/Επώνυμο", variable=search_type, value="name").pack(side=tk.LEFT)
        tk.Radiobutton(search_frame, text="Τηλέφωνο", variable=search_type, value="phone").pack(side=tk.LEFT)
        tk.Radiobutton(search_frame, text="Email", variable=search_type, value="email").pack(side=tk.LEFT)
        tk.Radiobutton(search_frame, text="Διεύθυνση", variable=search_type, value="address").pack(side=tk.LEFT)

        tk.Label(search_dialog, text="Κείμενο αναζήτησης:").pack(pady=5)
        search_entry = tk.Entry(search_dialog, width=40)
        search_entry.pack()

        def do_search():
            search_text = search_entry.get().strip().lower()
            if not search_text:
                messagebox.showwarning("Προειδοποίηση", "Παρακαλώ εισάγετε κείμενο για αναζήτηση")
                return

            for item in self.tree_pelates.get_children():
                self.tree_pelates.delete(item)
            
            column_map = {
                "name": [0, 1],
                "phone": [2],
                "email": [3],
                "address": [4]
            }
            
            search_columns = column_map[search_type.get()]
            found = False
            
            with open(FILE_NAME, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    for col in search_columns:
                        if search_text in row[col].lower():
                            self.tree_pelates.insert('', 'end', values=row)
                            found = True
                            break
            
            if not found:
                messagebox.showinfo("Πληροφορία", "Δεν βρέθηκαν αποτελέσματα")
            search_dialog.destroy()

        button_frame = tk.Frame(search_dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Αναζήτηση", command=do_search, bg='green', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Ακύρωση", command=search_dialog.destroy, bg='red', fg='white', width=15).pack(side=tk.LEFT, padx=5)

    def prosthiki_proiontos(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Καταχώρηση Νέου Προϊόντος")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.focus_set()
        center_window(dialog)

        input_frame = tk.Frame(dialog)
        input_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(input_frame, text="Όνομα Προϊόντος:").pack(pady=5)
        onoma = tk.Entry(input_frame, width=40)
        onoma.pack()

        tk.Label(input_frame, text="Κατηγορία:").pack(pady=5)
        katigoria = tk.Entry(input_frame, width=40)
        katigoria.pack()

        tk.Label(input_frame, text="Ποσότητα:").pack(pady=5)
        posotita = tk.Entry(input_frame, width=40)
        posotita.pack()

        tk.Label(input_frame, text="Τιμή:").pack(pady=5)
        timi = tk.Entry(input_frame, width=40)
        timi.pack()

        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(pady=10, padx=10)

        def check_product():
            product_name = onoma.get().strip()
            if not product_name:
                messagebox.showerror("Σφάλμα", "Παρακαλώ εισάγετε όνομα προϊόντος!")
                return

            with open(INVENTORY_FILE, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if row[0].lower() == product_name.lower():
                        messagebox.showinfo("Πληροφορίες", 
                            f"Το προϊόν '{row[0]}' υπάρχει ήδη στην αποθήκη.\n"
                            f"Διαθέσιμη ποσότητα: {row[2]}\n"
                            f"Τιμή: {row[3]}€")
                        return True
            return False

        def save():
            try:
                if not onoma.get() or not katigoria.get() or not posotita.get() or not timi.get():
                    messagebox.showerror("Σφάλμα", "Όλα τα πεδία είναι υποχρεωτικά!")
                    return

                if check_product():
                    messagebox.showwarning("Προειδοποίηση", 
                        "Το προϊόν υπάρχει ήδη στην αποθήκη.\n"
                        "Χρησιμοποιήστε το κουμπί 'Παραγγελία' για να προσθέσετε ποσότητα.")
                    return

                posotita_val = int(posotita.get())
                timi_val = float(timi.get())

                with open(INVENTORY_FILE, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        onoma.get(),
                        katigoria.get(),
                        posotita_val,
                        timi_val
                    ])
                
                messagebox.showinfo("Επιτυχία", "Το προϊόν καταχωρήθηκε επιτυχώς!")
                dialog.destroy()
                self.fortose_apothiki()
            except ValueError:
                messagebox.showerror("Σφάλμα", "Η ποσότητα πρέπει να είναι ακέραιος αριθμός και η τιμή δεκαδικός!")

        def order_product():
            product_name = onoma.get().strip()
            if not product_name:
                messagebox.showerror("Σφάλμα", "Παρακαλώ εισάγετε όνομα προϊόντος!")
                return

            existing_product = None
            with open(INVENTORY_FILE, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if row[0].lower() == product_name.lower():
                        existing_product = row
                        break

            if not existing_product:
                messagebox.showerror("Σφάλμα", "Το προϊόν δεν υπάρχει στην αποθήκη!")
                return

            order_dialog = tk.Toplevel(dialog)
            order_dialog.title("Παραγγελία Προϊόντος")
            order_dialog.geometry("300x200")
            order_dialog.transient(dialog)

            order_dialog.update_idletasks()
            width = order_dialog.winfo_width()
            height = order_dialog.winfo_height()
            x = (order_dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (order_dialog.winfo_screenheight() // 2) - (height // 2)
            order_dialog.geometry(f'{width}x{height}+{x}+{y}')

            tk.Label(order_dialog, text=f"Παραγγελία: {existing_product[0]}", font=("Arial", 10, "bold")).pack(pady=5)
            tk.Label(order_dialog, text=f"Τρέχουσα ποσότητα: {existing_product[2]}").pack(pady=5)
            
            tk.Label(order_dialog, text="Ποσότητα παραγγελίας:").pack(pady=5)
            order_quantity = tk.Entry(order_dialog, width=20)
            order_quantity.pack()

            def save_order():
                try:
                    quantity = int(order_quantity.get())
                    if quantity <= 0:
                        messagebox.showerror("Σφάλμα", "Η ποσότητα πρέπει να είναι θετικός αριθμός!")
                        return

                    rows = []
                    with open(INVENTORY_FILE, mode='r', newline='', encoding='utf-8') as file:
                        reader = csv.reader(file)
                        header = next(reader)
                        for row in reader:
                            if row[0].lower() == product_name.lower():
                                row[2] = str(int(row[2]) + quantity)
                            rows.append(row)

                    with open(INVENTORY_FILE, mode='w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(header)
                        writer.writerows(rows)

                    messagebox.showinfo("Επιτυχία", f"Προστέθηκαν {quantity} τεμάχια στο προϊόν {existing_product[0]}")
                    order_dialog.destroy()
                    dialog.destroy()
                    self.fortose_apothiki()
                except ValueError:
                    messagebox.showerror("Σφάλμα", "Παρακαλώ εισάγετε έγκυρη ποσότητα!")

            tk.Button(order_dialog, text="Αποθήκευση", command=save_order, bg='green', fg='white', width=15).pack(pady=10)
            tk.Button(order_dialog, text="Ακύρωση", command=order_dialog.destroy, bg='red', fg='white', width=15).pack(pady=5)

        tk.Button(buttons_frame, text="Αποθήκευση", command=save, bg='green', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Παραγγελία", command=order_product, bg='blue', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Ακύρωση", command=dialog.destroy, bg='red', fg='white', width=15).pack(side=tk.LEFT, padx=5)

    def pwlisi_proiontos(self):
        try:
            selected = self.tree_apothiki.selection()
            if not selected:
                logging.warning("Προσπάθεια πώλησης χωρίς επιλεγμένο προϊόν")
                messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε ένα προϊόν για πώληση")
                return

            item = self.tree_apothiki.item(selected[0])
            values = item['values']

            try:
                price = float(values[3])
                if price <= 0:
                    logging.warning(f"Προσπάθεια πώλησης προϊόντος με μη έγκυρη τιμή: {price}")
                    messagebox.showerror("Σφάλμα", "Η τιμή του προϊόντος πρέπει να είναι θετική!")
                    return
            except ValueError:
                logging.warning(f"Προσπάθεια πώλησης προϊόντος με μη έγκυρη τιμή: {values[3]}")
                messagebox.showerror("Σφάλμα", "Η τιμή του προϊόντος δεν είναι έγκυρη!")
                return

            try:
                quantity = int(values[2])
                if quantity <= 0:
                    logging.warning(f"Προσπάθεια πώλησης προϊόντος με μη έγκυρη ποσότητα: {quantity}")
                    messagebox.showerror("Σφάλμα", "Η ποσότητα του προϊόντος πρέπει να είναι θετική!")
                    return
            except ValueError:
                logging.warning(f"Προσπάθεια πώλησης προϊόντος με μη έγκυρη ποσότητα: {values[2]}")
                messagebox.showerror("Σφάλμα", "Η ποσότητα του προϊόντος δεν είναι έγκυρη!")
                return

            dialog = tk.Toplevel(self.root)
            dialog.title("Πώληση Προϊόντος")
            dialog.geometry("400x300")
            dialog.transient(self.root)
            dialog.grab_set()
            dialog.focus_set()

            dialog.update_idletasks()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (dialog.winfo_screenheight() // 2) - (height // 2)
            dialog.geometry(f'{width}x{height}+{x}+{y}')

            input_frame = tk.Frame(dialog)
            input_frame.pack(pady=10, padx=10, fill='x')

            tk.Label(input_frame, text=f"Πώληση: {values[0]}", font=("Arial", 12, "bold")).pack(pady=5)
            tk.Label(input_frame, text=f"Διαθέσιμη ποσότητα: {values[2]}", font=("Arial", 10)).pack(pady=5)
            tk.Label(input_frame, text=f"Τιμή μονάδας: {values[3]}€", font=("Arial", 10)).pack(pady=5)

            tk.Label(input_frame, text="Ποσότητα πώλησης:").pack(pady=5)
            posotita = tk.Entry(input_frame, width=40)
            posotita.pack()

            buttons_frame = tk.Frame(dialog)
            buttons_frame.pack(pady=10, padx=10)

            def save():
                try:
                    posotita_val = int(posotita.get())
                    if posotita_val <= 0:
                        messagebox.showerror("Σφάλμα", "Η ποσότητα πρέπει να είναι θετικός αριθμός!")
                        return
                    if posotita_val > quantity:
                        messagebox.showerror("Σφάλμα", "Δεν υπάρχει αρκετή ποσότητα στην αποθήκη!")
                        return

                    rows = []
                    try:
                        with open(INVENTORY_FILE, mode='r', newline='', encoding='utf-8') as file:
                            reader = csv.reader(file)
                            header = next(reader)
                            for row in reader:
                                if row[0] == values[0]:
                                    new_quantity = int(row[2]) - posotita_val
                                    if new_quantity < 0:
                                        messagebox.showerror("Σφάλμα", "Η ποσότητα δεν μπορεί να γίνει αρνητική!")
                                        return
                                    row[2] = str(new_quantity)
                                    if new_quantity == 0:
                                        messagebox.showwarning("Προειδοποίηση", 
                                            f"Το προϊόν '{values[0]}' έχει τελειώσει!\nΠαρακαλώ κάντε παραγγελία.")
                                rows.append(row)

                        with open(INVENTORY_FILE, mode='w', newline='', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            writer.writerow(header)
                            writer.writerows(rows)

                        total = posotita_val * price
                        logging.info(f"Πώληση προϊόντος: {values[0]}, ποσότητα: {posotita_val}, συνολικό ποσό: {total:.2f}€")
                        messagebox.showinfo("Επιτυχία", 
                            f"Η πώληση ολοκληρώθηκε επιτυχώς!\nΣυνολικό ποσό: {total:.2f}€")
                        dialog.destroy()
                        self.fortose_apothiki()
                    except Exception as e:
                        logging.error(f"Σφάλμα κατά την ενημέρωση της αποθήκης: {str(e)}")
                        messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την ενημέρωση της αποθήκης: {str(e)}")
                except ValueError:
                    messagebox.showerror("Σφάλμα", "Παρακαλώ εισάγετε έγκυρη ποσότητα!")

            tk.Button(buttons_frame, text="Ολοκλήρωση Πώλησης", command=save, bg='green', fg='white', width=20).pack(side=tk.LEFT, padx=5)
            tk.Button(buttons_frame, text="Ακύρωση", command=dialog.destroy, bg='red', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        except Exception as e:
            logging.error(f"Σφάλμα κατά την πώληση προϊόντος: {str(e)}")
            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την πώληση: {str(e)}")

    def fortose_kai_emfanise(self):
        for item in self.tree_pelates.get_children():
            self.tree_pelates.delete(item)
        
        try:
            if not os.path.exists(FILE_NAME):
                with open(FILE_NAME, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(CUSTOMER_HEADERS)
                logging.info(f"Δημιουργήθηκε νέο αρχείο {FILE_NAME}")
                return
            
            with open(FILE_NAME, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    self.tree_pelates.insert('', 'end', values=row)
                
        except Exception as e:
            logging.error(f"Σφάλμα κατά τη φόρτωση των πελατών: {str(e)}")
            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά τη φόρτωση των πελατών: {str(e)}")

    def fortose_apothiki(self):
        for item in self.tree_apothiki.get_children():
            self.tree_apothiki.delete(item)
        
        try:
            if not os.path.exists(INVENTORY_FILE):
                with open(INVENTORY_FILE, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(INVENTORY_HEADERS)
                logging.info(f"Δημιουργήθηκε νέο αρχείο {INVENTORY_FILE}")
                return
            
            with open(INVENTORY_FILE, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    self.tree_apothiki.insert('', 'end', values=row)
                
        except Exception as e:
            logging.error(f"Σφάλμα κατά τη φόρτωση της αποθήκης: {str(e)}")
            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά τη φόρτωση της αποθήκης: {str(e)}")

    def on_select_customer(self, event):
        selected = self.tree_pelates.selection()
        if selected:
            item = self.tree_pelates.item(selected[0])
            values = item['values']
            if len(values) > 5 and values[5]:
                self.btn_open_doc.config(state='normal')
            else:
                self.btn_open_doc.config(state='disabled')
        else:
            self.btn_open_doc.config(state='disabled')

    def anigma_egrafou(self):
        selected = self.tree_pelates.selection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε έναν πελάτη")
            return

        item = self.tree_pelates.item(selected[0])
        values = item['values']
        
        if len(values) > 5 and values[5]:
            docs = values[5].split(", ")
            if len(docs) == 1:
                try:
                    doc_path = os.path.join(DOCUMENTS_DIR, docs[0])
                    if not os.path.exists(doc_path):
                        messagebox.showerror("Σφάλμα", "Το αρχείο δεν βρέθηκε!")
                        return
                    os.startfile(doc_path)
                except Exception as e:
                    messagebox.showerror("Σφάλμα", f"Δεν ήταν δυνατό το άνοιγμα του εγγράφου: {str(e)}")
            else:
                dialog = tk.Toplevel(self.root)
                dialog.title("Επιλογή Εγγράφου")
                dialog.geometry("400x300")
                dialog.transient(self.root)
                dialog.grab_set()
                dialog.focus_set()
                center_window(dialog)

                tk.Label(dialog, text="Επιλέξτε έγγραφο για προβολή:", font=("Arial", 10, "bold")).pack(pady=10)

                docs_listbox = tk.Listbox(dialog, height=10, width=50)
                docs_listbox.pack(padx=10, pady=5)
                
                existing_docs = []
                for doc in docs:
                    doc_path = os.path.join(DOCUMENTS_DIR, doc)
                    if os.path.exists(doc_path):
                        docs_listbox.insert(tk.END, doc)
                        existing_docs.append(doc)
                    else:
                        logging.warning(f"Το έγγραφο {doc} δεν βρέθηκε για τον πελάτη {values[0]} {values[1]}")
                        messagebox.showwarning("Προειδοποίηση", f"Το έγγραφο {doc} δεν βρέθηκε!")

                if not existing_docs:
                    messagebox.showerror("Σφάλμα", "Δεν βρέθηκαν έγκυρα έγγραφα!")
                    dialog.destroy()
                    return

                def open_selected():
                    selection = docs_listbox.curselection()
                    if selection:
                        doc_name = docs_listbox.get(selection[0])
                        try:
                            doc_path = os.path.join(DOCUMENTS_DIR, doc_name)
                            if not os.path.exists(doc_path):
                                messagebox.showerror("Σφάλμα", "Το αρχείο δεν βρέθηκε!")
                                return
                            os.startfile(doc_path)
                            dialog.destroy()
                        except Exception as e:
                            messagebox.showerror("Σφάλμα", f"Δεν ήταν δυνατό το άνοιγμα του εγγράφου: {str(e)}")

                tk.Button(dialog, text="Άνοιγμα", command=open_selected, bg='green', fg='white', width=15).pack(pady=10)
        else:
            messagebox.showinfo("Πληροφορίες", "Ο πελάτης δεν έχει έγγραφα.")

    def diagrafi_proiontos(self):
        try:
            selected = self.tree_apothiki.selection()
            if not selected:
                logging.warning("Προσπάθεια διαγραφής χωρίς επιλεγμένο προϊόν")
                messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε ένα προϊόν για διαγραφή")
                return

            item = self.tree_apothiki.item(selected[0])
            values = item['values']
            
            if messagebox.askyesno("Επιβεβαίωση", f"Είστε σίγουροι ότι θέλετε να διαγράψετε το προϊόν {values[0]}?"):
                rows = []
                with open(INVENTORY_FILE, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    header = next(reader)
                    for row in reader:
                        if row[0] != values[0]:
                            rows.append(row)

                with open(INVENTORY_FILE, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(header)
                    writer.writerows(rows)

                logging.info(f"Διαγράφηκε το προϊόν: {values[0]}")
                messagebox.showinfo("Επιτυχία", "Το προϊόν διαγράφηκε επιτυχώς!")
                self.fortose_apothiki()
        except Exception as e:
            logging.error(f"Σφάλμα κατά τη διαγραφή προϊόντος: {str(e)}")
            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά τη διαγραφή: {str(e)}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = OpticalSystem()
    app.run()
