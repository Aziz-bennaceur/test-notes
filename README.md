# 💌 Girlfriend Grievance Portal

A fun grievance portal built using Flask, Python, and SQLite for managing grievances between users. The portal allows users to submit grievances, while administrators can respond to them, track their resolution, and send email notifications.

---

## 📄 Clone This Repo Into Your Own GitHub (For Beginners)

Want to customize or privately host your own version of this project? Here’s how you can copy it to your GitHub:

1. **Visit the Original Repo**: Sign in to Github and navigate to the original repo here:  
   `https://github.com/ishan-nerlekar/girlfriend-grievance-portal`
2. **Click “Fork”** (top-right corner):  
   This will create a copy of the project in your own GitHub account.
3. **(Optional) Rename the Repository**:  
   After forking, go to the "Settings" tab of your new repo and change the name if you like.
4. You now have your own private/public version of the code to deploy and modify!

---

## 🚀 Quick Deployment (Recommended)

**No coding needed! Just follow these steps:**

1. Go to [https://railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub Repo"**
3. Link your GitHub and choose this repository
4. In the **Environment Variables** section, add the following:

```env
MAIL_SERVER=smtp.your-provider.com
MAIL_PORT=587
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
EMAIL_DEFAULT_SENDER=your-sender-address@example.com
GRIEVANCE_NOTIFICATION_EMAIL=azizbennacer9@gmail.com
EMAIL_USER_RECEIVER=your.partner.email@gmail.com
USER_NAME=girlfriend
USER_PASSWORD=user123
ADMIN_NAME=boyfriend
ADMIN_PASSWORD=admin123
PORTAL_URL=https://your-railway-url.up.railway.app
```

The SMTP account is used only to send mail; new grievance notifications go to `GRIEVANCE_NOTIFICATION_EMAIL` (defaults to `azizbennacer9@gmail.com`).

5. Done! 🚀 Your private grievance portal is live and ready!

---

## 🖼️ How to Add Images

Want to personalize the portal by adding your own images (like custom banners or cute icons)? It’s easy!

1. Go to the project folder.
2. Open the `static/images/` directory. This is where all your image files are stored.
3. Copy and paste your image file into that folder.
4. Replace `home_image.webp` with the image of your choice, and so on for all the images. Do not rename the images, just replace them.

That's it! The image will now be displayed on the page.

---

## 🌐 Features

- User authentication for both user and administrator.
- Submit grievances with a title, description, mood, and priority.
- View grievances and their resolution status.
- Admin dashboard to manage grievances and send responses.
- Email notifications to both admins and users regarding grievances and responses.

## 🛠️ Technologies Used

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS (Bootstrap for responsiveness)
- **Email Service:** Gmail SMTP
- **Environment Variables:** `.env` for sensitive data
- **Deployment**: Railway

## 💻 Want to Run Locally? (Optional for Devs)

### Prerequisites

- Python 3.x
- pip (Python package manager)

### Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/girlfriend-grievance-portal.git
   cd girlfriend-grievance-portal
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Linux/Mac
   .\venv\Scripts\activate   # For Windows
   ```

3. **Install required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Edit the `.env` file in the root of the project and add the following:

    ```env
   # SMTP server settings for your chosen mail provider
   MAIL_SERVER=smtp.your-provider.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USE_SSL=false

   # SMTP credentials (legacy EMAIL_ADMIN / EMAIL_PASS names are also supported)
   SMTP_USERNAME=your-smtp-username
   SMTP_PASSWORD=your-smtp-password

   # Sender address and recipient of new grievance notifications
   EMAIL_DEFAULT_SENDER=your-sender-address@example.com
   GRIEVANCE_NOTIFICATION_EMAIL=azizbennacer9@gmail.com

   # Recipient email address for replies to the person submitting grievances
    EMAIL_USER_RECEIVER=user.email@example.com

    # Username and password for user (grievance submitter)
    USER_NAME=girlfriend
    USER_PASSWORD=user123

    # Username and password for admin (responder)
    ADMIN_NAME=boyfriend
    ADMIN_PASSWORD=admin123

    # Your hosted app URL (used in email templates)
    PORTAL_URL=http://your-grievance-portal-url
    ```
   - Set the SMTP values for your chosen provider. They do not change the grievance notification recipient.
   - Replace `girlfriend` and `boyfriend` with user and admin display names respectively, as desired. Similarly with their corresponding passwords.
   - New grievance notifications go to `GRIEVANCE_NOTIFICATION_EMAIL`; it defaults to `azizbennacer9@gmail.com`.

5. **Initialize the database:**

   ```bash
   python
   >>> from app import init_db
   >>> init_db()
   ```

   This will create the necessary SQLite database for storing grievances.

6. **Run the application:**

   ```bash
   flask run
   ```

   The portal should now be running at `http://localhost:5000`.

## Usage

1. **Login:**
   - Regular users can log in with the `USER_NAME` and `USER_PASSWORD`.
   - Administrators can log in with the `ADMIN_NAME` and `ADMIN_PASSWORD`.

2. **Submit Grievance:**
   - After logging in, regular users can submit a note with a title, description, mood, importance, and an update such as getting better, getting worse, or already resolved.

3. **Admin Dashboard:**
   - Administrators can view all grievances, respond to them, and mark them as resolved.

4. **Email Notifications:**
   - New-note notifications go to `GRIEVANCE_NOTIFICATION_EMAIL`; SMTP credentials are configured separately.
   - Replies are emailed to `EMAIL_USER_RECEIVER`. Notes are saved in SQLite even when an email cannot be sent.

## 📁 Project Structure

```
girlfriend-grievance-portal/
│
├── app.py                # Main application logic
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
├── .gitignore            # Git ignore file
├── templates/            # HTML templates
│   ├── home.html
│   ├── login.html
│   ├── submit.html
│   ├── thankyou.html
│   ├── my_grievances.html
│   └── dashboard.html
└── venv/                 # Virtual environment
```

### Notes:

- Make sure to set up your environment variables correctly in the `.env` file.
- If you're using Gmail for sending emails, ensure you use an app password (not your Google account password) if two-factor authentication (2FA) is enabled.

For more information, visit the official [Flask Documentation](https://flask.palletsprojects.com/).
