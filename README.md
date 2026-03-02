# 🔐 NumINTEL-X

> Official Intelligence Bot of HackingHubk ⚡  
> Telegram-Based Telecom Intelligence & Metadata System

---

## 🚀 Overview

NumINTEL-X is a Telegram intelligence bot built using Python.  
It implements a structured telecom metadata lookup system combined with a secure credit-based access architecture.

The system demonstrates controlled user access, referral incentives, and secure configuration management.

---

## ✨ Features

- 🔎 Number Lookup System  
- 💳 Credit-Based Usage Model  
- 🎁 Referral Reward Mechanism  
- 📢 Channel Membership Enforcement  
- 🔐 Secure Environment Variable Handling  
- 💾 Persistent User Data Storage  
- ⚡ Rate Limiting Protection  

---

## 🧠 System Architecture

```
User → Telegram Bot → Processing Engine → Data Layer
```

### Core Flow

1. User initiates interaction via `/start`
2. Bot verifies channel membership
3. Credits are assigned
4. Each lookup deducts credits
5. Referral system rewards both users
6. User data is stored persistently

---

## 🛠 Tech Stack

- Python 3  
- python-telegram-bot  
- python-dotenv  
- JSON-based storage  
- Git & GitHub  

---

## 📂 Project Structure

```
NumINTELBot/
│
├── NumINTELBot.py
├── README.md
├── requirements.txt
├── .gitignore
├── .env        (not uploaded)
└── data.json   (not uploaded)
```

---

## ⚙ Installation Guide

### 1️⃣ Clone Repository

```bash
git clone https://github.com/frharsh/NumINTEL-X.git
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Create `.env` File

Create a file named `.env` inside the project folder:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

### 4️⃣ Run The Bot

```bash
python NumINTELBot.py
```

---

## 🔐 Security Practices

- Bot token stored using environment variables  
- `.env` excluded via `.gitignore`  
- No secrets hardcoded in source  
- Controlled credit-based execution flow  
- Channel membership validation enforced  

---

## 👨‍💻 Author

**Created by Frharsh**
