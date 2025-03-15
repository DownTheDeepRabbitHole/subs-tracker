# Substracker
Choose subscriptions from a shared list or create custom subscriptions with your own
information. Recieve notifications for upcoming payments, and integrate with
RescueTime's screentime tracker to be notified of unused payments.

## Installation
**Warning:** the full development project (including libraries) exceeds 300MB. It's recommended to run the production version if memory is a concern.

**Prerequisites:**
- Python (install [here](https://www.python.org/downloads/))
- Node.js (install [here](https://nodejs.org/en/download))
- pip package manager (should be installed with python)

Open the subs-tracker-main directory with a code editor of choice (or terminal)

### 1. **Install Backend (Django)**

- Navigate to the backend folder.
   ```bash
  cd backend
  ```

- Setup the python virtual enviornment (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   .\venv\Scripts\activate  # On Windows
   ```

 - Install Django and dependencies.
   ```bash
   pip install -r requirements.txt
   ```

 - Start the Django server.
   ```bash
   python manage.py runserver
   ```

### 2. **Install Frontend (Vite + Vue)**

 - Open a new terminal and navigate to the frontend folder:
   ```bash
   cd frontend
   ```

- Install Node.js dependencies. **Note:** This can take a while, as node modules are very large  (~100MB)
     ```bash
     npm install
     ```

- Run the Vue project
   ```bash
   npm run dev
   ```

 ### 3. **Open the website**
The website should now be available at http://localhost:8080/. \
**Note:** By default, the backend runs on port 8000. If there are any other services running on the same port, you may recieve an error.
