# Go Game Backend

This is the backend API for the Go Game Fullstack project. It is built with Flask, SQLAlchemy, and supports JWT authentication. The backend connects to a PostgreSQL database and is designed to work seamlessly with the Go Game frontend.

## Features

- User signup and login (JWT authentication)
- Game creation, move saving, pausing, finishing, and history retrieval
- RESTful API endpoints
- CORS enabled for frontend connection

## Getting Started

### Prerequisites

- Python 3.12
- PostgreSQL database
- [pipenv](https://pipenv.pypa.io/en/latest/)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/go-backend.git
    cd go-backend
    ```

2. Install dependencies:
    ```sh
    pipenv install
    ```

3. Set up environment variables in `.env`:
    ```
    DATABASE_URL=your_postgres_url
    SECRET_KEY=your_secret_key
    JWT_SECRET_KEY=your_jwt_secret_key
    ```

4. Run migrations:
    ```sh
    pipenv run flask db upgrade
    ```

5. Start the server:
    ```sh
    pipenv run python main.py
    ```

## Connecting to the Frontend

- The backend is configured to accept requests from the frontend at `http://localhost:5173` (see [`CORS`](app/__init__.py)).
- Make sure your frontend is running on this address, or update the CORS settings in [`app/__init__.py`](app/__init__.py) as needed.

## API Usage

### User Endpoints

- `POST /user/signup` — Register a new user
- `POST /user/login` — Login and receive JWT token

### Game Endpoints

- `POST /game/new` — Start a new game (JWT required)
- `GET /game/active` — Get current active game (JWT required)
- `POST /game/<game_id>/move` — Save a move (JWT required)
- `POST /game/pass` — Pass turn (JWT required)
- `POST /game/finish` — Finish game (JWT required)
- `POST /game/pause` — Pause game (JWT required)
- `GET /game/history` — Get game history (JWT required)

Include the JWT token in the `Authorization: Bearer <token>` header for protected endpoints.

## Contributors

1. Horace Kauna  
2. Cynthia Mugo  
3. Wayne Muongi  
4. Irene Murage  
5. Ian Mabruk

Feel free to open issues or submit pull requests!

