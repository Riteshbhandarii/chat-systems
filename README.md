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

## 🚀 System Deployment

Deploy UmbraChat to a production environment using Docker, Nginx, Gunicorn, and Daphne for a scalable and secure setup.

### Deployment Architecture

- **Web Server**: Nginx (reverse proxy for HTTP and WebSocket traffic)
- **Application Server**: Gunicorn (handles HTTP requests), Daphne (handles WebSocket connections)
- **Database**: PostgreSQL (scalable storage)
- **Cache/Channel Layer**: Redis (for WebSocket channel management)
- **Containerization**: Docker and Docker Compose

### Prerequisites

- A cloud server (e.g., AWS EC2, DigitalOcean) with Ubuntu 22.04+
- Docker and Docker Compose installed
- Domain name (optional, for SSL setup)
- PostgreSQL and Redis (local or managed services)

### Deployment Steps

1. **Set Up the Server**:

   - Provision a server and install Docker:

     ```bash
     sudo apt update
     sudo apt install docker.io docker-compose
     sudo systemctl start docker
     sudo systemctl enable docker
     ```

   - Add your user to the Docker group: `sudo usermod -aG docker $USER`

2. **Clone the Repository**:

   ```bash
   git clone https://github.com/<your-username>/umbrachat.git
   cd umbrachat
   ```

3. **Configure Docker**: Create a `docker-compose.yml` file:

   ```yaml
   version: '3.8'
   services:
     web:
       build: .
       command: gunicorn umbrachat.wsgi:application --bind 0.0.0.0:8000
       volumes:
         - .:/app
       environment:
         - SECRET_KEY=${SECRET_KEY}
         - DATABASE_URL=${DATABASE_URL}
         - REDIS_URL=${REDIS_URL}
       depends_on:
         - db
         - redis
     daphne:
       build: .
       command: daphne -b 0.0.0.0 -p 8001 umbrachat.asgi:application
       volumes:
         - .:/app
       environment:
         - REDIS_URL=${REDIS_URL}
       depends_on:
         - redis
     db:
       image: postgres:15
       environment:
         - POSTGRES_DB=umbrachat_db
         - POSTGRES_USER=umbrachat
         - POSTGRES_PASSWORD=your-password
       volumes:
         - pgdata:/var/lib/postgresql/data
     redis:
       image: redis:7
     nginx:
       image: nginx:latest
       ports:
         - "80:80"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
       depends_on:
         - web
         - daphne
   volumes:
     pgdata:
   ```

   Create an `nginx.conf` file:

   ```nginx
   events {}
   http {
       server {
           listen 80;
           server_name your-domain.com;
           location / {
               proxy_pass http://web:8000;
               proxy_set_header Host $host;
               proxy_set_header X-Real-IP $remote_addr;
           }
           location /ws/ {
               proxy_pass http://daphne:8001;
               proxy_http_version 1.1;
               proxy_set_header Upgrade $http_upgrade;
               proxy_set_header Connection "upgrade";
           }
       }
   }
   ```

4. **Set Environment Variables**: Create a `.env` file:

   ```
   SECRET_KEY=your-secure-secret-key
   DATABASE_URL=postgresql://umbrachat:your-password@localhost:5432/umbrachat_db
   REDIS_URL=redis://redis:6379/0
   ```

5. **Build and Run**:

   ```bash
   docker-compose up --build -d
   ```

6. **Run Migrations**:

   ```bash
   docker-compose exec web python manage.py migrate
   ```

7. **Collect Static Files**:

   ```bash
   docker-compose exec web python manage.py collectstatic
   ```

8. **Set Up SSL (Optional but Recommended)**:

   - Install Certbot:

     ```bash
     sudo apt install certbot python3-certbot-nginx
     ```

   - Obtain an SSL certificate:

     ```bash
     sudo certbot --nginx -d your-domain.com
     ```

   - Update `nginx.conf` to include SSL:

     ```nginx
     events {}
     http {
         server {
             listen 80;
             server_name your-domain.com;
             return 301 https://$host$request_uri;
         }
         server {
             listen 443 ssl;
             server_name your-domain.com;
             ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
             ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
             location / {
                 proxy_pass http://web:8000;
                 proxy_set_header Host $host;
                 proxy_set_header X-Real-IP $remote_addr;
             }
             location /ws/ {
                 proxy_pass http://daphne:8001;
                 proxy_http_version 1.1;
                 proxy_set_header Upgrade $http_upgrade;
                 proxy_set_header Connection "upgrade";
             }
         }
     }
     ```

9. **Monitor and Scale**:

   - Check logs: `docker-compose logs`
   - Scale services if needed: `docker-compose scale web=3`

### Deployment Notes

- **Database**: Use a managed PostgreSQL service (e.g., AWS RDS) for high availability.
- **Redis**: Configure Redis with persistence and backups.
- **Security**: Ensure WebSocket connections use WSS (secure WebSockets).
- **Backups**: Schedule regular PostgreSQL backups.
- **Monitoring**: Use tools like Prometheus or CloudWatch for server monitoring.
