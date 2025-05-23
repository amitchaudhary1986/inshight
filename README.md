# Project Title: Analytics Dashboard

## Project Overview
This project is an analytics dashboard designed to provide insights into interview processes and platform engagement. It helps track metrics such as interview completion rates, candidate progression through hiring stages, platform feature usage, and overall system health. The backend is built with Django and Django REST Framework, providing a comprehensive API. The frontend is a Next.js application for dynamic data visualization and user interaction.

## Prerequisites
(Placeholder for required software like Python, Node.js, npm/yarn, pip)
- Python (e.g., 3.10 or higher)
- Pip (Python package installer)
- Node.js (e.g., 18.x or higher)
- npm (Node package manager, usually comes with Node.js)

## Backend Setup (Django)
(Placeholder for Django setup instructions)

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Navigate to the Django project directory:**
    ```bash
    cd analytics_dashboard
    ```

3.  **Create and activate a virtual environment:**
    *   On macOS and Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

4.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser (optional, for admin access):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the Django development server:**
    ```bash
    python manage.py runserver
    ```
    The backend will typically be available at `http://localhost:8000`.

## Frontend Setup (Next.js)
(Placeholder for Next.js setup instructions)

1.  **Navigate to the frontend directory (from the root of the cloned repository):**
    ```bash
    cd frontend
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Set up environment variables:**
    Create a `.env.local` file in the `frontend` directory by copying the example or creating a new one:
    ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```
    This variable points to your Django backend API.

4.  **Run the Next.js development server:**
    ```bash
    npm run dev
    ```
    The frontend will typically be available at `http://localhost:3000`.

## Running the Application
(Placeholder for instructions on how to access the app)

- Once both the backend and frontend servers are running:
  - Access the frontend application by navigating to `http://localhost:3000` in your web browser.
  - You should be able to register, log in, and view the dashboard.
  - The Django admin panel (if a superuser was created) can be accessed at `http://localhost:8000/admin/`.

## Key API Endpoints
(Placeholder for listing important API endpoints)

The main API is served from `/api/` relative to the backend URL (e.g., `http://localhost:8000/api/`).

*   **Authentication:**
    *   `/api/auth/login/` (POST): User login
    *   `/api/auth/logout/` (POST): User logout
    *   `/api/auth/registration/` (POST): User registration
    *   `/api/auth/user/` (GET): Get current user details (requires token authentication)
*   **Core Data Models (CRUD via ViewSets):**
    *   `/api/employers/`
    *   `/api/candidates/`
    *   `/api/recruiters/`
    *   `/api/interviews/`
    *   `/api/feedback/`
    *   `/api/featureusage/`
    *   `/api/systemissues/`
*   **Analytics Endpoints:**
    *   `/api/analytics/engagement/` (GET): Engagement metrics
    *   `/api/analytics/candidate-progression/` (GET): Candidate progression funnel data

(More detailed documentation for each endpoint, including request/response formats, would typically be provided via API documentation tools like Swagger/OpenAPI, which can be integrated with Django REST Framework.)
