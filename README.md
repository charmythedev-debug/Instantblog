# Instantblog

Instantblog is a **Flask-based blogging platform** built as part of the *100 Days of Python* challenge. It combines Flask, SQLAlchemy, Bootstrap, CKEditor, and Gravatar to deliver a simple but feature-rich blog application where users can register, log in, create posts, and comment.

---

## ✨ Features

- **User Authentication**  
  Register, log in, and log out with secure password hashing.

- **Blog Posts**  
  Create, edit, and delete posts. Each post includes a title, subtitle, body, image URL, and date.

- **Comments**  
  Logged-in users can comment on posts. Comments display with Gravatar profile images.

- **Admin & Author Controls**  
  Only admins or post authors can edit/delete their posts.

- **Rich Text Editing**  
  Integrated CKEditor for formatting blog content.

- **Responsive UI**  
  Styled with Bootstrap 5 for a clean, mobile-friendly interface.

---

## 🛠 Tech Stack

| Component        | Technology |
|------------------|------------|
| Backend          | Flask (Python) |
| Database         | SQLite (dev) / PostgreSQL (production) |
| ORM              | SQLAlchemy |
| Forms            | Flask-WTF |
| Styling          | Bootstrap 5 |
| Rich Text Editor | Flask-CKEditor |
| Avatars          | Flask-Gravatar |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- pip (Python package manager)
- PostgreSQL (for production deployment)

### Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/charmythedev-debug/Instantblog.git
   cd Instantblog
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Mac/Linux
   .venv\Scripts\activate      # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables:
   ```bash
   export FLASK_KEY="your_secret_key"
   export SQLALCHEMY_DATABASE_URI="sqlite:///posts.db"   # or your Postgres URI
   ```

5. Run the app:
   ```bash
   flask run
   ```

---

## 📂 Project Structure

```
Instantblog/
│
├── main.py              # Flask app entry point
├── forms.py             # WTForms classes
├── templates/           # Jinja2 HTML templates
├── static/              # CSS, JS, images
├── requirements.txt     # Python dependencies
└── .gitignore           # Git ignore rules
```

---

## 🌐 Deployment

- Designed to run on **Render** with PostgreSQL.  
- Ensure you set `SQLALCHEMY_DATABASE_URI` in Render’s Environment tab to your Postgres connection string.  
- Use `db.create_all()` or Flask-Migrate to initialize tables.

---

## 📸 Screenshots (optional)

Add screenshots of your blog homepage, post page, and comment section here for better presentation.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

---

## 📜 License

This project is open source under the MIT License.

---
