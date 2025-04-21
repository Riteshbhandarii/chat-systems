# UmbraChat – Real-Time Messaging App with Django Channels 💬

UmbraChat is a real-time messaging web app built using Django Channels]n, WebSockets, Redis, and PostgreSQL. It supports private and group chats, read receipts, friend requests, user account control, and a clean dark mode interface.

Built as a Big Data Engineering course project, UmbraChat focuses on scalable infrastructure, privacy-first design, and smooth real-time interactions. Whether you're chatting one-on-one or in groups, messages are delivered instantly — even at night 🌒.

## 🔑 Features
- One-on-one chat with real-time delivery and read receipts
- Group chat with add/remove members
- WebSocket-based communication via Django Channels
- Friend requests (mutual acceptance required)
- User registration, login, and secure authentication
- Delete your account or download your data as JSON
- GDPR-style privacy consent during sign-up
- Personalized UI with dark mode and starry background
## 🖼️ Screenshot Gallery

<div align="center" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin: 2rem 0;">

### 🔐 Authentication
<img width="1088" alt="01-login-destop" src="https://github.com/user-attachments/assets/04720aa1-7721-4650-815c-2b5b211c5908" />

✓ JWT authentication<br>
✓ Password recovery<br>
✓ Clean minimalist design</p>

<img src="./screenshots/auth/02-register-desktop.png" width="90%" alt="Registration Screen">
<p><strong>GDPR Signup</strong><br>
✓ Privacy policy consent<br>
✓ Optional email collection<br>
✓ Secure password validation</p>

### 💬 Messaging
<img src="./screenshots/chat/03-group-chat-destop.png" width="90%" alt="Group Chat">
<p><strong>Group Collaboration</strong><br>
✓ Real-time messaging<br>
✓ Member identification<br>
✓ Message timestamps</p>

<img src="./screenshots/chat/04-private-chat-destop.png" width="90%" alt="Private Chat">
<p><strong>Secure Conversations</strong><br>
✓ Read receipts (✓✓)<br>
✓ Online status indicators<br>
✓ Message history</p>

### ⚙️ Interface
<img src="./screenshots/ui/05-dashboard-destop.png" width="90%" alt="Dashboard">
<p><strong>User Dashboard</strong><br>
✓ Contact management<br>
✓ Notification center<br>
✓ Welcome messaging</p>

</div>

<sub>All screenshots captured in Chrome 120+ at 1920x1080 resolution</sub>

*All screenshots captured in Chrome 120+ at 1920x1080 resolution*
## ⚙️ Technologies Used
- Python, Django 5, Django REST Framework
- Django Channels, Redis, Daphne
- PostgreSQL for scalable data storage
- JavaScript, CSS, HTML
- JWT (SimpleJWT) for secure token-based auth
- Docker for containerized deployment

## 🔐 Privacy & GDPR Compliance
UmbraChat was designed with privacy in mind, following principles aligned with the General Data Protection Regulation (GDPR):
- 🔒 **Secure Password Handling** – Uses Django’s built-in hashing, never stores plain text
- 👤 **Minimal Data Collection** – Stores only what's necessary for communication
- 🧾 **User Control** – Delete your messages or entire account anytime
- ✅ **Consent Required** – Users must accept the Privacy Policy to register
- 📜 **Clear Policy Access** – Transparent documentation of how data is stored and used
- 📁 **Downloadable User Data** – Export your personal info as JSON at any time

## 📚 About This Project
UmbraChat was developed by a second-year Data Engineering student as part of a hands-on course project. The focus was on building a system that combines real-time data processing, backend scalability, and good privacy practices — all while looking good in dark mode.

