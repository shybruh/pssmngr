import base64
import csv
import getpass
import hashlib
import os
import pickle
import time
import tkinter
import tkinter.messagebox as messagebox
import uuid
from tkinter import filedialog

import customtkinter
from cryptography.fernet import Fernet

# Define global variables
passwords = {}
FILE_NAME = "pss.dat"
master_password_file = "master_password.dat"
encryption_key = None
# Function to generate a key from a password
def generate_key(password):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
# Function to encrypt data
def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode())
# Function to decrypt data
def decrypt_data(data, key):
    f = Fernet(key)
    return f.decrypt(data).decode()
# Function to save passwords to file
def save_passwords():
    try:
        with open(FILE_NAME, "wb") as f:
            encrypted_passwords = {k: {key: encrypt_data(value, encryption_key) for key, value in v.items()} for k, v in passwords.items()}
            pickle.dump(encrypted_passwords, f)
        messagebox.showinfo("Saved", "Passwords saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save passwords: {e}")
# Function to load passwords from file
def load_passwords():
    global passwords
    try:
        with open(FILE_NAME, "rb") as f:
            encrypted_passwords = pickle.load(f)
            passwords = {k: {key: decrypt_data(value, encryption_key) for key, value in v.items()} for k, v in encrypted_passwords.items()}
    except FileNotFoundError:
        passwords = {}  # If file does not exist, start with an empty dictionary
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load passwords: {e}")
# Function to save master password hash to file
def save_master_password(password):
    password_hash = generate_key(password)
    with open(master_password_file, "wb") as f:
        f.write(password_hash)
# Function to check master password
def check_master_password(password):
    if not os.path.exists(master_password_file):
        return False
    with open(master_password_file, "rb") as f:
        saved_password_hash = f.read()
    return saved_password_hash == generate_key(password)
# Function to switch to a specified frame
def show_frame(frame):
    frame.tkraise()
# Function to handle login
def handle_login():
    global encryption_key
    password = entry_login_password.get()
    if check_master_password(password):
        encryption_key = generate_key(password)
        load_passwords()
        show_frame(loading_frame)
        root.after(100, simulate_loading)  # Start the loading simulation bar
    else:
        messagebox.showerror("Error", "Invalid master password")
# Simulate loading process
def simulate_loading():
    for i in range(101):
        progress_bar.set(i / 100)
        root.update_idletasks()
        time.sleep(0.01)
    show_frame(main_frame)
# Function to handle first-time setup
def first_time_setup():
    global encryption_key
    master_password = str(uuid.uuid4())[:8]
    encryption_key = generate_key(master_password)
    save_master_password(master_password)
    load_passwords()
    text_master_password.configure(state="normal")
    text_master_password.insert("end", master_password)
    text_master_password.configure(state="disabled")
    show_frame(display_master_password_frame)
# Function to add a password
def add_password():
    show_frame(add_password_frame)
def save_new_password():
    email = entry_email.get()
    website = entry_website.get()
    password = entry_password.get()
    if not (email and website and password):
        messagebox.showerror("Error", "Please fill in all fields")
        return
    new_id = str(uuid.uuid4())[:8]
    while new_id in passwords:
        new_id = str(uuid.uuid4())[:8]
    passwords[new_id] = {"email": email, "website": website, "password": password}
    save_passwords()
    show_frame(main_frame)
    messagebox.showinfo("Success", "Password added successfully!")
# Function to edit a password
def edit_password():
    show_frame(edit_password_frame)
def perform_search():
    password_id = entry_search_id.get()
    if password_id in passwords:
        password_info = passwords[password_id]
        entry_edit_email.delete(0, 'end')
        entry_edit_website.delete(0, 'end')
        entry_edit_password.delete(0, 'end')
        entry_edit_email.insert("end", password_info['email'])
        entry_edit_website.insert("end", password_info['website'])
        entry_edit_password.insert("end", password_info['password'])
        show_frame(edit_password_details_frame)
    else:
        messagebox.showerror("Error", "Password ID not found")
