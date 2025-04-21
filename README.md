# UmbraChat – Real-Time Messaging App with Django Channels 💬

UmbraChat is a real-time messaging web app built using Django Channels, WebSockets, Redis, and PostgreSQL. It supports private and group chats, read receipts, friend requests, user account control, and a clean dark mode interface.

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

## 🚀 System Deployment on Railway

UmbraChat is deployed on [Railway](https://railway.app), a platform that simplifies provisioning, building, and deploying applications with integrated support for databases, caching, and WebSocket connections. This section guides you through deploying UmbraChat on Railway, leveraging its GitHub integration and managed services for PostgreSQL and Redis.

### Deployment Architecture
- **Application**: Railway builds and deploys UmbraChat from a GitHub repository, using a `Dockerfile` or auto-detected Python build settings.
- **Database**: Railway provisions a managed PostgreSQL database.
- **Cache/Channel Layer**: Railway provisions a managed Redis instance for WebSocket communication.
- **Networking**: Railway handles HTTP and WebSocket routing, eliminating the need for manual Nginx configuration.
- **Scaling**: Railway automatically scales resources based on demand.

### Prerequisites
- A Railway account (sign up at [railway.app](https://railway.app)). The free trial includes $5 in credits, sufficient for initial deployment.[](https://railway.com/pricing)
- A GitHub account with the UmbraChat repository pushed to it.
- The Railway CLI (optional, for local deployment or management).
- Local development tools (for testing before deployment):
  - Python 3.10+
  - Git

### Deployment Steps
1. **Set Up Local Development Environment (Optional)**:
   - If you need to install Git or other tools locally (e.g., for cloning the repo or testing), update your package lists and install dependencies on an Ubuntu-based system:
     ```bash
     sudo apt update
     sudo apt install git
     ```
   - Install the Railway CLI if you plan to deploy from the terminal:
     ```bash
     sudo apt update
     sudo apt install curl
     curl -fsSL https://railway.app/install.sh | sh
     ```
   - Log in to Railway CLI:
     ```bash
     railway login
     ```

2. **Clone and Prepare the Repository**:
   - Clone your UmbraChat repository:
     ```bash
     git clone https://github.com/<your-username>/umbrachat.git
     cd umbrachat
     ```
   - Ensure your project includes:
     - A `requirements.txt` file listing dependencies (e.g., `django`, `channels`, `djangorestframework`, `redis`, `psycopg2-binary`).
     - A `Dockerfile` (optional, as Railway can auto-detect Python projects). Example:
       ```dockerfile
       FROM python:3.10
       WORKDIR /app
       COPY requirements.txt .
       RUN pip install -r requirements.txt
       COPY . .
       CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "umbrachat.asgi:application"]
       ```
     - A `.python-version` file specifying `3.10` (if not using a `Dockerfile`), as Railway’s default Python version may be older:
       ```
       3.10
       ```

3. **Create a New Project on Railway**:
   - Log in to [railway.app](https://railway.app) and click **New Project**.
   - Select **Deploy from GitHub Repo** and connect your GitHub account.
   - Choose the UmbraChat repository from the dropdown and click **Deploy Now**.[](https://docs.railway.com/quick-start)

4. **Provision PostgreSQL and Redis**:
   - In the Railway dashboard, click **New** > **Database** > **PostgreSQL**.
   - Repeat for Redis: **New** > **Database** > **Redis**.
   - Railway will provision these services and provide connection URLs (e.g., `DATABASE_URL` and `REDIS_URL`) in the **Variables** tab of each service.

5. **Set Environment Variables**:
   - In your Railway project, go to the service’s **Variables** tab.
   - Add the following, using the connection URLs from PostgreSQL and Redis:
     ```
     SECRET_KEY=your-secure-secret-key
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     REDIS_URL=${{Redis.REDIS_URL}}
     ```
   - Railway automatically injects database variables, but you can reference them explicitly as shown.[](https://medium.com/%40andrea.faviait/deploying-a-telegram-bot-using-chatgpt-and-whisper-apis-with-railway-ef79e6cff955)
   - If your `settings.py` expects different variable names, adjust accordingly.

6. **Configure Deployment Settings**:
   - In the service’s **Settings** tab, ensure the **Build Command** is:
     ```bash
     pip install -r requirements.txt
     ```
   - Set the **Start Command** to run Daphne for WebSocket support:
     ```bash
     daphne -b 0.0.0.0 -p $PORT umbrachat.asgi:application
     ```
     Note: Railway sets the `PORT` environment variable automatically, so use `$PORT` in the command.[](https://docs.vendure.io/guides/deployment/deploy-to-railway/)
   - If using a `Dockerfile`, Railway will detect it and use its `CMD` instead.

7. **Deploy the Application**:
   - Commit and push any changes to your GitHub repository:
     ```bash
     git add .
     git commit -m "Configure for Railway deployment"
     git push origin main
     ```
   - Railway will detect the push, build, and deploy automatically.
   - Alternatively, use the Railway CLI to deploy locally:
     ```bash
     railway up
     ```

8. **Verify Deployment**:
   - Once deployed, go to the service’s **Settings** tab and click **Generate Domain** to get a public URL (e.g., `https://umbrachat-production.up.railway.app`).
   - Visit the URL to ensure the app is running.
   - Check **Deployments** > **Logs** for build or runtime errors if the app doesn’t load.

9. **Set Up SSL (Automatic)**:
   - Railway provides HTTPS by default for all generated domains, so no manual SSL setup (e.g., Certbot) is needed.[](https://docs.railway.com/quick-start)

10. **Monitor and Scale**:
    - Use Railway’s **Observability** tab to view logs and metrics.
    - Railway automatically scales resources based on load, but you can adjust CPU/RAM in the **Settings** tab for Pro plans.[](https://railway.com/features)

### Deployment Notes
- **Dockerfile vs. Nixpacks**: If you don’t provide a `Dockerfile`, Railway uses Nixpacks to build your Python app. Ensure `requirements.txt` and `.python-version` are correct to avoid version mismatches.[](https://nixpacks.com/docs/deploying/railway)
- **Database Backups**: Use Railway’s built-in PostgreSQL backups or export data with `pg_dump` for manual backups.[](https://medium.com/%40sergethiti/deploying-a-full-stack-app-on-railway-and-netlify-a-step-by-step-guide-6786105707ab)
- **Redis Persistence**: Configure Redis with persistence in the Railway dashboard for reliability.
- **WebSockets**: Railway supports WebSockets natively, so no manual Nginx configuration is needed.
- **Cost**: The free trial includes $5 in credits. After that, the Hobby plan ($5/month) covers basic usage, with additional costs for compute and storage.[](https://railway.com/pricing)
- **Updates**: Push changes to your GitHub repository to trigger automatic redeploys.
