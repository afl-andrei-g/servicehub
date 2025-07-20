# ServiceHub

**ServiceHub** is a digital platform built for auto repair shops, helping streamline operations such as appointment scheduling, repair tracking, customer management, and reporting. It's the modern solution for garages and workshops looking to work smarter, not harder.
> **Auto repair, reinvented.**  
> Track, manage, and optimize your workshop.

---

## 🚘 Key Features

- 📅 Online booking for customers
- 🛠️ Service tracking with full vehicle history
- 🧾 Create and manage estimates
- 👥 Customer and vehicle management
- 📊 Dashboard with analytics and reporting
- 🔔 Automated notifications (email)
- 🔐 Role-based access (for both companies and clients)

---

## 🛠 Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript, jQuery
- **Backend**: Django (Python3)
- **Database**: MariaDB (MySQL fork)
- **Deployment**: Gunicorn w/ Nginx

---

## ⚙️ Local Installation

1. Clone the repository:
```bash
git clone https://github.com/afl-andrei-g/servicehub.git
cd servicehub
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Create a .env file in the root of the project
```bash
SECRET_KEY='SECRET_KEY'
APP_URL='YOUR_APP_URL'
EMAIL_HOST='SMTP_HOST'
EMAIL_HOST_USER = 'SMTP_USER'
EMAIL_HOST_PASSWORD = 'SMTP_PW'

DB_USER='SMTP_USER'
DB_PW='SMTP_PW'
DB_HOST='localhost'
```

Make sure you fill all the needed information, including upload of the database.

3. Run the app:
```bash
python3 manage.py runserver
```

## 🤝 Contributing
Contributions are welcome! If you’d like to suggest improvements or fixes, feel free to open an issue or submit a pull request.
