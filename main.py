import tkinter as tk
from tkinter import font as tkfont, messagebox
from PIL import Image, ImageTk
import os
import csv

CSV_FILE = "users.csv"

class CryptoSimApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cryptosim Login")
        self.root.geometry("1000x500")
        self.root.configure(bg="#f3f3f3")

        self.blue_color = "#180c8c"
        self.white_color = "#ffffff"
        self.gray_text_color = "#9CA4AD"
        self.highlight_color = "#4361ee"

        self.title_font = tkfont.Font(family="Helvetica", size=20, weight="bold")
        self.text_font = tkfont.Font(family="Helvetica", size=10)

        self.entries = {}
        self.logo_img = self.load_image("C:/Users/emmau/vscode/CRYPTOSIM/images/cryptosim_background_f8f4fc.jpg", (100, 80))

        self.init_login_screen()

    def load_image(self, path, size):
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image not found: {path}")
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Failed to load image at {path}: {e}")
            return None

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_placeholder_entry(self, parent, icon, placeholder):
        frame = tk.Frame(parent, bg=self.white_color)
        frame.pack(pady=10)

        entry_bg = tk.Frame(frame, bg="white", bd=2, relief="groove")
        entry_bg.pack()

        if icon:
            icon_label = tk.Label(entry_bg, image=icon, bg="white")
            icon_label.image = icon
            icon_label.place(x=5, y=5)

        entry = tk.Entry(entry_bg, font=self.text_font, bd=0, relief="flat", fg="gray")
        entry.insert(0, placeholder)
        entry.pack(padx=(30, 5), pady=5, ipadx=40, ipady=4)

        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg="black", show="*" if placeholder == "Password" else "")

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg="gray", show="")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        self.entries[placeholder] = entry

    def load_users(self):
        if not os.path.exists(CSV_FILE):
            return []
        with open(CSV_FILE, newline='') as file:
            reader = csv.reader(file)
            return list(reader)

    def save_user(self, username, password):
        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([username, password])

    def register(self):
        username = self.entries["Username"].get()
        password = self.entries["Password"].get()
        if username == "" or password == "" or username == "Username" or password == "Password":
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        users = self.load_users()
        for user in users:
            if user[0] == username:
                messagebox.showerror("Error", "Username already exists.")
                return

        self.save_user(username, password)
        messagebox.showinfo("Success", "Account registered successfully!")

    def login(self):
        username = self.entries["Username"].get()
        password = self.entries["Password"].get()
        users = self.load_users()

        for user in users:
            if user[0] == username and user[1] == password:
                self.init_dashboard(username)
                return

        messagebox.showerror("Login Failed", "Incorrect username or password.")

    def init_login_screen(self):
        self.clear_window()

        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        left_frame = tk.Frame(container, bg=self.white_color)
        left_frame.pack(side="left", fill="both", expand=True)

        right_frame = tk.Frame(container, bg=self.blue_color)
        right_frame.pack(side="right", fill="both", expand=True)

        fingerprint_img = self.load_image("C:/Users/emmau/vscode/CRYPTOSIM/images/f5fd8f51-9f8b-450b-9088-0fb587266627.png", (500, 400))
        user_icon = self.load_image("C:/Users/emmau/vscode/CRYPTOSIM/images/person_24dp_7FACC9_FILL0_wght400_GRAD0_opsz24 (1).jpg", (24, 24))
        pass_icon = self.load_image("C:/Users/emmau/vscode/CRYPTOSIM/images/verified_user_24dp_7FACC9_FILL0_wght400_GRAD0_opsz24.jpg", (24, 24))

        if self.logo_img:
            logo_label = tk.Label(left_frame, image=self.logo_img, bg=self.white_color)
            logo_label.image = self.logo_img
            logo_label.pack(pady=(40, 5))

        tk.Label(left_frame, text="Please login with your info", font=self.text_font, bg=self.white_color).pack(pady=5)

        self.create_placeholder_entry(left_frame, user_icon, "Username")
        self.create_placeholder_entry(left_frame, pass_icon, "Password")

        btn_frame = tk.Frame(left_frame, bg=self.white_color)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Login", bg=self.blue_color, fg="white", font=self.text_font, relief="flat", padx=20, command=self.login).pack(side="left", padx=10)

        register_label = tk.Label(left_frame, text="Don't have an account? Register Now", font=self.text_font, fg="blue", bg=self.white_color, cursor="hand2")
        register_label.pack()
        register_label.bind("<Button-1>", lambda e: self.register())

        tk.Label(right_frame, text="Welcome to CryptoSim", font=self.title_font, fg="white", bg=self.blue_color).pack(pady=(100, 10))
        tk.Label(right_frame, text="To join our app. First you need to register. And\nverify your identity.", font=self.text_font, fg="white", bg=self.blue_color).pack(pady=10)
        if fingerprint_img:
            fingerprint_label = tk.Label(right_frame, image=fingerprint_img, bg=self.blue_color)
            fingerprint_label.image = fingerprint_img
            fingerprint_label.pack(pady=30)

    def init_dashboard(self, username):
        self.clear_window()

        sidebar = tk.Frame(self.root, bg=self.white_color, width=300)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        main_area = tk.Frame(self.root, bg="#f3f3f3")
        main_area.pack(side="right", fill="both", expand=True)

        topbar = tk.Frame(main_area, bg=self.white_color, height=50)
        topbar.pack(side="top", fill="x")
        topbar.pack_propagate(False)

        logout_btn = tk.Button(topbar, text="⭘", font=("Helvetica", 14), bg=self.white_color, relief="flat",
                            command=self.init_login_screen)
        logout_btn.pack(side="right", padx=10, pady=10)

        content = tk.Frame(main_area, bg="#f3f3f3")
        content.pack(fill="both", expand=True)

        tab_buttons = {}

        def switch_tab(tab_name):
            for widget in content.winfo_children():
                widget.destroy()
            for name, btn in tab_buttons.items():
                btn.config(bg=self.highlight_color if name == tab_name else self.white_color,
                        fg="white" if name == tab_name else self.gray_text_color)

            if tab_name == "Homepage":
                # Greeting
                greeting = tk.Label(content, text=f"Welcome, {username}", font=("Helvetica", 18, "bold"), bg="#f3f3f3", anchor="w")
                greeting.pack(padx=80, pady=(30, 10), anchor="w")

                # Top Container Frame
                top_frame = tk.Frame(content, bg="#f3f3f3")
                top_frame.pack(padx=80, fill="x")

                # Balance Box
                balance_frame = tk.Frame(top_frame, bg="white", bd=1, relief="groove")
                balance_frame.pack(side="left", fill="y", padx=(0, 20))

                card_icon = tk.Label(balance_frame, text="💳", font=("Helvetica", 32), bg="white")
                card_icon.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

                tk.Label(balance_frame, text="My Balance", font=self.text_font, fg="gray", bg="white").grid(row=0, column=1, sticky="w")
                tk.Label(balance_frame, text="$634.22 AUD", font=("Helvetica", 18, "bold"), fg="#1c1c1c", bg="white").grid(row=1, column=1, sticky="w")

                tk.Label(balance_frame, text="▲ 9.11% Today", font=("Helvetica", 10), fg="green", bg="white").grid(row=1, column=2, sticky="e", padx=10)
                deposit_btn = tk.Button(balance_frame, text="+ Deposit", bg="black", fg="white", font=("Helvetica", 10), relief="flat")
                deposit_btn.grid(row=0, column=2, sticky="e", padx=10, pady=10)

                # Action Buttons Box
                action_frame = tk.Frame(top_frame, bg="white", bd=1, relief="groove")
                action_frame.pack(side="left", fill="both", expand=True)

                def action_button(parent, symbol, text, command):
                    btn = tk.Button(parent, text=symbol, font=("Helvetica", 16, "bold"), bg=self.highlight_color, fg="white",
                                    width=4, height=2, relief="flat", command=command)
                    btn.pack(pady=(10, 5))
                    tk.Label(parent, text=text, font=("Helvetica", 10), bg="white").pack(pady=(0, 10))

                actions = [
                    ("+", "Buy", lambda: switch_tab("Buy/Sell")),
                    ("-", "Sell", lambda: switch_tab("Buy/Sell")),
                    ("↑", "Send", lambda: print("Send clicked")),
                    ("↓", "Receive", lambda: print("Receive clicked")),
                ]

                for symbol, label, cmd in actions:
                    col = tk.Frame(action_frame, bg="white")
                    col.pack(side="left", expand=True)
                    action_button(col, symbol, label, cmd)

        if self.logo_img:
            logo_label = tk.Label(sidebar, image=self.logo_img, bg=self.white_color)
            logo_label.image = self.logo_img
            logo_label.pack(pady=10)

        tabs = ["Homepage", "Buy/Sell", "Leaderboard", "Profile", "Settings"]
        for tab in tabs:
            btn = tk.Button(sidebar, text=tab, font=self.text_font, bg=self.white_color, fg=self.gray_text_color,
                            relief="flat", padx=20, pady=10, anchor="w",
                            command=lambda name=tab: switch_tab(name))
            btn.pack(fill="x", pady=5, padx=10)
            tab_buttons[tab] = btn

        switch_tab("Homepage")

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoSimApp(root)
    root.mainloop()