def save_edited_password():
    password_id = entry_search_id.get()
    email = entry_edit_email.get()
    website = entry_edit_website.get()
    password = entry_edit_password.get()
    if not (email and website and password):
        messagebox.showerror("Error", "Please fill in all fields")
        return
    passwords[password_id] = {"email": email, "website": website, "password": password}
    save_passwords()
    show_frame(main_frame)
    messagebox.showinfo("Success", "Password edited successfully!")
# Function to delete a password
def delete_password():
    show_frame(delete_password_frame)
def perform_delete():
    password_id = entry_delete_id.get()
    if password_id in passwords:
        confirm_delete = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete password ID: {password_id}?")
        if confirm_delete:
            del passwords[password_id]
            save_passwords()
            messagebox.showinfo("Success", f"Password ID: {password_id} deleted successfully!")
            show_frame(main_frame)
    else:
        messagebox.showerror("Error", "Password ID not found")
# Function to display all passwords
def show_all_passwords():
    text_display.configure(state="normal")  # Enable editing to update text
    text_display.delete(1.0, "end")  # Clear current text
    text_display.insert("end", format_passwords())
    text_display.configure(state="disabled")  # Disable editing
    show_frame(display_passwords_frame)
def format_passwords():
    formatted_text = ""
    for password_id, password_info in passwords.items():
        formatted_text += f"ID: {password_id}\nEmail: {password_info['email']}\nWebsite: {password_info['website']}\nPassword: {password_info['password']}\n\n"
    return formatted_text
def import_passwords():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return
    try:
        with open(file_path, "r") as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                email = row.get("username")
                website = row.get("url")
                password = row.get("password")
                if not (email and website and password):
                    continue
                new_id = str(uuid.uuid4())[:8]
                while new_id in passwords:
                    new_id = str(uuid.uuid4())[:8]
                passwords[new_id] = {"email": email, "website": website, "password": password}
        save_passwords()
        messagebox.showinfo("Success", "Passwords imported successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import passwords: {e}")

# Get the username of the current user
username = getpass.getuser()
# Initialize customtkinter
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")
root = customtkinter.CTk()
root.title("psmngr ver.1.0.0")
root.resizable(False, False)  # Disable window resizing
root.iconbitmap("shield.ico")
img = tkinter.PhotoImage(width=1, height=1)
root.iconphoto(True, img)
# Create frames
login_frame = customtkinter.CTkFrame(root, width=450, height=300,fg_color="#141414")
loading_frame = customtkinter.CTkFrame(root, width=450, height=300,fg_color="#141414")
main_frame = customtkinter.CTkFrame(root, width=450, height=300,fg_color="#141414")
add_password_frame = customtkinter.CTkFrame(root, width=450, height=300,fg_color="#141414")
edit_password_frame = customtkinter.CTkFrame(root, width=450, height=300,fg_color="#141414")
edit_password_details_frame = customtkinter.CTkFrame(root, width=450, height=300,fg_color="#141414")
delete_password_frame = customtkinter.CTkFrame(root, width=450, height=300,fg_color="#141414")
display_passwords_frame = customtkinter.CTkFrame(root, width=450, height=300,fg_color="#141414")
display_master_password_frame = customtkinter.CTkFrame(root, width=400, height=400,fg_color="#141414")
for frame in (login_frame, loading_frame, main_frame, add_password_frame, edit_password_frame, edit_password_details_frame, delete_password_frame, display_passwords_frame, display_master_password_frame):
    frame.grid(row=7, column=3, sticky="nsew")
