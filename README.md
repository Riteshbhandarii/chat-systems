# 💬 Real-Time Chat System

A real-time chat application built with **Django**, **Django Channels**, **WebSockets**, and **Redis** — all rendered through a single-page HTML (`chat_room.html`). It supports user registration, login, and real-time messaging.

---

## 🚀 Features

- 🔐 User Registration & Login
- 🧠 Authenticated Chat Interface
- 💬 Real-Time Messaging with WebSockets
- ⚙️ Powered by Django Channels and Redis
- 🧩 Single-page chat UI (`chat_room.html`)
- 💾 Message persistence via Django ORM

---

## 🗺️ Architecture Overview


![Untitled diagram-2025-04-11-093030](https://github.com/user-attachments/assets/8e255f10-29fa-4a62-b9e4-b6c4ef6659e5)


> The system uses WebSockets to maintain a persistent connection between the frontend and backend. Redis serves as a message broker via Django Channels' channel layer. All chat logic is handled in a single template with a JavaScript WebSocket client.

---

## 🛠️ Tech Stack

- **Backend**: Django, Django Channels
- **WebSocket Layer**: ASGI, Channels Consumers
- **Message Broker**: Redis
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL (Django ORM)

---

