# RecipeVault

## Objective

The objective of this project is to create a comprehensive and feature-rich web application using Python and Flask. The application allows users to manage and share their favorite recipes through a set of well-defined APIs.

## Features

### User Authentication and Authorization

- **Register**: Users can create an account with a unique username and password.
- **Login**: Secure login functionality using JWT for session management.

### Recipe Management

- **Create Recipe**: Authenticated users can create new recipes with details like title, description, ingredients, and instructions.
- **Read Recipes**:
  - **List All Recipes**: Retrieve all recipes with pagination support.
  - **View Single Recipe**: View detailed information about a specific recipe by its ID.
  - **Search Recipes**: Search for recipes by title or ingredients.
- **Update Recipe**: Users can update their own recipes.
- **Delete Recipe**: Users can delete their own recipes.

### Database Interactions

- **Relational Database**: Uses a relational database to store user and recipe data.

### Testing

- **Unit Tests**: Comprehensive tests to ensure functionality of critical components.
- **Testing Libraries**: Uses `unittest` for automated testing.

## REST API Endpoints

### Projects

- **Register a new user** (with pagination):

  - Endpoint: `/auth/register`
  - Method: `POST`

  ```json
  {
    "username": "user1",
    "email": "user1@example.com",
    "password": "Password123!"
  }
  ```

- **Login a user**:

  - Endpoint: `/auth/login`
  - Method: `POST`

  ```json
  {
    "email": "user1@example.com",
    "password": "Password123!"
  }
  ```

- **Logout a user**

  - Endpoint: `/auth/logout`
  - Method: `POST`

  ```heasers
     Authorization: Bearer <access_token>
  ```

- **List all recipes**:

  - Endpoint: `/api/recipes/`
  - Method: `GET`

- **Create a new recipe** (including all tasks for the project):

  - Endpoint: `/api/recipes/`
  - Method: `POST`

  ```json
  {
    "title": "Recipe Title",
    "description": "Recipe Description",
    "ingredients": "List of ingredients",
    "instructions": "Step by step instructions"
  }
  ```

- **View a specific recipe**

  - Endpoint: `/api/recipes/<int:id>`
  - Method: `GET`

- **View a project** (including all tasks for the project):

  - Endpoint: `/api-projects/<int:pk>/`
  - Method: `GET`

- **Update a specific recipe**

  - Endpoint: `/api/recipes/<int:id>`
  - Method: `PUT`

  ```json
  {
    "title": "Updated Recipe Title",
    "description": "Updated Recipe Description",
    "ingredients": "Updated list of ingredients",
    "instructions": "Updated step by step instructions"
  }
  ```

- **Delete a specific recipe**

  - Endpoint: `/api/recipes/<int:id>`
  - Method: `DELETE`

- **Search receipe by title**

  - Endpoint: `/api/recipes?search=pasta&page=int`
  - Method: `GET`

## Setup Instructions

### Prerequisites

- Python 3.8+
- Flask
- SQLAlchemy
- Flask-JWT-Extended
- Flask-Migrate

## Setup and Installation

1. **Clone the repository**:

   ```sh
   git clone https://github.com/tejas-21sept/recipe-vault.git
   cd recipe-vault

   ```

2. **Create a virtual environment and activate it**:

   i.Open a terminal:

   - Windows: Open `Command Prompt` or `PowerShell`.
   - macOS/Linux: Open a terminal window.

   ii. Navigate to the project directory:

   ```python
     cd recipe-vault

   ```

   iii. Create the virtual environment:

   ```python
     python -m venv venv

   ```

   iv. Activate the virtual environment:

   ```python

     source venv/bin/activate  # Linux/macOS

     venv\Scripts\activate.bat  # Windows

   ```

3. **Install dependencies**:

```pip
  pip install -r requirements.txt
```

4. **Run the migrations**:

   ```python
       flask db init
       flask db migrate -m "Details about migrations."
       flask db upgrade

   ```

5. **Create a .env file:**:
   Create a .env file in the root directory of your project, copy the contents of .env.example into it and add yout secret credentials in it.

6. **Start the development server**:

   ```python
       flask run
   ```

7. **Testing the apis**:

   ```python
         # For Windows
        set FLASK_CONFIG=TestConfig
        set TESTING_DATABASE_URL=mysql+pymysql://root:MySQL@localhost:3306/receipe_book
        set PRODUCTION_DATABASE_URL=mysql+pymysql://root:MySQL@localhost:3306/receipe_book_testing_db

        # For Linux/MacOS
         export FLASK_CONFIG=TestConfig
         export TESTING_DATABASE_URL=mysql+pymysql://root:MySQL@localhost:3306/receipe_book
         export PRODUCTION_DATABASE_URL=mysql+pymysql://root:MySQL@localhost:3306/receipe_book_testing_db
   ```

   For testing, use following commands.

   ```python
         python -m unittest discover -s tests
   ```

## Suggestions and Improvements

Feedback, suggestions, and contributions to enhance this project are highly appreciated! If you have any ideas to improve the functionality, add new features, or fix issues, please don't hesitate to reach out or submit a pull request.

## Contact

For any inquiries or assistance, feel free to reach out via email at [tejasj.1022@gmail.com](mailto:tejasj.1022@gmail.com). Your feedback is valuable and will be promptly addressed.
