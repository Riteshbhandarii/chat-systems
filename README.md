# UmbraChat – Real-Time Messaging Platform with Django Channels

UmbraChat is a real-time messaging web application built using Django Channels, WebSockets, Redis, and PostgreSQL. It supports one-on-one chats, group messaging, read receipts, friend requests, user account management, and a privacy-first design.

This project was developed as part of a Big Data Engineering course, focusing on scalable backend systems and secure user communication. With a sleek dark mode interface, UmbraChat provides a smooth and modern chat experience while prioritizing performance and data privacy.

## Key Features

- One-on-one chat with read receipts
- Group chat with member management
- Real-time communication via WebSockets
- Friend requests and mutual friendship validation
- User authentication and JWT-based login
- Delete account and download personal data (JSON)
- GDPR-style privacy consent during registration
- Dark mode UI with star-themed background
- Django REST Framework APIs for backend operations

## Technologies Used

- **Python** with Django 5
- **Django Channels** for asynchronous communication
- **Redis** as message broker
- **Daphne** as ASGI server
- **PostgreSQL** for relational data storage
- **JavaScript**, **HTML**, **CSS** for frontend
- **JWT** for secure authentication
- **Docker** for containerized deployment

## Privacy and Security

- Passwords securely stored using Django's hashing system
- Only minimal user data is collected and stored
- Users can delete messages and export their data
- Privacy Policy must be accepted on registration
- Personal data access and deletion features implemented

## About the Project

UmbraChat was created to explore the technical challenges of building scalable, real-time systems for communication. The backend emphasizes asynchronous architecture, message brokering, and secure data flow. A key goal of the project was to apply big data engineering principles in a meaningful and user-focused context.