## 🌐 Live Demo
Experience UmbraChat live: [https://umbrachat-production.up.railway.app](https://umbrachat.up.railway.app)

## 🛠️ Local Deployment and Usage

```mermaid
flowchart TD
    A[Client] -->|WebSocket| B["Daphne ASGI Server<br/>(localhost:8001)"]
    A -->|HTTPS API| C["Django REST<br/>(localhost:8000)"]
    B -->|HTTP/WS| D[Django Channels]
    C -->|JWT Auth| E[Authentication Service]
    D -->|Redis Pub/Sub| F["Redis<br/>(localhost:6379)"]
    D -->|Database Queries| G["PostgreSQL<br/>(localhost:5432)"]
```

This section explains how to deploy and run UmbraChat locally for development or testing, ensuring the full source code is usable.

### Prerequisites
- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Git
- (Optional) Virtual environment tool (`venv`)
## 🌐 System Architecture


### Code Modifications
To support local deployment, ensure your code is configured as follows:
- **`requirements.txt`**: Includes `django`, `channels`, `djangorestframework`, `redis`, `psycopg2-binary`, `daphne`, and `python-dotenv`. If `python-dotenv` is missing, add it:
  ```bash
  echo "python-dotenv" >> requirements.txt
  ```
- **`settings.py`**: Load environment variables for local and Railway compatibility. Use one of these approaches:
  - **Option 1 (Recommended)**: Parse `DATABASE_URL` and `REDIS_URL` for flexibility:
    ```python
    from pathlib import Path
    import os
    from dotenv import load_dotenv
    load_dotenv()
    SECRET_KEY = os.getenv('SECRET_KEY')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DATABASE_URL').split('/')[-1],
            'USER': os.getenv('DATABASE_URL').split(':')[1].split('//')[1],
            'PASSWORD': os.getenv('DATABASE_URL').split(':')[2].split('@')[0],
            'HOST': os.getenv('DATABASE_URL').split('@')[1].split(':')[0],
            'PORT': os.getenv('DATABASE_URL').split(':')[-1].split('/')[0],
        }
    }
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [(os.getenv('REDIS_URL').split('//')[1])],
            },
        },
    }
    ```
  - **Option 2 (Simpler, Local-Only)**: Use explicit local settings:
    ```python
    from pathlib import Path
    import os
    from dotenv import load_dotenv
    load_dotenv()
    SECRET_KEY = os.getenv('SECRET_KEY')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'umbrachat_db',
            'USER': 'umbrachat',
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [('localhost', 6379)],
            },
        },
    }
    ```
- **`asgi.py`**: Ensure it’s set up for Django Channels (should be correct if deployed on Railway).
- **Commit Changes**: After modifying `settings.py` or `requirements.txt`, push to GitHub:
  ```bash
  git add .
  git commit -m "Update for local deployment"
  git push origin main
  ```

### Installation
1. **Install System Dependencies** (on Ubuntu-based systems):
   - Update package lists and install Git:
     ```bash
     sudo apt update
     sudo apt install git
     ```
2. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/umbrachat.git
   cd umbrachat
   ```
3. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Set Up PostgreSQL**:
   - Install PostgreSQL:
     ```bash
     sudo apt install postgresql postgresql-contrib
     sudo systemctl start postgresql
     sudo systemctl enable postgresql
     ```
   - Create a database and user (replace `your-password` with a secure password):
     ```bash
     sudo -u postgres psql -c "CREATE DATABASE umbrachat_db;"
     sudo -u postgres psql -c "CREATE USER umbrachat WITH PASSWORD 'your-password';"
     sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE umbrachat_db TO umbrachat;"
     ```
6. **Set Up Redis**:
   - Install Redis:
     ```bash
     sudo apt install redis-server
     sudo systemctl start redis
     sudo systemctl enable redis
     ```
7. **Set Environment Variables**:
   - Create a `.env` file:
     ```
     SECRET_KEY=your-django-secret-key
     DATABASE_URL=postgresql://umbrachat:your-password@localhost:5432/umbrachat_db
     REDIS_URL=redis://localhost:6379/0
     ```
     - For Option 2 `settings.py`, use:
       ```
       SECRET_KEY=your-django-secret-key
       DB_PASSWORD=your-password
       ```
     - Generate a secure `SECRET_KEY`:
       ```bash
       python -c "import secrets; print(secrets.token_hex(32))"
       ```
8. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```
9. **Run the Application**:
   - Start the Django development server:
     ```bash
     python manage.py runserver
     ```
   - In a separate terminal, start Daphne for WebSocket support:
     ```bash
     daphne -b 0.0.0.0 -p 8001 umbrachat.asgi:application
     ```

### Usage
- Open `http://localhost:8000` in a browser.
- Register an account, accept the Privacy Policy, and start chatting.
- Use the UI to send friend requests, create group chats, or manage data (e.g., export as JSON).
- WebSockets handle real-time chat via `ws://localhost:8001`.

### Troubleshooting
- **Database Errors**: Verify PostgreSQL is running (`sudo systemctl status postgresql`) and `.env` credentials match `settings.py`.
- **WebSocket Errors**: Ensure Redis is running (`sudo systemctl status redis`) and Daphne is on port 8001.
- **Dependency Errors**: Run `pip install -r requirements.txt` and check `requirements.txt` for missing packages (e.g., `python-dotenv`).

## 🚀 System Deployment on Railway
UmbraChat is deployed on Railway, a platform that simplifies application deployment with managed databases and WebSocket support.
```mermaid
flowchart TD
    A[Client] -->|WebSocket| B["Daphne ASGI Server<br/>(Railway $PORT)"]
    A -->|HTTPS API| C["Django REST<br/>(Railway $PORT)"]
    B -->|HTTP/WS| D[Django Channels]
    C -->|JWT Auth| E[Authentication Service]
    D -->|Redis Pub/Sub| F[Railway Redis]
    D -->|Database Queries| G[Railway PostgreSQL]
```
### Deployment Architecture
- **Application**: Built from a GitHub repository.
- **Database**: Managed PostgreSQL.
- **Cache/Channel Layer**: Managed Redis for WebSockets.
- **Networking**: Railway handles HTTP and WebSocket routing.
- **Scaling**: Automatic resource scaling.

### Prerequisites
- Railway account (sign up at railway.app; free trial includes $5 in credits).
- GitHub repository with UmbraChat.
- (Optional) Railway CLI.

### Deployment Steps
1. **Prepare the Repository**:
   - Ensure `requirements.txt` includes `django`, `channels`, `djangorestframework`, `redis`, `psycopg2-binary`, `daphne`.
   - Add a `.python-version` file:
     ```
     3.10
     ```
   - (Optional) Add a `Dockerfile`:
     ```dockerfile
     FROM python:3.10
     WORKDIR /app
     COPY requirements.txt .
     RUN pip install -r requirements.txt
     COPY . .
     CMD ["daphne", "-b", "0.0.0.0", "-p", "$PORT", "umbrachat.asgi:application"]
     ```
   - Push to GitHub:
     ```bash
     git add .
     git commit -m "Prepare for Railway"
     git push origin main
     ```

2. **Create a Railway Project**:
   - Log in to railway.app, click **New Project**, and select **Deploy from GitHub Repo**.
   - Connect your GitHub account and choose the UmbraChat repository.

4. **Provision PostgreSQL and Redis**:
   - Click **New** > **Database** > **PostgreSQL**.
   - Repeat for Redis: **New** > **Database** > **Redis**.
   - Note the `DATABASE_URL` and `REDIS_URL` in each service’s **Variables** tab.

5. **Set Environment Variables**:
   - In the service’s **Variables** tab, add:
     ```
     SECRET_KEY=your-secure-secret-key
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     REDIS_URL=${{Redis.REDIS_URL}}
     ```

6. **Configure Deployment**:
   - In **Settings**, set:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `daphne -b 0.0.0.0 -p $PORT umbrachat.asgi:application`

7. **Deploy**:
   - Push to GitHub to trigger auto-deployment.
   - (Optional) Use Railway CLI:
     ```bash
     railway up
     ```

8. **Verify Deployment**:
   - In **Settings** > **Domains**, click **Generate Domain** (e.g., `https://umbrachat-production.up.railway.app`).
   - Visit the URL and check **Deployments** > **Logs** for errors.

9. **SSL and Monitoring**:
   - Railway provides HTTPS automatically.
   - Monitor via the **Observability** tab.

### Deployment Notes
- **Nixpacks**: Without a `Dockerfile`, Railway uses Nixpacks. Verify `.python-version` for Python 3.10.
- **Backups**: Enable PostgreSQL backups in Railway.
- **Redis**: Configure persistence in Redis settings.
- **WebSockets**: Supported natively by Railway.
- **Cost**: Free trial covers initial deployment; Hobby plan ($5/month) for continued use.


