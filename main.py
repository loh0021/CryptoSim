"""
CryptoSimApp – A desktop GUI application for simulating cryptocurrency trading.

Overview:
---------
CryptoSimApp is a Tkinter-based GUI that allows users to simulate cryptocurrency trading with a virtual balance.
It supports account creation, login, virtual deposits/withdrawals, buying/selling crypto assets, viewing holdings,
tracking recent activity, and comparing performance via a leaderboard. Admin functions allow resetting all user data.

Main Features:
--------------
- User Authentication:
  - Simple username/password registration and login system.
  - Data persistence using JSON files stored in a `user_data/` directory.

- Trading Simulation:
  - Simulate buying and selling popular cryptocurrencies using real-time market data from CoinDesk.
  - Automatically updates user portfolio and balance based on executed trades.

- Dashboard:
  - Displays user's balance, recent activity (deposits, withdrawals, trades), and portfolio holdings.
  - Enables quick access to common actions like Buy, Sell, Send, Receive.

- Buy/Sell Market:
  - Browse real-time cryptocurrency data including price, market cap, and 24-hour change.
  - Built-in search and sorting functionality to filter cryptocurrencies.

- Leaderboard:
  - Compare all users' total net worth (USD balance + crypto value).
  - Ranked display to foster competition.

- Admin Settings:
  - View all registered users, including activity history and holdings.
  - Option to reset (delete) all user data.

Design Notes:
-------------
- GUI built using Tkinter, with consistent styles for font and color.
- All image files must be available at hardcoded paths for proper icon rendering.
- Application state is maintained in instance variables (e.g. current_username, current_balance).
- Supports tabbed navigation via sidebar for modular views (Homepage, Buy/Sell, etc.).

Data Storage Format:
--------------------
Each user is stored in a JSON file: `user_data/{username}.json`
Fields:
- username: string
- password: string
- balance: float (USD)
- holdings: dict mapping symbol → amount
- activity: list of {desc: string, color: string}

Author: (Assumed)
Date: Auto-documented July 2025
"""
import tkinter as tk
from tkinter import font as tkfont, messagebox, simpledialog
from PIL import Image, ImageTk
import os

import requests
import urllib.request
import os
import json
import shutil
USER_DATA_DIR = "user_data"
os.makedirs(USER_DATA_DIR, exist_ok=True)

