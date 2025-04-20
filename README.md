# UmbraChat – Real-Time Messaging App with Django Channels 💬

**UmbraChat** is a real-time messaging web app built using Django Channels, WebSockets, Redis, and PostgreSQL. It supports private and group chats, read receipts, friend requests, user account control, and a clean dark mode interface.

Built as a Big Data Engineering course project, UmbraChat focuses on scalable infrastructure, privacy-first design, and smooth real-time interactions. Whether you're chatting one-on-one or in groups, messages are delivered instantly — even at night 🌒.

---

## 🔑 Features

- One-on-one chat with real-time delivery and read receipts
- Group chat with add/remove members
- WebSocket-based communication via Django Channels
- Friend requests (mutual acceptance required)
- User registration, login, and secure authentication
- Delete your account or download your data as JSON
- GDPR-style privacy consent during sign-up
- Personalized UI with dark mode and starry background

---

## ⚙️ Technologies Used

- **Python**, **Django 5**, **Django REST Framework**
- **Django Channels**, **Redis**, **Daphne**
- **PostgreSQL** for scalable data storage
- **JavaScript**, **CSS**, **HTML**
- **JWT (SimpleJWT)** for secure token-based auth
- **Docker** for containerized deployment

---

## 🔐 Privacy & GDPR Compliance

UmbraChat was designed with privacy in mind, following principles aligned with the **General Data Protection Regulation (GDPR)**:

- 🔒 **Secure Password Handling** – Uses Django’s built-in hashing, never stores plain text
- 👤 **Minimal Data Collection** – Stores only what's necessary for communication
- 🧾 **User Control** – Delete your messages or entire account anytime
- ✅ **Consent Required** – Users must accept the Privacy Policy to register
- 📜 **Clear Policy Access** – Transparent documentation of how data is stored and used
- 📁 **Downloadable User Data** – Export your personal info as JSON at any time

---

## 📚 About This Project

UmbraChat was developed by a second-year Data Engineering student as part of a hands-on course project. The focus was on building a system that combines real-time data processing, backend scalability, and good privacy practices — all while looking good in dark mode.

