# MoodBlume — Installation Guide

How to set up and run **MoodBlume** on a different computer. Instructions are provided for both **macOS** and **Windows**.

MoodBlume is a Flask (Python) web application backed by a local MySQL database.

---

## Prerequisites

Install these before you begin:

| Tool | Notes |
|------|-------|
| **Python 3.11+** | Developed and tested on Python 3.13. Download from [python.org](https://www.python.org/downloads/). On Windows, tick **"Add Python to PATH"** during install. |
| **MySQL Community Server 8.x** | Download from [dev.mysql.com](https://dev.mysql.com/downloads/mysql/). Remember the **root password** you set during installation. |
| **The project files** | Either the submitted `.zip` (unzipped) or `git clone`. |

> MySQL Workbench (optional) gives you a graphical way to create the database in Step 3.

---

## 1. Get the project

If you have the zip, unzip it and open a terminal **inside** the project folder (the one containing `app.py`).

Or clone it:

```bash
git clone https://github.com/introshia/MoodBlume.git
cd MoodBlume
```

---

## 2. Create a virtual environment and install dependencies

This keeps the project's Python packages isolated from the rest of your system.

### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Windows (Command Prompt)
```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

> When the virtual environment is active, your prompt shows `(venv)`. Re-run the activate command any time you open a new terminal.

---

## 3. Set up the MySQL database

The app expects a database named `moodblume_db` with five tables. The app does **not** create these automatically, so you must create them once.

**Open the MySQL prompt:**

- **macOS:** `mysql -u root -p`
- **Windows:** open **"MySQL 8.x Command Line Client"** from the Start Menu, or run `mysql -u root -p` if MySQL is on your PATH.

Enter your MySQL root password when prompted, then paste the entire block below:

```sql
CREATE DATABASE IF NOT EXISTS moodblume_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE moodblume_db;

CREATE TABLE IF NOT EXISTS users (
  id            INT NOT NULL AUTO_INCREMENT,
  username      VARCHAR(100) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at    TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  joined_at     TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  email         VARCHAR(255) NOT NULL,
  onboarded     TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY username (username),
  UNIQUE KEY email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS collections (
  id          INT NOT NULL AUTO_INCREMENT,
  user_id     INT DEFAULT NULL,
  name        VARCHAR(100) NOT NULL,
  cover_color VARCHAR(20) DEFAULT '#C8D898',
  art_style   VARCHAR(50) DEFAULT 'linen',
  created_at  TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  paper_type  VARCHAR(20) DEFAULT 'lined',
  page_type   VARCHAR(20) DEFAULT 'endless',
  PRIMARY KEY (id),
  KEY user_id (user_id),
  CONSTRAINT collections_ibfk_1 FOREIGN KEY (user_id)
    REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS journal_entries (
  id            INT NOT NULL AUTO_INCREMENT,
  content       TEXT NOT NULL,
  mood_score    INT NOT NULL,
  entry_date    TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  theme         VARCHAR(50) DEFAULT 'General',
  mood_tag      VARCHAR(50) DEFAULT NULL,
  user_id       INT DEFAULT NULL,
  collection_id INT DEFAULT NULL,
  PRIMARY KEY (id),
  KEY fk_collection (collection_id),
  CONSTRAINT fk_collection FOREIGN KEY (collection_id)
    REFERENCES collections (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS user_media (
  id         INT NOT NULL AUTO_INCREMENT,
  user_id    INT DEFAULT NULL,
  filename   VARCHAR(255) DEFAULT NULL,
  mimetype   VARCHAR(100) DEFAULT NULL,
  media_data LONGBLOB,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY user_id (user_id),
  CONSTRAINT user_media_ibfk_1 FOREIGN KEY (user_id)
    REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS quotes (
  id       INT NOT NULL AUTO_INCREMENT,
  category VARCHAR(50) DEFAULT NULL,
  text     TEXT NOT NULL,
  author   VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

Type `exit;` to leave the MySQL prompt.

> The `quotes` table is optional reflection content — the app runs fine with it empty.

---

## 4. Configure environment variables (`.env`)

The app reads your database password from a `.env` file in the project root (this file is intentionally **not** included in the submission for security).

Create a file named `.env` in the project folder with this line, replacing the value with **your own MySQL root password**:

```
DB_PASSWORD=your_mysql_root_password
```

Quick way to create it:

- **macOS:** `echo "DB_PASSWORD=your_mysql_root_password" > .env`
- **Windows (PowerShell):** `"DB_PASSWORD=your_mysql_root_password" | Out-File -Encoding ascii .env`

> If your MySQL uses a username other than `root`, also add `MYSQLUSER=your_username` on a new line. Defaults: host `localhost`, port `3306`, user `root`, database `moodblume_db`.

---

## 5. Run the application

With the virtual environment active (Step 2):

```bash
python app.py
```

You should see Flask start up. Open a browser and go to:

```
http://127.0.0.1:5001
```

---

## 6. First use

The database starts empty, so:

1. Click **Register** and create an account.
2. Complete the welcome screen.
3. Start journaling — entries are analyzed by the VADER sentiment engine and saved to your account.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` (e.g. flask not found) | The virtual environment isn't active. Re-run the activate command from Step 2, then `pip install -r requirements.txt`. |
| `Access denied for user 'root'@'localhost'` | The password in `.env` doesn't match your MySQL root password. Update `.env`. |
| `Unknown database 'moodblume_db'` | The database wasn't created. Repeat Step 3. |
| `Table ... doesn't exist` | The schema wasn't run. Repeat the `CREATE TABLE` block in Step 3. |
| Port 5001 already in use | Close whatever is using it, or edit the last line of `app.py` to use a different port (e.g. `port=5002`). |
| Page won't load on macOS at port 5000 | macOS AirPlay uses port 5000 — this app already uses 5001, so use `http://127.0.0.1:5001`. |
| `'python' is not recognized` (Windows) | Python wasn't added to PATH. Reinstall Python and tick "Add Python to PATH", or use `py` instead of `python`. |