class CryptoSimApp:
    def __init__(self, root):
        """Initializes the CryptoSimApp GUI and sets up the login screen."""
        self.root = root
        self.root.title("Cryptosim Login")
        self.root.geometry("1000x500")
        self.root.configure(bg="#f3f3f3")

        self.blue_color = "#180c8c"
        self.white_color = "#ffffff"
        self.gray_text_color = "#9CA4AD"
        self.highlight_color = "#4361ee"
        self.current_username = None
        self.current_balance = 0
        self.holdings = {}
        self.activity = []   # will hold tuples of (description, color)
        self.usd_icon = self.load_image(
            os.path.join('images', 'United-states_flag_icon_round.svg.png'),
            (16,16))


        self.title_font = tkfont.Font(family="Helvetica", size=20, weight="bold")
        self.text_font = tkfont.Font(family="Helvetica", size=10)

        self.entries = {}
        self.logo_img = self.load_image(os.path.join('images', 'cryptosim_background_f8f4fc.jpg'), (100, 80))

        self.init_login_screen()



    def clear_all_user_data(self):
        """Deletes all user data JSON files after confirmation."""
        confirm = messagebox.askyesno("Confirm", "This will delete ALL user accounts. Continue?")
        if confirm:
            if os.path.exists(USER_DATA_DIR):
                shutil.rmtree(USER_DATA_DIR)  # delete folder and contents
                os.makedirs(USER_DATA_DIR)    # recreate empty folder
            messagebox.showinfo("Reset Complete", "All user data has been deleted.")





    def load_image(self, path, size):
        """Loads and resizes an image from a file path using PIL. Returns a Tkinter-compatible PhotoImage."""
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image not found: {path}")
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Failed to load image at {path}: {e}")
            return None
        

    def user_data_path(self, username=None):
        """Constructs the path to the user data JSON file for a given or current user."""
        u = username or self.current_username
        return os.path.join(USER_DATA_DIR, f"{u}.json")

    def load_user_data(self, username):
        """Loads and parses user data from a JSON file. Returns None if invalid."""
        path = self.user_data_path(username)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # file is missing, empty, or corrupted
            return None

    def save_user_data(self):
        """Saves the current user's data to their JSON file (balance, holdings, activity)."""
        # Strip out PhotoImage objects — just keep desc & color
        serialized_activity = [
            {"desc": desc, "color": color}
            for icon, desc, color in self.activity
        ]

        data = {
            "username": self.current_username,
            "password": self.current_password,
            "balance":   self.current_balance,
            "holdings":  self.holdings,
            "activity":  serialized_activity
        }
        with open(self.user_data_path(), "w") as f:
            json.dump(data, f, indent=2)


    def fetch_coin_data(self):
        """Centralized fetch for Buy/Sell coin metadata (same API your tab uses)."""
        try:
            response = requests.get(
                'https://data-api.coindesk.com/asset/v2/metadata',
                params={
                    "asset_lookup_priority": "SYMBOL",
                    "quote_asset": "USD",
                    "asset_language": "en-US",
                    "assets": "BTC,ETH,SOL,USDT,XRP,BNB,DOGE,ADA,SHIB,TRX,LINK,AVAX",
                    "groups": "ID,PRICE,MKT_CAP,CHANGE,BASIC"
                },
                headers={"Content-type": "application/json; charset=UTF-8"}
            )
            data = response.json()
            return list(data['Data'].values())
        except Exception as e:
            print(f"Failed to fetch coin data: {e}")
            return []


    def load_all_users_data(self):
        """Returns a dict { username: user_data_dict } for every JSON in user_data/."""
        all_users = {}
        for fn in os.listdir(USER_DATA_DIR):
            if not fn.endswith(".json"):
                continue
            user = fn[:-5]
            path = os.path.join(USER_DATA_DIR, fn)
            try:
                with open(path, "r") as f:
                    all_users[user] = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                continue
        return all_users

    def get_coin_icon(self, symbol, size=(30,30)):
        """
        Tries to load symbol.png from your images folder, falling back to None.
        """
        fn = f"{symbol.lower()}.png"
        path = os.path.join(
            "C:/Users/emmau/vscode/CRYPTOSIM/images",
            fn
        )
        if os.path.exists(path):
            return self.load_image(path, size)
        return None


    def clear_window(self):
        """Clears all widgets from the current root window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_placeholder_entry(self, parent, icon, placeholder):
        """Creates a stylized entry field with placeholder and optional icon."""
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
            """TODO: Add description."""
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg="black", show="*" if placeholder == "Password" else "")

        def on_focus_out(event):
            """TODO: Add description."""
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg="gray", show="")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        self.entries[placeholder] = entry



    def register(self):
        """Registers a new user, saving their info and returning to the login screen."""
        username = self.entries["Username"].get().strip()
        password = self.entries["Password"].get().strip()
        if not username or not password or username=="Username" or password=="Password":
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if os.path.exists(self.user_data_path(username)):
            messagebox.showerror("Error", "Username already exists.")
            return

        # init new user data
        self.current_username = username
        self.current_password = password
        self.current_balance  = 0.0
        self.holdings         = {}
        self.activity         = []
        self.save_user_data()

        messagebox.showinfo("Success", "Account registered successfully!")
        self.init_login_screen()



    def login(self):
        """Authenticates a user and loads their dashboard if credentials match."""
        username = self.entries["Username"].get().strip()
        password = self.entries["Password"].get().strip()

        data = self.load_user_data(username)
        if data is None or data.get("password") != password:
            messagebox.showerror("Login Failed", "Incorrect username or password.")
            return

        # load scalar fields
        self.current_username = username
        self.current_password = password
        self.current_balance  = data.get("balance", 0.0)
        self.holdings         = data.get("holdings", {})

        # rebuild activity tuples with your USD icon
        raw_act = data.get("activity", [])
        self.activity = [
            (self.usd_icon, item["desc"], item["color"])
            for item in raw_act
        ]

        # proceed to dashboard
        self.init_dashboard(username)



    def edit_balance(self):
        """Displays a popup to choose between depositing or withdrawing USD."""
        popup = tk.Toplevel(self.root)
        popup.title("Edit Balance")
        popup.geometry("300x150")
        popup.configure(bg="white")

        tk.Label(popup, text="Choose an action:", font=("Helvetica", 12), bg="white").pack(pady=10)

        def do_deposit():
            """TODO: Add description."""
            popup.destroy()
            self.deposit()

        def do_withdraw():
            """TODO: Add description."""
            popup.destroy()
            self.withdraw()

        btn_frame = tk.Frame(popup, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Deposit", width=10, bg="green", fg="white", command=do_deposit).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Withdraw", width=10, bg="red", fg="white", command=do_withdraw).pack(side="left", padx=10)

    def deposit(self):
        """Prompts for and processes a deposit into the user's balance."""
        amount = simpledialog.askfloat("Deposit", "Enter amount to deposit:")
        if amount is None or amount <= 0:
            return
        self.current_balance += amount

        # record activity immediately and refresh
        desc = f"Deposited ${amount:.2f} USD"
        self.activity.insert(0, (self.usd_icon, desc, "green"))
        if len(self.activity) > 5: 
            self.activity.pop()
        self.switch_tab("Homepage")
        self.save_user_data()

        self.update_balance_display()


    def withdraw(self):
        """Prompts for and processes a withdrawal from the user's balance."""
        amount = simpledialog.askfloat("Withdraw", "Enter amount to withdraw:")
        if amount is None or amount <= 0:
            return
        if amount > self.current_balance:
            messagebox.showerror("Error", "You cannot withdraw more than your current balance.")
            return
        self.current_balance -= amount

        # record activity immediately and refresh
        desc = f"Withdrew ${amount:.2f} USD"
        self.activity.insert(0, (self.usd_icon, desc, "red"))
        if len(self.activity) > 5:
            self.activity.pop()
        self.switch_tab("Homepage")
        self.save_user_data()

        self.update_balance_display()


    def update_balance_display(self):
        """Updates the GUI label that shows the user's current USD balance."""
        if hasattr(self, 'balance_label') and self.balance_label.winfo_exists():
            self.balance_label.config(text=f"${self.current_balance:.2f} USD")



    def init_login_screen(self):
        """Renders the login interface with entry fields and images."""
        self.clear_window()

        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        left_frame = tk.Frame(container, bg=self.white_color)
        left_frame.pack(side="left", fill="both", expand=True)

        right_frame = tk.Frame(container, bg=self.blue_color)
        right_frame.pack(side="right", fill="both", expand=True)

        fingerprint_img = self.load_image(os.path.join('images', 'f5fd8f51-9f8b-450b-9088-0fb587266627.png'), (500, 400))
        user_icon = self.load_image(os.path.join('images', 'person_24dp_7FACC9_FILL0_wght400_GRAD0_opsz24 (1).jpg'), (24, 24))
        pass_icon = self.load_image(os.path.join('images', 'verified_user_24dp_7FACC9_FILL0_wght400_GRAD0_opsz24.jpg'), (24, 24))

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
        """Initializes the main dashboard view including balance, assets, and sidebar."""
        self.clear_window()
        self.cached_coins_data = self.fetch_coin_data()
        self.displayed_coins   = list(self.cached_coins_data)
        sidebar = tk.Frame(self.root, bg=self.white_color, width=300)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        # Add logo image at the top of sidebar
        if self.logo_img:
            logo_label = tk.Label(sidebar, image=self.logo_img, bg=self.white_color)
            logo_label.image = self.logo_img
            logo_label.pack(pady=20)


        main_area = tk.Frame(self.root, bg="#f3f3f3")
        main_area.pack(side="right", fill="both", expand=True)
        credit_card_icon = self.load_image(os.path.join('images', 'cc1-1-1024x869.png'), (140, 100))

        topbar = tk.Frame(main_area, bg=self.white_color, height=50)
        topbar.pack(side="top", fill="x")
        topbar.pack_propagate(False)

        logout_btn = tk.Button(topbar, text="Logout", font=("Helvetica", 14), bg=self.white_color, relief="flat",
                            command=self.init_login_screen)
        logout_btn.pack(side="right", padx=10, pady=10)

        self.content = tk.Frame(main_area, bg="#f3f3f3")
        self.content.pack(fill="both", expand=True)

        tab_buttons = {}

        def switch_tab(tab_name):
            """TODO: Add description."""
            for widget in self.content.winfo_children():
                widget.destroy()
            for name, btn in tab_buttons.items():
                btn.config(bg=self.highlight_color if name == tab_name else self.white_color,
                        fg="white" if name == tab_name else self.gray_text_color)


            if tab_name == "Homepage":


               # Greeting Box Frame
                greeting_frame = tk.Frame(self.content, bg="white", bd=1, relief="groove", width=500)
                greeting_frame.pack(fill="x", pady=(10, 5), padx=10)
                greeting_frame.pack_propagate(True)


                greeting_label = tk.Label(
    greeting_frame,
    text=f"Welcome, {self.current_username}",
    font=("Helvetica", 18, "bold"),
    bg="white",
    anchor="w",
    padx=10,
    pady=10
)

                greeting_label.pack(fill="x")


                # Top Container Frame
                top_frame = tk.Frame(self.content, bg="#f3f3f3")
                top_frame.pack(padx=80, fill="both", expand=True)

                left_column = tk.Frame(top_frame, bg="#f3f3f3")
                left_column.pack(side="left", fill="both", expand=True)


                # Activity Box Frame
                activity_frame = tk.Frame(top_frame, bg="white", bd=1, relief="groove", width=250)
                activity_frame.pack(side="right", fill="y", padx=(20, 0))
                activity_frame.pack_propagate(False)


                # Activity Header with "See All"
                activity_header = tk.Frame(activity_frame, bg="white")
                activity_header.pack(fill="x", pady=(10, 5), padx=10)

                tk.Label(activity_header, text="Activity", font=("Helvetica", 12, "bold"), bg="white").pack(side="left")
                see_all_label = tk.Label(activity_header, text="See All", font=("Helvetica", 10), fg="blue", bg="white", cursor="hand2")
                see_all_label.pack(side="right")
                see_all_label.bind("<Button-1>", lambda e: switch_tab("Profile"))

                                # Activity List
                # clear any old rows (keep the header intact)
                                # Activity List
                # clear old rows (keep the header intact)
                for child in activity_frame.winfo_children()[1:]:
                    child.destroy()

                if not self.activity:
                    tk.Label(activity_frame,
                             text="No recent activity.",
                             font=self.text_font, bg="white")\
                      .pack(pady=20)
                else:
                    for icon, desc, col in self.activity:
                        row = tk.Frame(activity_frame, bg="white")
                        row.pack(fill="x", padx=10, pady=5)
                        # icon (fallback to 🪙 if None)
                        if icon:
                            lbl = tk.Label(row, image=icon, bg="white")
                            lbl.image = icon
                            lbl.pack(side="left")
                        else:
                            tk.Label(row, text="🪙", font=("Helvetica",16), bg="white")\
                              .pack(side="left")
                        # description text
                        tk.Label(row, text=desc, font=("Helvetica",10),
                                 fg=col, bg="white")\
                          .pack(side="left", padx=5)


                

                                # Row to hold balance and action side by side
                balance_action_row = tk.Frame(left_column, bg="#f3f3f3")
                balance_action_row.pack(fill="x", pady=(0, 10))

                # Balance Box (left half)
                balance_frame = tk.Frame(balance_action_row, bg="white", bd=1, relief="groove")
                balance_frame.pack(side="left", expand=True, fill="both", padx=(0, 5))

                if credit_card_icon:
                    card_icon = tk.Label(balance_frame, image=credit_card_icon, bg="white")
                    card_icon.image = credit_card_icon
                    card_icon.grid(row=0, column=0, rowspan=2, padx=10, pady=10)


                tk.Label(balance_frame, text="My Balance", font=self.text_font, fg="gray", bg="white").grid(row=0, column=1, sticky="w")
                self.balance_label = tk.Label(balance_frame, text=f"${self.current_balance:.2f} USD", font=("Helvetica", 18, "bold"), fg="#1c1c1c", bg="white")
                self.balance_label.grid(row=1, column=1, sticky="w")


                tk.Label(balance_frame, text="▲ 9.11% Today", font=("Helvetica", 10), fg="green", bg="white").grid(row=1, column=2, sticky="e", padx=10)
                edit_btn = tk.Button(balance_frame, text="Edit", bg="black", fg="white", font=("Helvetica", 10), relief="flat", command=self.edit_balance)
                edit_btn.grid(row=0, column=2, sticky="e", padx=10, pady=10)

                # Action Buttons Box (right half)
                action_frame = tk.Frame(balance_action_row, bg="white", bd=1, relief="groove")
                action_frame.pack(side="left", expand=True, fill="both", padx=(5, 0))

                def action_button(parent, symbol, text, command):
                    """TODO: Add description."""
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

                # Asset Holdings Box
                # Asset Holdings Box
                asset_frame = tk.Frame(left_column, bg="white", bd=1, relief="groove")
                asset_frame.pack(fill="x", pady=10, padx=10)

                # Configure three equal columns (icon/info, value, amount) + extra for menu button
                for col in range(4):
                    asset_frame.grid_columnconfigure(col, weight=1)

                # Header row
                tk.Label(asset_frame, text="Assets", font=("Helvetica",12,"bold"), bg="white")\
                .grid(row=0, column=0, sticky="w", padx=10, pady=(10,5))
                tk.Label(asset_frame, text="Value (USD)", font=("Helvetica",10,"bold"), bg="white")\
                .grid(row=0, column=1, sticky="w", padx=10, pady=(10,5))
                tk.Label(asset_frame, text="Amount", font=("Helvetica",10,"bold"), bg="white")\
                .grid(row=0, column=2, sticky="w", padx=10, pady=(10,5))
                # empty placeholder for the menu column header (so rows line up underneath)
                tk.Label(asset_frame, text="", bg="white")\
                .grid(row=0, column=3, padx=10, pady=(10,5))

                if not self.holdings:
                    tk.Label(asset_frame, text="You have no assets yet.",
                            font=self.text_font, bg="white")\
                    .grid(row=1, column=0, columnspan=4, pady=20)
                else:
                    for i, (sym, amt) in enumerate(self.holdings.items(), start=1):
                        # lookup price
                        price = next((c['PRICE_USD'] for c in self.cached_coins_data if c['SYMBOL']==sym), 0)
                        total_val = price * amt
                        coin_data = next((c for c in self.cached_coins_data if c['SYMBOL'] == sym), {})
                        # Icon + symbol
                        info_frame = tk.Frame(asset_frame, bg="white")
                        info_frame.grid(row=i, column=0, sticky="w", padx=10, pady=5)
                        icon = self.get_coin_icon(sym, (24,24))
                        if icon:
                            lbl_icon = tk.Label(info_frame, image=icon, bg="white")
                            lbl_icon.image = icon
                            lbl_icon.pack(side="left")
                        else:
                            tk.Label(info_frame, text="🪙", font=("Helvetica",14), bg="white")\
                            .pack(side="left")
                        tk.Label(info_frame, text=f"{sym}", font=("Helvetica",11,"bold"), bg="white")\
                        .pack(side="left", padx=(5,0))

                        # Total USD value
                        tk.Label(asset_frame, text=f"${total_val:,.2f}", font=("Helvetica",11), bg="white")\
                        .grid(row=i, column=1, sticky="w", padx=10)

                        # Amount
                        tk.Label(asset_frame, text=f"{amt:.6f}", font=("Helvetica",11), bg="white")\
                        .grid(row=i, column=2, sticky="w", padx=10)

                        # 3‑dot menu button at the far right
                        more_btn = tk.Button(asset_frame, text="⋯", font=("Helvetica", 14),
                                            bg="white", bd=0, cursor="hand2")
                        more_btn.grid(row=i, column=3, sticky="e", padx=10)




                        def show_context_menu(event, coin=coin_data, symbol=sym):
                            """TODO: Add description."""
                            menu = tk.Menu(self.root, tearoff=0, bg="white", fg="black",
                                        font=("Helvetica", 10))
                            # BUY
                            menu.add_command(
                                label="Buy",
                                command=lambda c=coin: self.init_coin_detail({
                                    "name":   c.get("NAME",""),
                                    "symbol": c.get("SYMBOL",""),
                                    "price":  float(c.get("PRICE_USD",0)),
                                    "change": float(c.get("SPOT_MOVING_24_HOUR_CHANGE_PERCENTAGE_USD",0))
                                })
                            )
                            # SELL (same as Buy screen for now)
                            menu.add_command(
                                label="Sell",
                                command=lambda c=coin: self.init_coin_detail({
                                    "name":   c.get("NAME",""),
                                    "symbol": c.get("SYMBOL",""),
                                    "price":  float(c.get("PRICE_USD",0)),
                                    "change": float(c.get("SPOT_MOVING_24_HOUR_CHANGE_PERCENTAGE_USD",0))
                                })
                            )
                            # SEND (no-op)
                            menu.add_command(label="Send", command=lambda: None)
                            # DELETE
                            menu.add_command(
                                label="Delete",
                                command=lambda s=symbol: (
                                    self.holdings.pop(s, None),
                                    self.save_user_data(),
                                    self.switch_tab("Homepage")
                                )
                            )

                            try:
                                menu.tk_popup(event.x_root, event.y_root)
                            finally:
                                menu.grab_release()

                        more_btn = tk.Button(asset_frame, text="⋯", font=("Helvetica", 14),
                                            bg="white", bd=0, cursor="hand2")
                        more_btn.grid(row=i, column=3, sticky="e", padx=10)
                        more_btn.bind("<Button-1>", show_context_menu)

        

            elif tab_name == "Buy/Sell":
                buy_sell_frame = tk.Frame(self.content, bg="#f4f4f4")
                buy_sell_frame.pack(fill="both", expand=True)

                # 1) CONTROL BAR
                ctrl_frame = tk.Frame(buy_sell_frame, bg="#f4f4f4", pady=5)
                ctrl_frame.pack(fill="x", padx=20)

                self.search_var = tk.StringVar()
                tk.Entry(ctrl_frame, textvariable=self.search_var, width=30).pack(side="left")
                tk.Button(ctrl_frame, text="🔍 Search", command=self.run_search).pack(side="left", padx=5)

                filter_btn = tk.Menubutton(ctrl_frame, text="Filter ▾", relief="raised")
                filter_btn.pack(side="right", padx=5)
                menu = tk.Menu(filter_btn, tearoff=0)
                for attr,label in [
                    ("PRICE_USD","Price"),
                    ("TOTAL_MKT_CAP_USD","Market Cap"),
                    ("SPOT_MOVING_24_HOUR_CHANGE_PERCENTAGE_USD","24h %"),
                ]:
                    sm = tk.Menu(menu, tearoff=0)
                    sm.add_command(label="↑ Low→High",  command=lambda a=attr: self.run_sort(a, True))
                    sm.add_command(label="↓ High→Low", command=lambda a=attr: self.run_sort(a, False))
                    menu.add_cascade(label=label, menu=sm)
                filter_btn.config(menu=menu)

                # 2) TABLE FRAME
                table_frame = tk.Frame(buy_sell_frame, bg="#f4f4f4")
                table_frame.pack(fill="both", expand=True, padx=20, pady=20)

                # Only fetch & cache once
                if not hasattr(self, 'cached_coins_data'):
                    try:
                        response = requests.get(
                            'https://data-api.coindesk.com/asset/v2/metadata',
                            params={
                                "asset_lookup_priority": "SYMBOL",
                                "quote_asset": "USD",
                                "asset_language": "en-US",
                                "assets": "BTC,ETH,SOL,USDT,XRP,BNB,DOGE,ADA,SHIB,TRX,LINK,AVAX",
                                "groups": "ID,PRICE,MKT_CAP,CHANGE,BASIC"
                            },
                            headers={"Content-type": "application/json; charset=UTF-8"}
                        )
                        data = response.json()
                        self.cached_coins_data = list(data['Data'].values())
                    except Exception as e:
                        self.cached_coins_data = []
                        tk.Label(
                            table_frame,
                            text=f"Failed to load data: {e}",
                            font=("Helvetica", 10),
                            bg="#f4f4f4", fg="red"
                        ).grid(row=1, column=0, columnspan=6)
                        return

                    # ← seed display list only on first fetch
                    self.displayed_coins = list(self.cached_coins_data)

                # safety: if displayed_coins for some reason didn't get set
                if not hasattr(self, 'displayed_coins'):
                    self.displayed_coins = list(self.cached_coins_data)

                # TABLE HEADER
                for col in range(6):
                    table_frame.grid_columnconfigure(col, weight=1)
                tk.Label(table_frame, text="Name",       font=("Helvetica",10,"bold"), bg="#f4f4f4").grid(row=0, column=1)
                tk.Label(table_frame, text="Price",      font=("Helvetica",10,"bold"), bg="#f4f4f4").grid(row=0, column=2)
                tk.Label(table_frame, text="Market Cap", font=("Helvetica",10,"bold"), bg="#f4f4f4").grid(row=0, column=3)
                tk.Label(table_frame, text="24h %",      font=("Helvetica",10,"bold"), bg="#f4f4f4").grid(row=0, column=4)

                # DATA ROWS
                # DATA ROWS
                for i, coin in enumerate(self.displayed_coins, start=1):
                    name   = coin.get('NAME','')
                    symbol = coin.get('SYMBOL','')
                    price  = f"${coin.get('PRICE_USD',0):,.2f} USD"
                    mcap   = f"{coin.get('TOTAL_MKT_CAP_USD',0):,.2f}"
                    chg    = float(coin.get('SPOT_MOVING_24_HOUR_CHANGE_PERCENTAGE_USD',0))
                    color  = "green" if chg >= 0 else "red"

                    # — LOAD ICON —
                    icon_path = os.path.join("images", f"{symbol.lower()}.png")
                    icon = None
                    if os.path.exists(icon_path):
                        icon = self.load_image(icon_path, (30, 30))

                    # — ROW FRAME —
                    card = tk.Frame(table_frame, bg="white", bd=0)
                    card.grid(row=i, column=0, columnspan=6, sticky="ew", pady=5, padx=10)
                    for c in range(6):
                        card.grid_columnconfigure(c, weight=1)

                    # — PLACE ICON OR FALLBACK —
                    if icon:
                        icon_lbl = tk.Label(card, image=icon, bg="white")
                        icon_lbl.image = icon
                        icon_lbl.grid(row=0, column=0, padx=10, pady=5, sticky="w")
                    else:
                        tk.Label(card, text="🪙", font=("Helvetica", 12), bg="white")\
                        .grid(row=0, column=0, padx=10, pady=5, sticky="w")

                    # — TEXT COLUMNS —
                    tk.Label(card, text=f"{name} ({symbol})", font=("Helvetica",10), bg="white")\
                    .grid(row=0, column=1, sticky="w", padx=10)
                    tk.Label(card, text=price, font=("Helvetica",10), bg="white")\
                    .grid(row=0, column=2, sticky="w", padx=10)
                    tk.Label(card, text=mcap, font=("Helvetica",10), bg="white")\
                    .grid(row=0, column=3, sticky="w", padx=10)
                    tk.Label(card, text=f"{chg:.2f}%", font=("Helvetica",10), fg=color, bg="white")\
                    .grid(row=0, column=4, sticky="w", padx=10)

                    # — BUY BUTTON —
                    tk.Button(
                        card, text="Buy", bg="#4a4aff", fg="white", font=("Helvetica",9),
                        relief="flat", padx=10,
                        command=lambda c=coin: self.init_coin_detail({
                            "name":   c.get("NAME",""),
                            "symbol": c.get("SYMBOL",""),
                            "price":  float(c.get("PRICE_USD",0)),
                            "change": float(c.get("SPOT_MOVING_24_HOUR_CHANGE_PERCENTAGE_USD",0))
                        })
                    ).grid(row=0, column=5, sticky="e", padx=10)

            elif tab_name == "Leaderboard":
                # header
                tk.Label(self.content,
                            text="🏆 Leaderboard",
                            font=("Helvetica", 16, "bold"),
                            bg="#f3f3f3")\
                    .pack(pady=(10, 5), padx=10, anchor="w")

                # fetch all users
                users = self.load_all_users_data()

                # compute net worths
                networths = []
                for username, data in users.items():
                    bal = data.get("balance", 0.0)
                    holdings = data.get("holdings", {})
                    total_assets = 0.0
                    for sym, amt in holdings.items():
                        price = next(
                            (c["PRICE_USD"] for c in self.cached_coins_data
                                if c["SYMBOL"] == sym),
                            0.0
                        )
                        total_assets += price * amt
                    networths.append((username, bal + total_assets))

                # sort descending by net worth
                networths.sort(key=lambda x: x[1], reverse=True)

                # display rankings
                for rank, (username, nw) in enumerate(networths, start=1):
                    tk.Label(self.content,
                                text=f"{rank}. {username}: ${nw:.2f} USD",
                                font=self.text_font,
                                bg="#f3f3f3")\
                        .pack(anchor="w", padx=20, pady=2)

                # re‑highlight the button
                for name, btn in tab_buttons.items():
                    btn.config(bg=self.highlight_color if name=="Leaderboard"
                                    else self.white_color,
                                fg="white" if name=="Leaderboard"
                                    else self.gray_text_color)


            
            
            
            
            
            
            
            
            
            
            elif tab_name == "Settings":
                users = self.load_all_users_data()

                tk.Label(self.content,
                        text="Settings – All Users",
                        font=("Helvetica", 16, "bold"),
                        bg="#f3f3f3")\
                .pack(pady=(10, 5))





                reset_all_button = tk.Button(self.content, text="Reset All Accounts", command=self.clear_all_user_data)
                reset_all_button.pack(pady=10)


                canvas = tk.Canvas(self.content, bg="#f3f3f3", highlightthickness=0)
                scroll = tk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
                container = tk.Frame(canvas, bg="white")
                container.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )
                canvas.create_window((0,0), window=container, anchor="nw")
                canvas.configure(yscrollcommand=scroll.set)
                canvas.pack(side="left", fill="both", expand=True, padx=10, pady=5)
                scroll.pack(side="right", fill="y")

                for user, data in users.items():              # ← renamed loop var
                    lf = tk.LabelFrame(container,
                                    text=user,              # ← use `user` here
                                    font=self.text_font,
                                    bg="white",
                                    bd=1, relief="groove")
                    lf.pack(fill="x", padx=5, pady=5)

                    fields = {
                        "Username":       data.get("username", ""),
                        "Password":       data.get("password", ""),
                        "Balance (USD)":  f"${data.get('balance', 0):.2f}",
                        "Holdings":       ", ".join(f"{k}:{v}" for k,v in data.get("holdings",{}).items()) or "—",
                        "Activity":       "\n".join(f"- {itm['desc']}" for itm in data.get("activity",[])) or "—"
                    }

                    for i, (label, val) in enumerate(fields.items()):
                        tk.Label(lf, text=label + ":", font=self.text_font, bg="white")\
                        .grid(row=i, column=0, sticky="w", padx=5, pady=2)
                        tk.Label(lf, text=val,    font=self.text_font, bg="white", wraplength=400, justify="left")\
                        .grid(row=i, column=1, sticky="w", padx=5, pady=2)

                # re‑highlight the Settings button
                for name, btn in tab_buttons.items():
                    btn.config(bg=self.highlight_color if name=="Settings" else self.white_color,
                            fg="white" if name=="Settings" else self.gray_text_color)




        self.switch_tab = switch_tab





        tabs = ["Homepage", "Buy/Sell", "Leaderboard", "Profile", "Settings"]
        for tab in tabs:
            btn = tk.Button(sidebar, text=tab, font=self.text_font, bg=self.white_color, fg=self.gray_text_color,
                            relief="flat", padx=20, pady=10, anchor="w",
                            command=lambda name=tab: switch_tab(name))
            btn.pack(fill="x", pady=5, padx=10)
            tab_buttons[tab] = btn

            




        switch_tab("Homepage")


    def init_coin_detail(self, coin):
        """Displays a detailed coin view with buy/sell options and live conversion."""
        # 1) clear the content area
        for w in self.content.winfo_children():
            w.destroy()

        # 2) back button + header (icon, name, price, change)
        back_btn = tk.Button(
            self.content, text="← Back", font=self.text_font,
            bg=self.white_color, relief="flat",
            command=self.switch_to_buy_sell
        )
        back_btn.pack(side="left", padx=10, pady=10)

        header = tk.Frame(self.content, bg=self.white_color)
        header.pack(fill="x", pady=10)

        # load the coin icon
        icon_path = os.path.join("images", f"{coin['symbol'].lower()}.png")
        icon_img = self.load_image(icon_path, (30,30)) if os.path.exists(icon_path) else None
        if icon_img:
            lbl = tk.Label(header, image=icon_img, bg=self.white_color)
            lbl.image = icon_img
            lbl.pack(side="left", padx=(10,5))
        else:
            tk.Label(header, text="🪙", font=("Helvetica",16), bg=self.white_color)\
            .pack(side="left", padx=(10,5))

        tk.Label(header, text=coin["name"], font=self.title_font, bg=self.white_color)\
        .pack(side="left")
        tk.Label(header, text=f"({coin['symbol']})", font=self.text_font,
                fg=self.gray_text_color, bg=self.white_color)\
        .pack(side="left", padx=(5,0))
        tk.Label(header, text=f"${coin['price']:.2f} USD", font=self.title_font,
                bg=self.white_color).pack(side="right", padx=10)
        col = "green" if coin["change"]>=0 else "red"
        tk.Label(header, text=f"{coin['change']:+.2f}%", font=self.text_font,
                fg=col, bg=self.white_color).pack(side="right")

        # 3) Buy/Sell toggle
        state = tk.StringVar(value="Buy")
        switch_frame = tk.Frame(self.content, bg=self.white_color)
        switch_frame.pack(pady=(10,0))
        def on_toggle(x):
            """TODO: Add description."""
            state.set(x); render_form()
        buy_btn = tk.Button(switch_frame, text="Buy",
                            command=lambda:on_toggle("Buy"), width=10)
        sell_btn= tk.Button(switch_frame, text="Sell",
                            command=lambda:on_toggle("Sell"), width=10)
        buy_btn.grid(row=0, column=0); sell_btn.grid(row=0, column=1)
        def style(*_):
            """TODO: Add description."""
            if state.get()=="Buy":
                buy_btn.config(bg=self.highlight_color, fg="white")
                sell_btn.config(bg=self.white_color, fg=self.gray_text_color)
            else:
                sell_btn.config(bg=self.highlight_color, fg="white")
                buy_btn.config(bg=self.white_color, fg=self.gray_text_color)
        state.trace_add("write", style)

        # 4) form area
        form_frame = tk.Frame(self.content, bg=self.white_color, bd=1, relief="solid")
        form_frame.pack(fill="x", padx=20, pady=10)

        # USD icon
        usd_path = os.path.join('images', 'United-states_flag_icon_round.svg.png')
        usd_img = self.load_image(usd_path, (24,24)) if os.path.exists(usd_path) else None

        def render_form():
            """TODO: Add description."""
            # clear form_frame
            for w in form_frame.winfo_children():
                w.destroy()
            style()

            price = coin["price"]
            sym   = coin["symbol"]

            # --- You Pay row ---
            r1 = tk.Frame(form_frame, bg=self.white_color)
            r1.pack(fill="x", pady=5, padx=10)
            tk.Label(r1, text="You Pay", font=self.text_font, bg=self.white_color)\
            .pack(side="left")
            pay_e = tk.Entry(r1, font=self.text_font, width=12, justify="right")
            pay_e.pack(side="right", padx=(0,5))
            if state.get()=="Buy":
                if usd_img:
                    l = tk.Label(r1, image=usd_img, bg=self.white_color)
                    l.image=usd_img; l.pack(side="right")
                else:
                    tk.Label(r1, text="USD", font=self.text_font, bg=self.white_color)\
                    .pack(side="right", padx=5)
            else:
                if icon_img:
                    l = tk.Label(r1, image=icon_img, bg=self.white_color)
                    l.image=icon_img; l.pack(side="right")
                else:
                    tk.Label(r1, text=sym, font=self.text_font, bg=self.white_color)\
                    .pack(side="right", padx=5)

            # --- You Get row ---
            tk.Frame(form_frame, height=1, bg=self.gray_text_color)\
            .pack(fill="x", padx=5, pady=2)
            r2 = tk.Frame(form_frame, bg=self.white_color)
            r2.pack(fill="x", pady=5, padx=10)
            tk.Label(r2, text="You Get", font=self.text_font, bg=self.white_color)\
            .pack(side="left")
            get_e = tk.Entry(r2, font=self.text_font, width=12, justify="right")
            get_e.pack(side="right", padx=(0,5))
            if state.get()=="Buy":
                if icon_img:
                    l = tk.Label(r2, image=icon_img, bg=self.white_color)
                    l.image=icon_img; l.pack(side="right")
                else:
                    tk.Label(r2, text=sym, font=self.text_font, bg=self.white_color)\
                    .pack(side="right", padx=5)
            else:
                if usd_img:
                    l = tk.Label(r2, image=usd_img, bg=self.white_color)
                    l.image=usd_img; l.pack(side="right")
                else:
                    tk.Label(r2, text="USD", font=self.text_font, bg=self.white_color)\
                    .pack(side="right", padx=5)

            # live conversion
            busy=False
            def on_pay(_):
                """TODO: Add description."""
                nonlocal busy
                if busy: return
                busy = True
                try:
                    v = float(pay_e.get())
                    if state.get() == "Buy":
                        # paying USD → getting coin
                        qty = v / price
                        get_e.delete(0, tk.END)
                        get_e.insert(0, f"{qty:.6f}")
                    else:
                        # paying coin → getting USD
                        usd = v * price
                        get_e.delete(0, tk.END)
                        get_e.insert(0, f"{usd:.2f}")
                except ValueError:
                    pass
                busy = False

            def on_get(_):
                """TODO: Add description."""
                nonlocal busy
                if busy: return
                busy = True
                try:
                    v = float(get_e.get())
                    if state.get() == "Buy":
                        # entering coin amount → compute USD needed
                        usd = v * price
                        pay_e.delete(0, tk.END)
                        pay_e.insert(0, f"{usd:.2f}")
                    else:
                        # entering USD amount → compute coins to sell
                        qty = v / price
                        pay_e.delete(0, tk.END)
                        pay_e.insert(0, f"{qty:.6f}")
                except ValueError:
                    pass
                busy = False

            pay_e.bind("<KeyRelease>", on_pay)
            get_e.bind("<KeyRelease>", on_get)

            # action button
            act=state.get()
            tk.Button(
    form_frame,
    text=act,
    bg=self.highlight_color,
    fg="white",
    font=self.text_font,
    width=20,
    # for Buy: (pay_e → USD amount, get_e → coin qty)
    # for Sell: swap them so pay_amt is USD from get_e, qty is coins from pay_e
    command=lambda: self.execute_trade(
        coin,
        act,
        float(pay_e.get()) if act == "Buy" else float(get_e.get()),
        float(get_e.get()) if act == "Buy" else float(pay_e.get())
    )
).pack(pady=(10, 10))


        render_form()






    def execute_trade(self, coin, action, pay_amt, qty):
        """Processes a simulated Buy or Sell transaction and updates user data."""
        sym = coin["symbol"]

        if action == "Buy":
            if pay_amt > self.current_balance:
                return messagebox.showerror("Error", "Insufficient USD balance.")
            self.current_balance -= pay_amt
            self.holdings[sym] = self.holdings.get(sym, 0) + qty
            result_msg = f"Bought {qty:.6f} {sym} for ${pay_amt:.2f} USD"
        else:
            owned = self.holdings.get(sym, 0)
            if qty > owned:
                return messagebox.showerror("Error", f"Not enough {sym} to sell.")
            self.holdings[sym] -= qty
            self.current_balance += pay_amt
            result_msg = f"Sold {qty:.6f} {sym} for ${pay_amt:.2f} USD"

                # record activity
                # record activity immediately and refresh
        color = "red" if action == "Buy" else "green"
        icon  = self.get_coin_icon(sym, (16,16))
        msg   = result_msg if len(result_msg) <= 30 else result_msg[:27] + "…"
        self.activity.insert(0, (icon, msg, color))
        if len(self.activity) > 5:
            self.activity.pop()
        self.switch_tab("Homepage")
        self.save_user_data()


        # rebuild dashboard & show balance
        self.switch_to_buy_sell()
        self.update_balance_display()



        # 1) rebuild dashboard (this recreates balance_label)
        self.switch_to_buy_sell()

        # 2) update the new balance_label
        self.update_balance_display()

        # 3) show confirmation
        messagebox.showinfo("Success", result_msg)





    def switch_to_buy_sell(self):
        """Switches view back to the Buy/Sell tab on the dashboard."""
        # rebuild your dashboard in Buy/Sell mode
        self.init_dashboard(self.current_username)
        # then immediately switch to that tab:
        for widget in self.root.winfo_children():
            # find and click the Buy/Sell sidebar button
            if isinstance(widget, tk.Frame):
                for btn in widget.winfo_children():
                    if getattr(btn, "cget", lambda *a: "")("text") == "Buy/Sell":
                        btn.invoke()
                        return
                    

    def run_search(self):
        """Linear search on NAME or SYMBOL containing the query."""
        q = self.search_var.get().strip().lower()
        if not q:
            self.displayed_coins = list(self.cached_coins_data)
        else:
            self.displayed_coins = [
                c for c in self.cached_coins_data
                if q in c.get("NAME","").lower() or q in c.get("SYMBOL","").lower()
            ]
        self.switch_tab("Buy/Sell")

    def run_sort(self, attr, ascending=True):
        """Quick‑sort self.displayed_coins by numeric attribute."""
        def quick_sort(arr):
            """TODO: Add description."""
            if len(arr) <= 1:
                return arr
            pivot = arr[len(arr)//2]
            pv = float(pivot.get(attr,0) or 0)
            left = [x for x in arr if float(x.get(attr,0) or 0) < pv]
            mid  = [x for x in arr if float(x.get(attr,0) or 0) == pv]
            right= [x for x in arr if float(x.get(attr,0) or 0) > pv]
            return quick_sort(left) + mid + quick_sort(right)

        sorted_list = quick_sort(self.displayed_coins)
        if not ascending:
            sorted_list.reverse()
        self.displayed_coins = sorted_list
        self.switch_tab("Buy/Sell")




if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoSimApp(root)
    root.mainloop()
