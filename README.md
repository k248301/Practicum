# CryptoFlux - Crypto Trading Bot (Practicum)

This repository contains the source code for the CryptoFlux project, developed for our Practicum. It consists of a web-based dashboard and a backend news microservice.

## Project Structure

- **`Cryptoflux/`**: The frontend web application (Dashboard). Built with HTML, CSS, JavaScript (Vanilla ES Modules), and Firebase.
- **`NewsAPI/`**: A Flask-based backend microservice responsible for fetching and serving cryptocurrency news.

---

## Prerequisites

- **Python 3.8+** (for NewsAPI)
- **Web Browser** (Chrome/Firefox/Edge)
- **Local Web Server** (Recommended for the frontend, e.g., VS Code Live Server or Python `http.server`)

---

## Component Setup

### 1. NewsAPI Service

The NewsAPI service fetches crypto news from NewsAPI.org and serves it via a REST API.

**Installation:**
1. Navigate to the `NewsAPI` directory:
   ```bash
   cd NewsAPI
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

**Running the Service:**
```bash
python NewsAPI.py
```
The service will start on `http://0.0.0.0:8081`.

*For more details, check the [NewsAPI README](NewsAPI/README.md).*

---

### 2. Web Application (Cryptoflux)

The frontend is a static web application that connects to backend services.

**Running the Frontend:**
Since the app uses ES Modules, you cannot simply open `index.html` directly from the file system. You must serve it over HTTP.

**Option A: Using Python (Simplest)**
1. Navigate to the `Cryptoflux` directory:
   ```bash
   cd Cryptoflux
   ```
2. Start a simple HTTP server:
   ```bash
   python -m http.server 8000
   ```
3. Open your browser and go to `http://localhost:8000`.

**Option B: using VS Code Live Server**
1. Open the project in VS Code.
2. Right-click on `Cryptoflux/index.html`.
3. Select "Open with Live Server".

**Configuration:**
The API endpoints are configured in `Cryptoflux/js/core/constants.js`.
- **`BOT_API_URL`**: Points to the backend API.
- **`SOCKET_URL`**: Points to the WebSocket server.

*Note: Currently, these may point to remote development servers (ngrok). If you are running the full backend stack locally, update these URLs to point to your local instances (e.g., `http://localhost:8081` for the NewsAPI).*

---

## Usage

1. Start the **NewsAPI** service (running on port 8081).
2. Start the **Web App** (running on port 8000).
3. Open the Web App in your browser.
4. Log in (if required) or explore the dashboard. The news section will fetch data from the NewsAPI service.

## Developers

- **Main Branch**: Protected. Do not commit directly to Main.
- **Workflow**: Feature branches -> Pull Request -> Merge to Main.
