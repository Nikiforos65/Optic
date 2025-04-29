import csv
import os
import tkinter as tk
from tkinter import messagebox, ttk, filedialog, scrolledtext
from datetime import datetime
import shutil
import logging
import re
import math
import zipfile
import sys
import subprocess

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
NOTES_CSV = "σημειώσεις.csv"

CUSTOMER_HEADERS = ["Όνομα", "Επώνυμο", "Τηλέφωνο", "Email", "Διεύθυνση", "Έγγραφα"]
INVENTORY_HEADERS = ["Όνομα Προϊόντος", "Κατηγορία", "Ποσότητα", "Τιμή"]
NOTES_HEADERS = ["Ημερομηνία", "Ονοματεπώνυμο", "Σημειώσεις"]

for file_name, headers in [(FILE_NAME, CUSTOMER_HEADERS),
                         (INVENTORY_FILE, INVENTORY_HEADERS),
                         (NOTES_CSV, NOTES_HEADERS)]:
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
        try:
            self.root.iconbitmap("optic_logo_white_bg.ico")
        except Exception:
            pass  # fallback αν δεν βρεθεί το ico
        self.root.state('zoomed')
        self.root.configure(bg='#f0f0f0')
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 11), padding=6, background='#ff9800', foreground='black')
        style.configure('TLabel', font=('Segoe UI', 11), background='#f0f0f0', foreground='#ff9800')
        style.configure('Treeview.Heading', font=('Segoe UI', 11, 'bold'), background='#ff9800', foreground='black')
        style.configure('Treeview', background='#f0f0f0', fieldbackground='#f0f0f0', foreground='black')
        # Header με λογότυπο και gradient
        header_height = 70
        header_frame = tk.Frame(self.root, height=header_height)
        header_frame.pack(fill='x')
        header_canvas = tk.Canvas(header_frame, height=header_height, width=self.root.winfo_screenwidth(), highlightthickness=0, bd=0)
        header_canvas.pack(fill='both', expand=True)
        # Gradient από γκρι σε πορτοκαλί
        def draw_gradient(canvas, width, height, color1, color2):
            r1, g1, b1 = self.root.winfo_rgb(color1)
            r2, g2, b2 = self.root.winfo_rgb(color2)
            r_ratio = (r2 - r1) / width
            g_ratio = (g2 - g1) / width
            b_ratio = (b2 - b1) / width
            for i in range(width):
                nr = int(r1 + (r_ratio * i)) // 256
                ng = int(g1 + (g_ratio * i)) // 256
                nb = int(b1 + (b_ratio * i)) // 256
                color = f'#{nr:02x}{ng:02x}{nb:02x}'
                canvas.create_line(i, 0, i, height, fill=color)
        self.root.update_idletasks()
        width = self.root.winfo_width() or 1200
        draw_gradient(header_canvas, width, header_height, '#f0f0f0', '#ff9800')
        # Τοποθέτηση λογότυπου και τίτλου πάνω από το gradient
        try:
            from PIL import Image, ImageTk
            logo_img = Image.open('optic_logo_white_bg_128x128.png')
            logo_img = logo_img.resize((48, 48), Image.LANCZOS)
            logo = ImageTk.PhotoImage(logo_img)
            header_canvas.create_image(30, header_height//2, image=logo, anchor='w')
            self.header_logo = logo  # κρατάμε reference
        except Exception:
            header_canvas.create_text(50, header_height//2, text='👓', font=('Segoe UI', 32), anchor='w')
        header_canvas.create_text(100, header_height//2, text="Σύστημα Διαχείρισης Οπτικών", font=("Segoe UI", 20, "bold"), anchor='w', fill='#333333')
        # Κουμπί Βοήθειας (πορτοκαλί)
        help_btn = tk.Button(header_frame, text='Βοήθεια', command=self.toggle_help_drawer, bg='#ff9800', fg='black', font=('Segoe UI', 11, 'bold'))
        help_btn.place(x=width-120, y=header_height//2-18, width=100, height=36)
        
        self.create_customer_section()
        self.create_inventory_section()
        
        self.fortose_kai_emfanise()
        self.fortose_apothiki()

        # Φόρτωση του λογότυπου για χρήση στο συνταγολόγιο
        try:
            from PIL import Image, ImageTk
            self.prescription_logo = Image.open('optic_logo_white_bg.png')
            self.prescription_logo = self.prescription_logo.resize((100, 100), Image.LANCZOS)
            self.prescription_logo = ImageTk.PhotoImage(self.prescription_logo)
        except Exception as e:
            logging.error(f"Σφάλμα κατά τη φόρτωση του λογότυπου: {str(e)}")
            self.prescription_logo = None

        # Επαναφορά help drawer στο κάτω μέρος
        self.help_drawer = tk.Frame(self.root, bg='#e8eaf6', height=0)
        self.help_drawer.pack(fill='x', side='bottom', anchor='s')
        self.help_drawer_visible = False

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

        self.btn_open_doc = tk.Button(frame_pelates, text="Προβολή Εγγράφου", command=self.anigma_egrafou, state='disabled')
        self.btn_open_doc.grid(row=0, column=5, padx=5)

        self.btn_view_prescriptions = tk.Button(frame_pelates, text="Προβολή Συνταγών", command=self.provoli_syntagon, state='disabled')
        self.btn_view_prescriptions.grid(row=0, column=6, padx=5)

        self.btn_view_notes = tk.Button(frame_pelates, text="Προβολή Σημειώσεων", command=self.provoli_seimeioseon, state='disabled')
        self.btn_view_notes.grid(row=0, column=7, padx=5)

        cols = ("Όνομα", "Επώνυμο", "Τηλέφωνο", "Email", "Διεύθυνση", "Διαθέσιμα")
        self.tree_pelates = ttk.Treeview(self.root, columns=cols, show='headings')
        
        col_widths = {
            "Όνομα": 120,
            "Επώνυμο": 120,
            "Τηλέφωνο": 100,
            "Email": 180,
            "Διεύθυνση": 200,
            "Διαθέσιμα": 200
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
        dialog.geometry("600x500")  # Wider and shorter window
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.focus_set()
        dialog.configure(bg='#f0f0f0')
        center_window(dialog)

        input_frame = tk.Frame(dialog, bg='#f0f0f0')
        input_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(input_frame, text="Όνομα:", bg='#f0f0f0', fg='#ff9800').pack(pady=5)
        onoma = tk.Entry(input_frame, width=60)  # Wider entry fields
        onoma.pack()

        tk.Label(input_frame, text="Επώνυμο:", bg='#f0f0f0', fg='#ff9800').pack(pady=5)
        eponimo = tk.Entry(input_frame, width=60)
        eponimo.pack()

        tk.Label(input_frame, text="Τηλέφωνο:", bg='#f0f0f0', fg='#ff9800').pack(pady=5)
        tilefono = tk.Entry(input_frame, width=60)
        tilefono.pack()

        tk.Label(input_frame, text="Email:", bg='#f0f0f0', fg='#ff9800').pack(pady=5)
        email = tk.Entry(input_frame, width=60)
        email.pack()

        tk.Label(input_frame, text="Διεύθυνση:", bg='#f0f0f0', fg='#ff9800').pack(pady=5)
        dieuthinsi = tk.Entry(input_frame, width=60)
        dieuthinsi.pack()

        docs_frame = tk.Frame(dialog, bg='#f0f0f0')
        docs_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(docs_frame, text="Έγγραφα:", bg='#f0f0f0', fg='#ff9800').pack(pady=5)
        docs_listbox = tk.Listbox(docs_frame, height=5, width=70)  # Wider listbox
        docs_listbox.pack()

        action_buttons_frame = tk.Frame(dialog, bg='#f0f0f0')
        action_buttons_frame.pack(pady=5)

        def add_document():
            file_path = filedialog.askopenfilename(
                title="Επιλέξτε έγγραφο",
                filetypes=[("PDF files", "*.pdf"), ("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    # Create documents directory if it doesn't exist
                    if not os.path.exists(DOCUMENTS_DIR):
                        os.makedirs(DOCUMENTS_DIR)

                    # Generate unique filename with customer name and timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = os.path.basename(file_path)
                    customer_name = f"{onoma.get()}_{eponimo.get()}".strip().replace(" ", "_")
                    if not customer_name:
                        customer_name = "unnamed"
                    filename = f"{customer_name}_{timestamp}_{base_name}"
                    target_path = os.path.join(DOCUMENTS_DIR, filename)
                    
                    # Copy the file
                    shutil.copy2(file_path, target_path)
                    
                    # Verify the file was copied successfully
                    if os.path.exists(target_path):
                        docs_listbox.insert(tk.END, filename)
                        messagebox.showinfo("Επιτυχία", f"Το έγγραφο {os.path.basename(file_path)} προστέθηκε επιτυχώς!")
                    else:
                        messagebox.showerror("Σφάλμα", "Δεν ήταν δυνατή η αντιγραφή του εγγράφου!")
                except Exception as e:
                    messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την προσθήκη του εγγράφου: {str(e)}")

        def open_prescription():
            customer_name = f"{onoma.get()} {eponimo.get()}".strip()
            if not customer_name:
                messagebox.showwarning("Προειδοποίηση", "Παρακαλώ συμπληρώστε το όνομα και το επώνυμο πρώτα!")
                return
            self.create_prescription_form(dialog, customer_name)

        def open_notes():
            customer_name = f"{onoma.get()} {eponimo.get()}".strip()
            if not customer_name:
                messagebox.showwarning("Προειδοποίηση", "Παρακαλώ συμπληρώστε το όνομα και το επώνυμο πρώτα!")
                return
            self.create_notes_form(dialog, customer_name)

        tk.Button(action_buttons_frame, text="Προσθήκη Εγγράφου", command=add_document, 
                 bg='#ff9800', fg='black', width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(action_buttons_frame, text="Προσθήκη Συνταγών", command=open_prescription,
                 bg='#ff9800', fg='black', width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(action_buttons_frame, text="Προσθήκη Σημειώσεων", command=open_notes,
                 bg='#ff9800', fg='black', width=20).pack(side=tk.LEFT, padx=5)

        def save():
            try:
                name = onoma.get().strip()
                surname = eponimo.get().strip()
                phone = tilefono.get().strip()
                email_val = email.get().strip()
                address = dieuthinsi.get().strip()

                if not name:
                    logging.warning("Προσπάθεια αποθήκευσης πελάτη χωρίς όνομα")
                    messagebox.showerror("Σφάλμα", "Το όνομα είναι υποχρεωτικό!")
                    return

                if phone and not validate_phone(phone):
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
                    logging.warning(f"Προσπάθεια διπλής καταχώρισης πελάτη: {name} {surname}")
                    messagebox.showerror("Σφάλμα", 
                        "Υπάρχει ήδη πελάτης με τα ίδια στοιχεία!\n" +
                        "(έλεγχος για ίδιο όνομα/επώνυμο, τηλέφωνο ή email)")
                    return

                # Get documents from listbox
                documents = []
                for i in range(docs_listbox.size()):
                    doc_name = docs_listbox.get(i)
                    doc_path = os.path.join(DOCUMENTS_DIR, doc_name)
                    if os.path.exists(doc_path):
                        documents.append(doc_name)
                    else:
                        logging.warning(f"Το έγγραφο {doc_name} δεν βρέθηκε κατά την αποθήκευση")
                documents_str = ", ".join(documents)

                # Add flags based on what was added
                flags = []
                if documents:  # Changed from documents_str to documents
                    flags.append("Έγγραφα")

                # Check for prescriptions
                customer_name = f"{name} {surname}".strip()
                if os.path.exists("συνταγολόγια.csv"):
                    with open("συνταγολόγια.csv", mode='r', newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        next(reader)
                        for row in reader:
                            if row[1].strip().lower() == customer_name.lower():
                                flags.append("Συνταγές")
                                break

                # Check for notes
                if os.path.exists(NOTES_CSV):
                    with open(NOTES_CSV, mode='r', newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        next(reader)
                        for row in reader:
                            if row[1].strip().lower() == customer_name.lower():
                                flags.append("Σημειώσεις")
                                break

                flags_str = ", ".join(flags)

                with open(FILE_NAME, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([name, surname, phone, email_val, address, documents_str, flags_str])

                logging.info(f"Προστέθηκε νέος πελάτης: {name} {surname}")
                messagebox.showinfo("Επιτυχία", "Ο πελάτης καταχωρήθηκε επιτυχώς!")
                dialog.destroy()
                self.fortose_kai_emfanise()
            except Exception as e:
                logging.error(f"Σφάλμα κατά την αποθήκευση πελάτη: {str(e)}")
                messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την αποθήκευση: {str(e)}")

        save_cancel_frame = tk.Frame(dialog)
        save_cancel_frame.pack(pady=10, padx=10)
        tk.Button(save_cancel_frame, text="Αποθήκευση", command=save, bg='green', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(save_cancel_frame, text="Ακύρωση", command=dialog.destroy, bg='red', fg='white', width=15).pack(side=tk.LEFT, padx=5)

    def diagrafi_pelati(self):
        selected = self.tree_pelates.selection()
        if not selected:
            logging.warning("Προσπάθεια διαγραφής χωρίς επιλεγμένο πελάτη")
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε έναν πελάτη για διαγραφή")
            return

        item = self.tree_pelates.item(selected[0])
        values = item['values']

        if messagebox.askyesno("Επιβεβαίωση", f"Είστε σίγουροι ότι θέλετε να διαγράψετε τον πελάτη {values[0]} {values[1]}?"):
            try:
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
                # Διαγραφή πελάτη από το πελάτες.csv
                rows = []
                with open(FILE_NAME, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    header = next(reader)
                    for row in reader:
                        # Σύγκριση με strip και lower για σωστή διαγραφή
                        if str(row[0]).strip().lower() != str(values[0]).strip().lower() or str(row[1]).strip().lower() != str(values[1]).strip().lower():
                            rows.append(row)
                with open(FILE_NAME, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(header)
                    writer.writerows(rows)
                # Διαγραφή συνταγών από το συνταγολόγια.csv
                PRESCRIPTION_CSV = "συνταγολόγια.csv"
                if os.path.exists(PRESCRIPTION_CSV):
                    try:
                        rows = []
                        with open(PRESCRIPTION_CSV, mode='r', newline='', encoding='utf-8') as f:
                            reader = csv.reader(f)
                            header = next(reader)
                            for row in reader:
                                # row[1] = Ονοματεπώνυμο
                                if len(row) > 1 and row[1].strip().replace(' ', '').lower() != f"{values[0]}{values[1]}".strip().replace(' ', '').lower():
                                    rows.append(row)
                        with open(PRESCRIPTION_CSV, mode='w', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow(header)
                            writer.writerows(rows)
                        logging.info(f"Διαγράφηκαν οι συνταγές του πελάτη {values[0]} {values[1]} από το συνταγολόγια.csv")
                    except Exception as e:
                        logging.error(f"Σφάλμα κατά τη διαγραφή συνταγών πελάτη: {str(e)}")
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
        
        # Convert all values to strings and handle None values
        values = [str(val) if val is not None else "" for val in values]
        
        # Now we can safely use string operations since all values are strings
        old_name = values[0].strip()
        old_surname = values[1].strip()
        old_phone = values[2].strip()
        old_email = values[3].strip()
        old_address = values[4].strip()
        old_customer_name = f"{old_name} {old_surname}".strip().lower()

        # Get the original documents from the CSV file
        original_documents = []
        try:
            with open(FILE_NAME, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if row[0].strip().lower() == old_name.lower() and row[1].strip().lower() == old_surname.lower():
                        if len(row) > 5 and row[5]:
                            original_documents = [doc.strip() for doc in row[5].split(",") if doc.strip()]
                        break
        except Exception as e:
            logging.error(f"Σφάλμα κατά την ανάγνωση εγγράφων: {str(e)}")

        dialog = tk.Toplevel(self.root)
        dialog.title("Διόρθωση Πελάτη")
        dialog.geometry("600x500")  # Same size as kataxwrisi_pelati
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.focus_set()
        dialog.configure(bg='#f0f0f0')
        center_window(dialog)

        input_frame = tk.Frame(dialog, bg='#f0f0f0')
        input_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(input_frame, text="Όνομα:", bg='#f0f0f0', fg='#ff9800').pack(pady=5)
        onoma = tk.Entry(input_frame, width=60)
        onoma.insert(0, values[0])
        onoma.pack()

        tk.Label(input_frame, text="Επώνυμο:", bg='#f0f0f0', fg='#ff9800').pack(pady=5)
        eponimo = tk.Entry(input_frame, width=60)
        eponimo.insert(0, values[1])
        eponimo.pack()

        tk.Label(input_frame, text="Τηλέφωνο:", bg='#f0f0f0', fg='#ff9800').pack(pady=5)
        tilefono = tk.Entry(input_frame, width=60)
        tilefono.insert(0, values[2])
        tilefono.pack()

        tk.Label(input_frame, text="Email:", bg='#f0f0f0', fg='#ff9800').pack(pady=5)
        email = tk.Entry(input_frame, width=60)
        email.insert(0, values[3] if len(values) > 3 else "")
        email.pack()

        tk.Label(input_frame, text="Διεύθυνση:", bg='#f0f0f0', fg='#ff9800').pack(pady=5)
        dieuthinsi = tk.Entry(input_frame, width=60)
        dieuthinsi.insert(0, values[4] if len(values) > 4 else "")
        dieuthinsi.pack()

        docs_frame = tk.Frame(dialog, bg='#f0f0f0')
        docs_frame.pack(pady=10, fill='x')

        tk.Label(docs_frame, text="Έγγραφα Πελάτη:", font=("Arial", 10, "bold"), bg='#f0f0f0', fg='#ff9800').pack()
        docs_listbox = tk.Listbox(docs_frame, height=5, width=70)
        docs_listbox.pack(fill='x', padx=5)

        # Load existing documents
        for doc in original_documents:
            if os.path.exists(os.path.join(DOCUMENTS_DIR, doc)):
                docs_listbox.insert(tk.END, doc)

        def add_document():
            file_path = filedialog.askopenfilename(
                title="Επιλέξτε έγγραφο",
                filetypes=[("PDF files", "*.pdf"), ("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    # Create documents directory if it doesn't exist
                    if not os.path.exists(DOCUMENTS_DIR):
                        os.makedirs(DOCUMENTS_DIR)

                    # Generate unique filename with customer name and timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = os.path.basename(file_path)
                    customer_name = f"{onoma.get()}_{eponimo.get()}".strip().replace(" ", "_")
                    if not customer_name:
                        customer_name = "unnamed"
                    filename = f"{customer_name}_{timestamp}_{base_name}"
                    target_path = os.path.join(DOCUMENTS_DIR, filename)
                    
                    # Copy the file
                    shutil.copy2(file_path, target_path)
                    
                    # Verify the file was copied successfully
                    if os.path.exists(target_path):
                        docs_listbox.insert(tk.END, filename)
                        messagebox.showinfo("Επιτυχία", f"Το έγγραφο {os.path.basename(file_path)} προστέθηκε επιτυχώς!")
                    else:
                        messagebox.showerror("Σφάλμα", "Δεν ήταν δυνατή η αντιγραφή του εγγράφου!")
                except Exception as e:
                    messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την προσθήκη του εγγράφου: {str(e)}")

        def open_prescription():
            customer_name = f"{onoma.get()} {eponimo.get()}".strip()
            if not customer_name:
                messagebox.showwarning("Προειδοποίηση", "Παρακαλώ συμπληρώστε το όνομα και το επώνυμο πρώτα!")
                return
            self.create_prescription_form(dialog, customer_name)

        def open_notes():
            customer_name = f"{onoma.get()} {eponimo.get()}".strip()
            if not customer_name:
                messagebox.showwarning("Προειδοποίηση", "Παρακαλώ συμπληρώστε το όνομα και το επώνυμο πρώτα!")
                return
            self.create_notes_form(dialog, customer_name)

        action_buttons_frame = tk.Frame(dialog, bg='#f0f0f0')
        action_buttons_frame.pack(pady=5)

        tk.Button(action_buttons_frame, text="Προσθήκη Εγγράφου", command=add_document, 
                 bg='#ff9800', fg='black', width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(action_buttons_frame, text="Προσθήκη Συνταγών", command=open_prescription,
                 bg='#ff9800', fg='black', width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(action_buttons_frame, text="Προσθήκη Σημειώσεων", command=open_notes,
                 bg='#ff9800', fg='black', width=20).pack(side=tk.LEFT, padx=5)

        def save():
            try:
                name = onoma.get().strip()
                surname = eponimo.get().strip()
                phone = tilefono.get().strip()
                email_val = email.get().strip()
                address = dieuthinsi.get().strip()
                new_customer_name = f"{name} {surname}".strip().lower()

                if not name:
                    logging.warning("Προσπάθεια αποθήκευσης πελάτη χωρίς όνομα (διόρθωση)")
                    messagebox.showerror("Σφάλμα", "Το όνομα είναι υποχρεωτικό!")
                    return

                if phone and not validate_phone(phone):
                    logging.warning(f"Προσπάθεια αποθήκευσης πελάτη με μη έγκυρο τηλέφωνο (διόρθωση): {phone}")
                    messagebox.showerror("Σφάλμα",
                        "Το τηλέφωνο πρέπει να είναι 10 ψηφία και να ξεκινάει:\n" +
                        "- με 69 για κινητό\n" +
                        "- με 2 για σταθερό")
                    return

                if email_val and not validate_email(email_val):
                    logging.warning(f"Προσπάθεια αποθήκευσης πελάτη με μη έγκυρο email (διόρθωση): {email_val}")
                    messagebox.showerror("Σφάλμα", "Το email πρέπει να έχει τη μορφή: onoma@domain.com")
                    return

                # Get documents from listbox
                documents = []
                for i in range(docs_listbox.size()):
                    doc_name = docs_listbox.get(i)
                    doc_path = os.path.join(DOCUMENTS_DIR, doc_name)
                    if os.path.exists(doc_path):
                        documents.append(doc_name)
                    else:
                        logging.warning(f"Το έγγραφο {doc_name} δεν βρέθηκε κατά την αποθήκευση")
                documents_str = ", ".join(documents)

                # Add flags based on what was added
                flags = []
                if documents:
                    flags.append("Έγγραφα")

                # Update prescriptions if name changed
                if os.path.exists("συνταγολόγια.csv"):
                    prescriptions_updated = False
                    temp_rows = []
                    try:
                        with open("συνταγολόγια.csv", mode='r', newline='', encoding='utf-8') as f:
                            reader = csv.reader(f)
                            header = next(reader)
                            has_prescriptions = False
                            for row in reader:
                                if row[1].strip().lower() == old_customer_name:
                                    has_prescriptions = True
                                    if old_customer_name != new_customer_name:
                                        row[1] = f"{name} {surname}"
                                temp_rows.append(row)
                            if has_prescriptions:
                                flags.append("Συνταγές")
                                
                        if old_customer_name != new_customer_name and temp_rows:
                            with open("συνταγολόγια.csv", mode='w', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerow(header)
                                writer.writerows(temp_rows)
                                prescriptions_updated = True
                                logging.info(f"Ενημερώθηκαν οι συνταγές του πελάτη από {old_customer_name} σε {new_customer_name}")
                    except Exception as e:
                        logging.error(f"Σφάλμα κατά την ενημέρωση συνταγών: {str(e)}")

                # Update notes if name changed
                if os.path.exists(NOTES_CSV):
                    notes_updated = False
                    temp_rows = []
                    try:
                        with open(NOTES_CSV, mode='r', newline='', encoding='utf-8') as f:
                            reader = csv.reader(f)
                            header = next(reader)
                            has_notes = False
                            for row in reader:
                                if row[1].strip().lower() == old_customer_name:
                                    has_notes = True
                                    if old_customer_name != new_customer_name:
                                        row[1] = f"{name} {surname}"
                                temp_rows.append(row)
                            if has_notes:
                                flags.append("Σημειώσεις")

                        if old_customer_name != new_customer_name and temp_rows:
                            with open(NOTES_CSV, mode='w', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerow(header)
                                writer.writerows(temp_rows)
                                notes_updated = True
                                logging.info(f"Ενημερώθηκαν οι σημειώσεις του πελάτη από {old_customer_name} σε {new_customer_name}")
                    except Exception as e:
                        logging.error(f"Σφάλμα κατά την ενημέρωση σημειώσεων: {str(e)}")

                flags_str = ", ".join(flags)

                # Update the customer's record
                rows = []
                updated = False
                with open(FILE_NAME, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    header = next(reader)
                    for row in reader:
                        if row[0].strip().lower() == old_name.lower() and row[1].strip().lower() == old_surname.lower():
                            rows.append([name, surname, phone, email_val, address, documents_str, flags_str])
                            updated = True
                        else:
                            rows.append(row)

                if not updated:
                    rows.append([name, surname, phone, email_val, address, documents_str, flags_str])

                with open(FILE_NAME, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(header)
                    writer.writerows(rows)

                logging.info(f"Ενημερώθηκε ο πελάτης: {name} {surname}")
                messagebox.showinfo("Επιτυχία", "Τα στοιχεία του πελάτη ενημερώθηκαν επιτυχώς!")
                dialog.destroy()
                self.fortose_kai_emfanise()
            except Exception as e:
                logging.error(f"Σφάλμα κατά την αποθήκευση πελάτη (διόρθωση): {str(e)}")
                messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την αποθήκευση: {str(e)}")

        save_cancel_frame = tk.Frame(dialog)
        save_cancel_frame.pack(pady=10, padx=10)
        tk.Button(save_cancel_frame, text="Αποθήκευση", command=save, bg='green', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(save_cancel_frame, text="Ακύρωση", command=dialog.destroy, bg='red', fg='white', width=15).pack(side=tk.LEFT, padx=5)

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
                    # Get the documents from column 5 (index 5)
                    documents = row[5] if len(row) > 5 and row[5] else ""
                    
                    # Get or create flags from column 6 (index 6)
                    flags = []
                    if len(row) > 6 and row[6]:
                        flags = row[6].split(", ")
                    else:
                        # If no flags column, create flags based on available items
                        if documents:
                            flags.append("Έγγραφα")
                    
                    # Create display row
                    display_row = [row[0], row[1], row[2], row[3], row[4], ", ".join(flags)]
                    
                    # Insert into tree view
                    self.tree_pelates.insert('', 'end', values=display_row)
                
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
            
            # Get the flags from the last column
            available_items = values[5].split(", ") if values[5] else []
            
            # Enable/disable buttons based on what's available
            if "Έγγραφα" in available_items:
                self.btn_open_doc.config(state='normal')
            else:
                self.btn_open_doc.config(state='disabled')
                
            if "Συνταγές" in available_items:
                self.btn_view_prescriptions.config(state='normal')
            else:
                self.btn_view_prescriptions.config(state='disabled')
                
            if "Σημειώσεις" in available_items:
                self.btn_view_notes.config(state='normal')
            else:
                self.btn_view_notes.config(state='disabled')
        else:
            self.btn_open_doc.config(state='disabled')
            self.btn_view_prescriptions.config(state='disabled')
            self.btn_view_notes.config(state='disabled')

    def anigma_egrafou(self):
        selected = self.tree_pelates.selection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε έναν πελάτη")
            return

        item = self.tree_pelates.item(selected[0])
        values = item['values']
        customer_name = f"{values[0]} {values[1]}".strip()
        
        # Read the original file to get the documents
        documents = []
        try:
            with open(FILE_NAME, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if row[0].strip() == values[0].strip() and row[1].strip() == values[1].strip():
                        if len(row) > 5 and row[5]:  # Check if documents exist
                            documents = [doc.strip() for doc in row[5].split(",") if doc.strip()]
                        break

            if not documents:
                messagebox.showinfo("Πληροφορίες", "Ο πελάτης δεν έχει έγγραφα.")
                return

            if len(documents) == 1:
                doc_path = os.path.join(DOCUMENTS_DIR, documents[0])
                if not os.path.exists(doc_path):
                    messagebox.showerror("Σφάλμα", "Το αρχείο δεν βρέθηκε!")
                    return
                try:
                    os.startfile(doc_path)
                except Exception as e:
                    messagebox.showerror("Σφάλμα", f"Δεν ήταν δυνατό το άνοιγμα του εγγράφου: {str(e)}")
            else:
                dialog = tk.Toplevel(self.root)
                dialog.title("Επιλογή Εγγράφου")
                dialog.geometry("500x400")
                dialog.transient(self.root)
                dialog.grab_set()
                dialog.focus_set()
                center_window(dialog)

                tk.Label(dialog, text="Επιλέξτε έγγραφο για προβολή:", font=("Arial", 10, "bold")).pack(pady=10)

                docs_listbox = tk.Listbox(dialog, height=15, width=60)
                docs_listbox.pack(padx=10, pady=5)
                
                existing_docs = []
                for doc in documents:
                    doc_path = os.path.join(DOCUMENTS_DIR, doc.strip())
                    if os.path.exists(doc_path):
                        docs_listbox.insert(tk.END, doc.strip())
                        existing_docs.append(doc.strip())
                    else:
                        logging.warning(f"Το έγγραφο {doc} δεν βρέθηκε για τον πελάτη {customer_name}")

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
                tk.Button(dialog, text="Ακύρωση", command=dialog.destroy, bg='red', fg='white', width=15).pack(pady=5)

        except Exception as e:
            logging.error(f"Σφάλμα κατά το άνοιγμα εγγράφων: {str(e)}")
            messagebox.showerror("Σφάλμα", f"Σφάλμα κατά το άνοιγμα εγγράφων: {str(e)}")

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

    def toggle_help_drawer(self):
        # Εμφάνιση modal παραθύρου στο κέντρο της οθόνης
        if hasattr(self, 'help_modal') and self.help_modal and self.help_modal.winfo_exists():
            self.help_modal.destroy()
            self.help_modal = None
            return
        self.help_modal = tk.Toplevel(self.root)
        self.help_modal.title('Βοήθεια')
        self.help_modal.geometry('350x150')
        self.help_modal.transient(self.root)
        self.help_modal.grab_set()
        self.help_modal.focus_set()
        self.help_modal.resizable(False, False)
        # Κεντράρισμα
        self.help_modal.update_idletasks()
        w = self.help_modal.winfo_width()
        h = self.help_modal.winfo_height()
        ws = self.help_modal.winfo_screenwidth()
        hs = self.help_modal.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.help_modal.geometry(f'+{x}+{y}')
        # Περιεχόμενο
        frame = tk.Frame(self.help_modal, bg='#fff')
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        btn_update = ttk.Button(frame, text='Έλεγχος για Ενημέρωση', command=lambda: [self.help_modal.destroy(), self.check_for_update()])
        btn_update.pack(fill='x', pady=8)
        btn_about = ttk.Button(frame, text='Σχετικά με το Πρόγραμμα', command=lambda: [self.help_modal.destroy(), self.show_about()])
        btn_about.pack(fill='x', pady=8)
        # Κλείσιμο όταν κάνεις κλικ εκτός
        def close_modal(event):
            if self.help_modal:
                self.help_modal.destroy()
                self.help_modal = None
        self.help_modal.bind('<FocusOut>', close_modal)

    def populate_help_drawer(self):
        for widget in self.help_drawer.winfo_children():
            widget.destroy()
        btn_update = ttk.Button(self.help_drawer, text='Έλεγχος για Ενημέρωση', command=self.check_for_update)
        btn_update.pack(side='left', padx=20, pady=10)
        btn_about = ttk.Button(self.help_drawer, text='Σχετικά με το Πρόγραμμα', command=self.show_about)
        btn_about.pack(side='left', padx=20, pady=10)

    def show_about(self):
        about_win = tk.Toplevel(self.root)
        about_win.title('Σχετικά με το Πρόγραμμα')
        about_win.geometry('700x600')
        about_win.transient(self.root)
        about_win.grab_set()
        
        # Center the window
        about_win.update_idletasks()
        w = about_win.winfo_width()
        h = about_win.winfo_height()
        ws = about_win.winfo_screenwidth()
        hs = about_win.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        about_win.geometry(f'+{x}+{y}')
        
        # Create main frame with padding
        main_frame = tk.Frame(about_win, padx=20, pady=10)
        main_frame.pack(expand=True, fill='both')
        
        # Add logo if available
        if self.prescription_logo:
            logo_label = tk.Label(main_frame, image=self.prescription_logo)
            logo_label.pack(pady=(0, 20))
        
        # Get version info
        version = '1.0.0'  # Default version
        try:
            with open('version.txt', encoding='utf-8') as f:
                version = f.read().strip()
        except Exception:
            pass
        
        # Version label
        version_label = tk.Label(main_frame, text=f'Έκδοση {version}', font=('Segoe UI', 12, 'bold'))
        version_label.pack(pady=(0, 20))
        
        # Create text widget for content
        txt = scrolledtext.ScrolledText(main_frame, wrap='word', font=('Segoe UI', 11))
        txt.pack(expand=True, fill='both')
        
        # Try to read README content
        try:
            with open('README.md', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = '''Το Optic είναι ένα ολοκληρωμένο σύστημα διαχείρισης για καταστήματα οπτικών.
            
Δεν βρέθηκε το αρχείο README.md με την πλήρη τεκμηρίωση.

Για περισσότερες πληροφορίες και υποστήριξη, επικοινωνήστε με την ομάδα ανάπτυξης.'''
            logging.error(f"Error reading README.md: {str(e)}")
        
        txt.insert('1.0', content)
        txt.config(state='disabled')
        
        # Create button frame
        button_frame = tk.Frame(about_win)
        button_frame.pack(pady=15)
        
        # Close button with improved styling
        close_btn = ttk.Button(button_frame, text='Κλείσιμο', command=about_win.destroy)
        close_btn.pack()

    def check_for_update(self):
        import threading, requests
        def do_check():
            try:
                # Χρησιμοποιούμε τα σωστά URLs για τις ενημερώσεις
                version_url = 'https://raw.githubusercontent.com/Nikiforos65/Optic/main/version.txt'
                exe_url = 'https://github.com/Nikiforos65/Optic/releases/latest/download/optic.zip'
                local_version = '1.0.0'
                try:
                    with open('version.txt', encoding='utf-8') as f:
                        local_version = f.read().strip()
                except Exception:
                    pass
                r = requests.get(version_url, timeout=5)
                if r.status_code == 200:
                    remote_version = r.text.strip()
                    if remote_version != local_version:
                        if messagebox.askyesno('Ενημέρωση', f'Βρέθηκε νέα έκδοση ({remote_version}). Θέλετε να την κατεβάσετε;'):
                            self.download_update(exe_url)
                    else:
                        messagebox.showinfo('Έλεγχος Ενημέρωσης', 'Έχετε ήδη την τελευταία έκδοση.')
                else:
                    messagebox.showerror('Σφάλμα', 'Αποτυχία ελέγχου για ενημέρωση.')
            except Exception as e:
                messagebox.showerror('Σφάλμα', f'Αποτυχία ελέγχου για ενημέρωση: {e}')
        threading.Thread(target=do_check, daemon=True).start()

    def download_update(self, zip_url):
        import requests, zipfile, os, sys, subprocess
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if getattr(sys, 'frozen', False):
                current_dir = os.path.dirname(sys.executable)
            
            # Κατεβάζουμε το zip στον τρέχοντα φάκελο
            temp_zip = os.path.join(current_dir, "optic_update.zip")
            r = requests.get(zip_url, stream=True)
            total = int(r.headers.get('content-length', 0))
            
            # Δείχνουμε πρόοδο λήψης
            progress = tk.Toplevel()
            progress.title('Λήψη Ενημέρωσης')
            progress.geometry('300x150')
            progress.transient(self.root)
            progress.grab_set()
            
            label = ttk.Label(progress, text='Λήψη ενημέρωσης...')
            label.pack(pady=10)
            
            progressbar = ttk.Progressbar(progress, length=200, mode='determinate')
            progressbar.pack(pady=10)
            
            # Κατεβάζουμε το αρχείο
            with open(temp_zip, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            progressbar['value'] = (downloaded / total) * 100
                            progress.update()
            
            progress.destroy()
            
            # Δημιουργούμε batch script για την ενημέρωση
            batch_path = os.path.join(current_dir, "update.bat")
            with open(batch_path, 'w', encoding='utf-8') as f:
                f.write('@echo off\n')
                f.write('timeout /t 1 /nobreak >nul\n')
                # Χρησιμοποιούμε PowerShell για την αποσυμπίεση
                f.write(f'powershell -Command "Expand-Archive -Force \'{temp_zip}\' \'{current_dir}\'\n"')
                f.write(f'del /f "{temp_zip}"\n')
                f.write(f'start "" "{os.path.join(current_dir, "optic.exe")}"\n')
                f.write('exit\n')
            
            # Εκτελούμε το batch script και κλείνουμε το πρόγραμμα
            subprocess.Popen(batch_path, shell=True)
            self.root.quit()
            
        except Exception as e:
            messagebox.showerror('Σφάλμα', f'Σφάλμα κατά την ενημέρωση: {str(e)}')

    def create_prescription_form(self, parent_window, customer_name=''):
        PRESCRIPTION_CSV = "συνταγολόγια.csv"
        if not os.path.exists(PRESCRIPTION_CSV):
            with open(PRESCRIPTION_CSV, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Ημερομηνία", "Ονοματεπώνυμο",
                    "Μακριά_Sph1", "Μακριά_Cyl1", "Μακριά_Axe1", "Μακριά_Sph2", "Μακριά_Cyl2", "Μακριά_Axe2", "Μακριά_Ecartement",
                    "Πλησίον_Sph1", "Πλησίον_Cyl1", "Πλησίον_Axe1", "Πλησίον_Sph2", "Πλησίον_Cyl2", "Πλησίον_Axe2", "Πλησίον_Ecartement",
                    "Δ_Γραμμές", "A_Γραμμές"
                ])

        prescription_window = tk.Toplevel(parent_window)
        prescription_window.title("Συνταγή")
        prescription_window.geometry("1400x800")
        prescription_window.transient(parent_window)
        prescription_window.grab_set()
        center_window(prescription_window)

        canvas = tk.Canvas(prescription_window, width=1100, height=350, bg='white')
        canvas.pack(padx=10, pady=10)

        if self.prescription_logo:
            canvas.create_image(50, 30, image=self.prescription_logo, anchor='nw')

        canvas.create_text(300, 50, text="Ονοματεπώνυμο:", anchor='w', font=('Arial', 12))
        canvas.create_line(420, 55, 1000, 55, dash=(4, 2))
        canvas.create_text(430, 50, text=customer_name, anchor='w', font=('Arial', 12))

        def draw_protractor(cx, cy, letter):
            radius = 120
            canvas.create_arc(cx-radius, cy-radius, cx+radius, cy+radius, start=0, extent=180, style='arc', width=2)
            canvas.create_line(cx-radius, cy, cx+radius, cy, width=2)
            for angle in range(0, 181):
                rad = math.radians(angle)
                arc_x = cx + radius * math.cos(rad)
                arc_y = cy - radius * math.sin(rad)
                dx = math.cos(rad)
                dy = -math.sin(rad)
                if angle % 10 == 0:
                    line_len = 25
                else:
                    line_len = 12
                x1 = arc_x
                y1 = arc_y
                x2 = arc_x + line_len * dx
                y2 = arc_y + line_len * dy
                canvas.create_line(x1, y1, x2, y2, width=2 if angle % 10 == 0 else 1)
                if angle % 10 == 0:
                    label_dist = 40
                    label_x = cx + (radius + label_dist) * math.cos(rad)
                    label_y = cy - (radius + label_dist) * math.sin(rad)
                    canvas.create_text(label_x, label_y, text=str(angle), font=('Arial', 9))
            canvas.create_text(cx, cy+30, text=letter, font=('Arial', 32, 'bold'))

        draw_protractor(350, 260, "Δ")
        draw_protractor(800, 260, "A")

        # Drawing functionality
        drawing = {'active': False, 'x': None, 'y': None, 'lines_D': [], 'lines_A': [], 'current': None}

        def start_draw(event):
            drawing['active'] = True
            drawing['x'] = event.x
            drawing['y'] = event.y
            # Determine which protractor
            if abs(event.x - 350) < 130:
                drawing['current'] = 'D'
            elif abs(event.x - 800) < 130:
                drawing['current'] = 'A'
            else:
                drawing['current'] = None

        def draw(event):
            if drawing['active'] and drawing['current']:
                canvas.create_line(drawing['x'], drawing['y'], event.x, event.y, fill='red', width=2)
                if drawing['current'] == 'D':
                    drawing['lines_D'].append((drawing['x'], drawing['y'], event.x, event.y))
                elif drawing['current'] == 'A':
                    drawing['lines_A'].append((drawing['x'], drawing['y'], event.x, event.y))
                drawing['x'] = event.x
                drawing['y'] = event.y

        def stop_draw(event):
            drawing['active'] = False
            drawing['current'] = None

        canvas.bind('<Button-1>', start_draw)
        canvas.bind('<B1-Motion>', draw)
        canvas.bind('<ButtonRelease-1>', stop_draw)

        table_frame = tk.Frame(prescription_window)
        table_frame.pack(pady=10)

        headers = ["", "Sph.", "Cyl.", "Axe", "Sph.", "Cyl.", "Axe", "Ecartement Pupillaire"]
        col_widths = [10, 18, 18, 18, 18, 18, 18, 26]

        for col, header in enumerate(headers):
            e = tk.Entry(table_frame, width=col_widths[col], font=('Arial', 11, 'bold'), justify='center')
            e.grid(row=0, column=col, sticky='nsew', ipady=8)
            e.insert(0, header)
            e.config(state='readonly')

        # Changed order of labels
        for row_idx, label in enumerate(["Μακριά", "Πλησίον"]):
            e = tk.Entry(table_frame, width=10, font=('Arial', 11), justify='center')
            e.grid(row=row_idx+1, column=0, sticky='nsew', ipady=12)
            e.insert(0, label)
            e.config(state='readonly')

        entries = []
        for row_idx in range(2):
            row_entries = []
            for col in range(1, 8):
                t = tk.Text(table_frame, width=col_widths[col], height=2, font=('Arial', 11), wrap='word')
                t.grid(row=row_idx+1, column=col, sticky='nsew', padx=1, pady=1)
                row_entries.append(t)
            entries.append(row_entries)

        def clear_drawing():
            canvas.delete('all')
            if self.prescription_logo:
                canvas.create_image(50, 30, image=self.prescription_logo, anchor='nw')
            canvas.create_text(300, 50, text="Ονοματεπώνυμο:", anchor='w', font=('Arial', 12))
            canvas.create_line(420, 55, 1000, 55, dash=(4, 2))
            canvas.create_text(430, 50, text=customer_name, anchor='w', font=('Arial', 12))
            draw_protractor(350, 260, "Δ")
            draw_protractor(800, 260, "A")
            drawing['lines_D'].clear()
            drawing['lines_A'].clear()

        def save_csv():
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row = [timestamp, customer_name]
                
                # Get values from entries in the correct order (Μακριά first, then Πλησίον)
                for row_entries in entries:
                    for entry in row_entries:
                        row.append(entry.get("1.0", "end-1c"))
                
                # Add the drawing lines
                row.append(str(drawing['lines_D']))
                row.append(str(drawing['lines_A']))

                with open(PRESCRIPTION_CSV, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(row)

                messagebox.showinfo("Επιτυχία", "Η συνταγή αποθηκεύτηκε επιτυχώς!")
                prescription_window.destroy()
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την αποθήκευση: {str(e)}")

        button_frame = tk.Frame(prescription_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Καθαρισμός Σχεδίασης", command=clear_drawing, bg='orange', fg='black', width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Αποθήκευση", command=save_csv, bg='green', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Ακύρωση", command=prescription_window.destroy, bg='red', fg='white', width=15).pack(side=tk.LEFT, padx=5)

    def provoli_syntagon(self):
        selected = self.tree_pelates.selection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε έναν πελάτη")
            return
        item = self.tree_pelates.item(selected[0])
        values = item['values']
        # Δημιουργία ονόματος πελάτη, χρησιμοποιώντας μόνο το επώνυμο αν υπάρχει
        customer_name = str(values[0])
        if values[1]:  # Αν υπάρχει επώνυμο
            customer_name = f"{str(values[0])} {str(values[1])}"
        customer_name = customer_name.strip()
        
        prescription_rows = []
        PRESCRIPTION_CSV = "συνταγολόγια.csv"
        if not os.path.exists(PRESCRIPTION_CSV):
            messagebox.showinfo("Πληροφορία", "Δεν υπάρχουν αποθηκευμένες συνταγές για αυτόν τον πελάτη.")
            return
        with open(PRESCRIPTION_CSV, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                # Normalize both names by removing extra spaces and converting to lowercase
                if len(row) > 1 and row[1].strip().replace('  ', ' ').lower() == customer_name.strip().replace('  ', ' ').lower():
                    prescription_rows.append(row)
        if not prescription_rows:
            messagebox.showinfo("Πληροφορία", "Δεν βρέθηκαν συνταγές για τον πελάτη.")
            return
        def show_prescription(row):
            win = tk.Toplevel(self.root)
            win.title(f"Συνταγή για {customer_name} - {row[0]}")
            win.geometry("1400x800")
            win.transient(self.root)
            win.grab_set()
            center_window(win)
            canvas = tk.Canvas(win, width=1100, height=350, bg='white')
            canvas.pack(padx=10, pady=10)
            if self.prescription_logo:
                canvas.create_image(50, 30, image=self.prescription_logo, anchor='nw')
            canvas.create_text(300, 50, text="Ονοματεπώνυμο:", anchor='w', font=('Arial', 12))
            canvas.create_line(420, 55, 1000, 55, dash=(4, 2))
            canvas.create_text(430, 50, text=customer_name, anchor='w', font=('Arial', 12))
            def draw_protractor(cx, cy, letter):
                radius = 120
                canvas.create_arc(cx-radius, cy-radius, cx+radius, cy+radius, start=0, extent=180, style='arc', width=2)
                canvas.create_line(cx-radius, cy, cx+radius, cy, width=2)
                for angle in range(0, 181):
                    rad = math.radians(angle)
                    arc_x = cx + radius * math.cos(rad)
                    arc_y = cy - radius * math.sin(rad)
                    dx = math.cos(rad)
                    dy = -math.sin(rad)
                    if angle % 10 == 0:
                        line_len = 25
                    else:
                        line_len = 12
                    x1 = arc_x
                    y1 = arc_y
                    x2 = arc_x + line_len * dx
                    y2 = arc_y + line_len * dy
                    canvas.create_line(x1, y1, x2, y2, width=2 if angle % 10 == 0 else 1)
                    if angle % 10 == 0:
                        label_dist = 40
                        label_x = cx + (radius + label_dist) * math.cos(rad)
                        label_y = cy - (radius + label_dist) * math.sin(rad)
                        canvas.create_text(label_x, label_y, text=str(angle), font=('Arial', 9))
                canvas.create_text(cx, cy+30, text=letter, font=('Arial', 32, 'bold'))
            draw_protractor(350, 260, "Δ")
            draw_protractor(800, 260, "A")
            # --- Εμφάνιση αποθηκευμένων γραμμών ---
            try:
                lines_D = eval(row[-2]) if len(row) > 16 else []
                lines_A = eval(row[-1]) if len(row) > 17 else []
                for l in lines_D:
                    canvas.create_line(*l, fill='red', width=2)
                for l in lines_A:
                    canvas.create_line(*l, fill='red', width=2)
            except Exception:
                pass
            table_frame = tk.Frame(win)
            table_frame.pack(pady=10)
            headers_table = ["", "Sph.", "Cyl.", "Axe", "Sph.", "Cyl.", "Axe", "Ecartement Pupillaire"]
            col_widths = [10, 18, 18, 18, 18, 18, 18, 26]
            for col, header in enumerate(headers_table):
                e = tk.Entry(table_frame, width=col_widths[col], font=('Arial', 11, 'bold'), justify='center')
                e.grid(row=0, column=col, sticky='nsew', ipady=8)
                e.insert(0, header)
                e.config(state='readonly')
            for row_idx, label in enumerate(["Μακριά", "Πλησίον"]):
                e = tk.Entry(table_frame, width=10, font=('Arial', 11), justify='center')
                e.grid(row=row_idx+1, column=0, sticky='nsew', ipady=12)
                e.insert(0, label)
                e.config(state='readonly')
            idx = 2
            for row_idx in range(2):
                for col in range(1, 8):
                    t = tk.Text(table_frame, width=col_widths[col], height=2, font=('Arial', 11), wrap='word')
                    t.grid(row=row_idx+1, column=col, sticky='nsew', padx=1, pady=1)
                    val = row[idx] if idx < len(row) else ""
                    t.insert("1.0", val)
                    t.config(state='disabled', bg='#f0f0f0')
                    idx += 1
            ttk.Button(win, text="Κλείσιμο", command=win.destroy).pack(pady=10)
        if len(prescription_rows) == 1:
            show_prescription(prescription_rows[0])
        else:
            sel_win = tk.Toplevel(self.root)
            sel_win.title(f"Επιλογή Συνταγής για {customer_name}")
            sel_win.geometry("500x400")
            sel_win.transient(self.root)
            sel_win.grab_set()
            center_window(sel_win)
            tk.Label(sel_win, text="Επιλέξτε συνταγή (ημερομηνία):", font=("Arial", 12, "bold")).pack(pady=10)
            lb = tk.Listbox(sel_win, height=15, width=60)
            lb.pack(padx=10, pady=5)
            for row in prescription_rows:
                lb.insert(tk.END, f"{row[0]} - {customer_name}")
            def open_selected():
                sel = lb.curselection()
                if sel:
                    show_prescription(prescription_rows[sel[0]])
                    sel_win.destroy()
            ttk.Button(sel_win, text="Προβολή", command=open_selected).pack(pady=10)
            ttk.Button(sel_win, text="Κλείσιμο", command=sel_win.destroy).pack(pady=5)

    def create_notes_form(self, parent_window, customer_name=''):
        notes_window = tk.Toplevel(parent_window)
        notes_window.title("Σημειώσεις")
        notes_window.geometry("800x600")
        notes_window.transient(parent_window)
        notes_window.grab_set()
        center_window(notes_window)

        # Δημιουργία του text area
        text_area = scrolledtext.ScrolledText(notes_window, wrap=tk.WORD, width=80, height=30)
        text_area.pack(expand=True, fill='both', padx=10, pady=10)

        button_frame = tk.Frame(notes_window)
        button_frame.pack(pady=10)

        def save_notes():
            try:
                notes_content = text_area.get("1.0", tk.END).strip()
                if not notes_content:
                    messagebox.showwarning("Προειδοποίηση", "Οι σημειώσεις είναι κενές!")
                    return

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                with open(NOTES_CSV, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp, customer_name, notes_content])

                messagebox.showinfo("Επιτυχία", "Οι σημειώσεις αποθηκεύτηκαν επιτυχώς!")
                notes_window.destroy()
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Σφάλμα κατά την αποθήκευση: {str(e)}")

        tk.Button(button_frame, text="Αποθήκευση", command=save_notes, bg='green', fg='white', width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Ακύρωση", command=notes_window.destroy, bg='red', fg='white', width=15).pack(side=tk.LEFT, padx=5)

    def provoli_seimeioseon(self):
        selected = self.tree_pelates.selection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Παρακαλώ επιλέξτε έναν πελάτη")
            return

        item = self.tree_pelates.item(selected[0])
        values = item['values']
        customer_name = f"{values[0]} {values[1]}".strip()

        if not os.path.exists(NOTES_CSV):
            messagebox.showinfo("Πληροφορία", "Δεν υπάρχουν αποθηκευμένες σημειώσεις.")
            return

        notes = []
        with open(NOTES_CSV, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row[1].strip().lower() == customer_name.lower():
                    notes.append(row)

        if not notes:
            messagebox.showinfo("Πληροφορία", "Δεν υπάρχουν σημειώσεις για αυτόν τον πελάτη.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Σημειώσεις - {customer_name}")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        center_window(dialog)

        tk.Label(dialog, text=f"Σημειώσεις για: {customer_name}", font=("Arial", 12, "bold")).pack(pady=10)
        
        notes_frame = tk.Frame(dialog)
        notes_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Create a canvas with scrollbar
        canvas = tk.Canvas(notes_frame)
        scrollbar = ttk.Scrollbar(notes_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Display notes
        for note in notes:
            note_frame = tk.Frame(scrollable_frame, relief='solid', borderwidth=1)
            note_frame.pack(fill='x', expand=True, pady=5, padx=5)
            
            header_frame = tk.Frame(note_frame)
            header_frame.pack(fill='x', padx=5, pady=5)
            
            tk.Label(header_frame, text=f"Ημερομηνία: {note[0]}", font=("Arial", 10, "bold")).pack(side='left')
            
            text_widget = tk.Text(note_frame, wrap='word', height=4, width=80)
            text_widget.pack(fill='both', expand=True, padx=5, pady=5)
            text_widget.insert('1.0', note[2])
            text_widget.config(state='disabled')

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Button(dialog, text="Κλείσιμο", command=dialog.destroy, bg='red', fg='white', width=15).pack(pady=10)

    def run(self):
        self.root.mainloop()

def check_duplicate_customer(name, surname, phone, email_val):
    with open(FILE_NAME, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if (row[0].lower() == name.lower() and row[1].lower() == surname.lower()) or \
               (phone and row[2] == phone) or \
               (email_val and row[3] and row[3].lower() == email_val.lower()):
                return True
    return False

if __name__ == "__main__":
    app = OpticalSystem()
    app.run()
