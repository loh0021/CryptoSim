CryptoSimApp – Cryptocurrency Trading Simulator
===============================================

This is a desktop GUI application built with Python and Tkinter to simulate cryptocurrency trading.

📁 Project Structure
---------------------
CryptoSimApp/
├── main.py         # Main application script with all logic and GUI
├── images/                  # Folder containing all required icons and images
│   ├── btc.png
│   ├── eth.png
│   ├── ...
├── user_data/               # Stores user data in JSON format (auto-created if missing)
├── requirements.txt         # List of Python packages to install
├── README.txt               # This file

📦 How to Run
--------------
1. Make sure you have Python 3 installed.
2. Open a terminal in the project directory.
3. Install required libraries:
   pip install -r requirements.txt
4. Run the app:
   python main_portable.py

🖼️ Images Note
---------------
Ensure the `images/` folder contains all referenced image files:
- Coin icons (btc.png, eth.png, etc.)
- Background and interface icons (e.g., fingerprint, credit card, user icon)

📝 User Data
-------------
User accounts, balances, and activity logs are stored in the `user_data/` folder.
This is created automatically on first run.

🔒 Dependencies
----------------
See `requirements.txt` for a full list. Key libraries:
- tkinter (built-in with Python)
- Pillow (for image loading/resizing)
- requests (for fetching live crypto data)

Created for educational/demo purposes.