# Login frame widgets
label_welcome = customtkinter.CTkLabel(login_frame, text=f"welcome, {username}", font=("JetBrains mono bold", 15))
entry_login_password = customtkinter.CTkEntry(login_frame, placeholder_text="password", show="*", font=("JetBrains mono",14))
button_login = customtkinter.CTkButton(login_frame, text="login", command=handle_login, corner_radius=5, hover_color="#2b2b2b",fg_color="transparent", border_color="white", border_width=1, font=("JetBrains mono",14))
label_welcome.grid(row=0, column=2, padx=5, pady=5)
entry_login_password.grid(row=1, column=2, padx=5, pady=5)
button_login.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
login_frame.grid_rowconfigure(0, weight=1)
login_frame.grid_rowconfigure(3, weight=1)
login_frame.grid_columnconfigure(0, weight=1)
login_frame.grid_columnconfigure(3, weight=1)
# Loading frame widgets
progress_bar = customtkinter.CTkProgressBar(loading_frame, width=200, progress_color="white")
progress_bar.set(0)
progress_bar.grid(row=1, column=1, pady=20)
label_loading = customtkinter.CTkLabel(loading_frame, text="loading...", font=("JetBrains mono",14))
label_loading.grid(row=2, column=1, pady=20)
loading_frame.grid_rowconfigure(0, weight=1)
loading_frame.grid_rowconfigure(3, weight=1)
loading_frame.grid_columnconfigure(0, weight=1)
loading_frame.grid_columnconfigure(3, weight=1)
# Main frame widgets, corner_radius=5, fg_color="transparent", border_color="white", border_width=1, font=("JetBrains mono",14)
button_add = customtkinter.CTkButton(main_frame, text="add password", command=add_password, corner_radius=5, fg_color="transparent", hover_color="#2b2b2b",border_color="white", border_width=1, font=("JetBrains mono",14))
button_edit = customtkinter.CTkButton(main_frame, text="edit password", command=edit_password, corner_radius=5, fg_color="transparent",hover_color="#2b2b2b", border_color="white", border_width=1, font=("JetBrains mono",14))
button_delete = customtkinter.CTkButton(main_frame, text="delete password", command=delete_password, corner_radius=5, fg_color="transparent",hover_color="#2b2b2b", border_color="white", border_width=1, font=("JetBrains mono",14))
button_display_all = customtkinter.CTkButton(main_frame, text="show all", command=show_all_passwords, corner_radius=5, fg_color="transparent",hover_color="#2b2b2b", border_color="white", border_width=1, font=("JetBrains mono",14))
button_import = customtkinter.CTkButton(main_frame, text="import csv", command=import_passwords, corner_radius=5, fg_color="transparent", hover_color="#2b2b2b",border_color="white", border_width=1, font=("JetBrains mono",14) )
button_add.grid(row=1, column=1, padx=10, pady=10)
button_edit.grid(row=2, column=1, padx=10, pady=10)
button_delete.grid(row=3, column=1, padx=10, pady=10)
button_display_all.grid(row=4, column=1, padx=10, pady=10)
button_import.grid(row=5, column=1, padx=10, pady=10)
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_rowconfigure(5, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(3, weight=1)
# Add password frame widgets
label_email = customtkinter.CTkLabel(add_password_frame, text="email:", font=("JetBrains mono",14))
entry_email = customtkinter.CTkEntry(add_password_frame, placeholder_text="email")
label_website = customtkinter.CTkLabel(add_password_frame, text="website:", font=("JetBrains mono",14))
entry_website = customtkinter.CTkEntry(add_password_frame, placeholder_text="website")
label_password = customtkinter.CTkLabel(add_password_frame, text="password:", font=("JetBrains mono",14))
entry_password = customtkinter.CTkEntry(add_password_frame, placeholder_text="password",show="*")
button_save_password = customtkinter.CTkButton(add_password_frame, text="save password", hover_color="#2b2b2b",command=save_new_password, corner_radius=5, fg_color="transparent", border_color="white", border_width=1, font=("JetBrains mono",14))
button_back_to_main = customtkinter.CTkButton(add_password_frame, text="back to main menu",hover_color="#2b2b2b", command=lambda: show_frame(main_frame), corner_radius=5, fg_color="transparent", border_color="white", border_width=1, font=("JetBrains mono",14))
label_email.grid(row=1, column=1, padx=10, pady=10, sticky="e")
entry_email.grid(row=1, column=2, padx=10, pady=10)
label_website.grid(row=2, column=1, padx=10, pady=10, sticky="e")
entry_website.grid(row=2, column=2, padx=10, pady=10)
label_password.grid(row=3, column=1, padx=10, pady=10, sticky="e")
entry_password.grid(row=3, column=2, padx=10, pady=10)
button_save_password.grid(row=4, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
button_back_to_main.grid(row=5, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
add_password_frame.grid_rowconfigure(0, weight=1)
add_password_frame.grid_rowconfigure(6, weight=1)
add_password_frame.grid_columnconfigure(0, weight=1)
add_password_frame.grid_columnconfigure(3, weight=1)
# Edit password frame widgets
label_search_id = customtkinter.CTkLabel(edit_password_frame, text="enter password id:", font=("JetBrains mono",14))
entry_search_id = customtkinter.CTkEntry(edit_password_frame, placeholder_text="id", font=("JetBrains mono",14))
button_search = customtkinter.CTkButton(edit_password_frame, text="search",hover_color="#2b2b2b", command=perform_search, corner_radius=5, fg_color="transparent", border_color="white", border_width=1, font=("JetBrains mono",14))
button_back_to_main = customtkinter.CTkButton(edit_password_frame, text="back to main menu", hover_color="#2b2b2b",command=lambda: show_frame(main_frame), corner_radius=5, fg_color="transparent", border_color="white", border_width=1, font=("JetBrains mono",14))
label_search_id.grid(row=1, column=1, padx=10, pady=10, sticky="e")
entry_search_id.grid(row=1, column=2, padx=10, pady=10)
button_search.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
button_back_to_main.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
edit_password_frame.grid_rowconfigure(0, weight=1)
edit_password_frame.grid_rowconfigure(4, weight=1)
edit_password_frame.grid_columnconfigure(0, weight=1)
edit_password_frame.grid_columnconfigure(3, weight=1)
# Edit password details frame widgets
label_edit_email = customtkinter.CTkLabel(edit_password_details_frame, text="email:", font=("JetBrains mono",14))
entry_edit_email = customtkinter.CTkEntry(edit_password_details_frame, placeholder_text="email")
label_edit_website = customtkinter.CTkLabel(edit_password_details_frame, text="website:", font=("JetBrains mono",14))
entry_edit_website = customtkinter.CTkEntry(edit_password_details_frame, placeholder_text="website")
label_edit_password = customtkinter.CTkLabel(edit_password_details_frame, text="password:", font=("JetBrains mono",14))
entry_edit_password = customtkinter.CTkEntry(edit_password_details_frame, placeholder_text="password", show="*", font=("JetBrains mono",14))
button_save_edited_password = customtkinter.CTkButton(edit_password_details_frame, text="save changes",hover_color="#2b2b2b", command=save_edited_password, corner_radius=5, fg_color="transparent", border_color="white", border_width=1, font=("JetBrains mono",14))
button_back_to_edit_search = customtkinter.CTkButton(edit_password_details_frame, text="back to search",hover_color="#2b2b2b", command=lambda: show_frame(edit_password_frame), corner_radius=5, fg_color="transparent", border_color="white", border_width=1, font=("JetBrains mono",14))
label_edit_email.grid(row=1, column=1, padx=10, pady=10, sticky="e")
entry_edit_email.grid(row=1, column=2, padx=10, pady=10)
label_edit_website.grid(row=2, column=1, padx=10, pady=10, sticky="e")
entry_edit_website.grid(row=2, column=2, padx=10, pady=10)
label_edit_password.grid(row=3, column=1, padx=10, pady=10, sticky="e")
entry_edit_password.grid(row=3, column=2, padx=10, pady=10)
button_save_edited_password.grid(row=4, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
button_back_to_edit_search.grid(row=5, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
edit_password_details_frame.grid_rowconfigure(0, weight=1)
edit_password_details_frame.grid_rowconfigure(6, weight=1)
edit_password_details_frame.grid_columnconfigure(0, weight=1)
edit_password_details_frame.grid_columnconfigure(3, weight=1)
# Delete password frame widgets
label_delete_id = customtkinter.CTkLabel(delete_password_frame, text="enter password id:", font=("JetBrains mono",14))
entry_delete_id = customtkinter.CTkEntry(delete_password_frame, placeholder_text="id", font=("JetBrains mono",14))
button_delete = customtkinter.CTkButton(delete_password_frame, text="Delete",hover_color="#2b2b2b", command=perform_delete, corner_radius=5, fg_color="transparent", border_color="white", border_width=1, font=("JetBrains mono",14))
button_back_to_main = customtkinter.CTkButton(delete_password_frame, text="back to main menu",hover_color="#2b2b2b", command=lambda: show_frame(main_frame), corner_radius=5, fg_color="transparent", border_color="white", border_width=1, font=("JetBrains mono",14))
label_delete_id.grid(row=1, column=1, padx=10, pady=10, sticky="e")
entry_delete_id.grid(row=1, column=2, padx=10, pady=10)
button_delete.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
button_back_to_main.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
delete_password_frame.grid_rowconfigure(0, weight=1)
delete_password_frame.grid_rowconfigure(4, weight=1)
delete_password_frame.grid_columnconfigure(0, weight=1)
delete_password_frame.grid_columnconfigure(3, weight=1)
# Display passwords frame widgets
text_display = customtkinter.CTkTextbox(display_passwords_frame, wrap="word", state="disabled", font=("JetBrains mono",14))
text_display.grid(row=1, column=1, padx=5, pady=5)
button_back_to_main = customtkinter.CTkButton(display_passwords_frame, text="back to main menu", hover_color="#2b2b2b",command=lambda: show_frame(main_frame), corner_radius=5, fg_color="transparent", border_color="white", border_width=1, font=("JetBrains mono",14))
button_back_to_main.grid(row=2, column=1, padx=10, pady=10)
display_passwords_frame.grid_rowconfigure(0, weight=1)
display_passwords_frame.grid_rowconfigure(3, weight=1)
display_passwords_frame.grid_columnconfigure(0, weight=1)
display_passwords_frame.grid_columnconfigure(3, weight=1)
# Display master password frame widgets
label_master_password = customtkinter.CTkLabel(display_master_password_frame, text="save this master password somewhere safe.\nYou cannot change it. You cannot forget it.", height=150, font=("JetBrains mono",14))
text_master_password = customtkinter.CTkTextbox(display_master_password_frame, wrap="word", state="normal", height=50, width=300, font=("JetBrains mono",14))
text_master_password.configure(state="disabled")
button_close = customtkinter.CTkButton(display_master_password_frame, width=100, text="Close",hover_color="#2b2b2b", command=lambda: show_frame(main_frame), corner_radius=5, fg_color="transparent", border_color="white", border_width=1, font=("JetBrains mono",14))
label_master_password.grid(row=1, column=1, padx=10, pady=10, sticky="w")
text_master_password.grid(row=2, column=1, padx=10, pady=10)
button_close.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
display_master_password_frame.grid_rowconfigure(0, weight=1)
display_master_password_frame.grid_rowconfigure(4, weight=1)
display_master_password_frame.grid_columnconfigure(0, weight=1)
display_master_password_frame.grid_columnconfigure(3, weight=1)
# If no master password is set, perform first-time setup
if not os.path.exists(master_password_file):
    first_time_setup()
else:
    show_frame(login_frame)
# Start the main loop
root.mainloop()
