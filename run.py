from dotenv import load_dotenv

from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create Flask application instance
app = create_app()

if __name__ == "__main__":
    # Run the application
    app.run()
