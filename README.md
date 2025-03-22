# FooDie - Food Finder and BMI Calculator

## Description
FooDie is an application designed to help users manage their food preferences and calculate their Body Mass Index (BMI). It features an intuitive interface for exploring healthy recipes based on BMI values and provides a BMI calculator to assist users in maintaining a healthy lifestyle.

## Features
- **BMI Calculator**: Allows users to calculate their BMI based on height and weight.
- **Healthy Recipe Generator**: Recommends recipes based on the user's BMI category (Underweight, Normal weight, Overweight, Obesity).
- **User Registration and Login**: Provides authentication for users.
- **Admin Dashboard**: Allows admin to manage user data and monitor BMI records.
- **Recipe Saving**: Users can save recipes to their profile for future reference.

## Installation

Follow the steps below to get started with the FooDie application:

### 1. Clone the Repository
Clone the repository to your local machine:

```bash
git clone https://github.com/vishnuqd/FRS.git
```

### 2. Set Up a Virtual Environment
Create and activate a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

- **Windows** (Git Bash):
  ```bash
  source venv/Scripts/activate
  ```
  
- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies
Install the required dependencies by running the following command:

```bash
pip install -r requirements.txt
```

### 4. Set Up the Database
Make sure you have a MySQL database running. You can use **XAMPP** or any MySQL server of your choice. Once the server is up, run the queries in the `tables.sql` file to create the necessary tables for this project.

#### `tables.sql` file contains the following table creation queries:

```sql
-- Create User Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create BMIRecord Table
CREATE TABLE IF NOT EXISTS bmi_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    height DECIMAL(5, 2),
    weight DECIMAL(5, 2),
    bmi DECIMAL(5, 2),
    category ENUM('Underweight', 'Normal weight', 'Overweight', 'Obesity'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create Saved Recipe Table
CREATE TABLE IF NOT EXISTS saved_recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(255),
    image VARCHAR(255),
    used_ingredients TEXT,
    missed_ingredients TEXT,
    likes INT,
    spoonacular_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 5. Run the Backend Server
Navigate to the backend folder and run the backend server using **Uvicorn**:

```bash
cd backend
uvicorn main:app --reload
```

### 6. Running the Frontend
- Make sure you have the **frontend** (HTML, CSS, JavaScript) in place. The frontend is ready to interact with the backend once it’s running.
- If you are using any local frontend (like `index.html`, `bmi.html`, etc.), you can open these HTML files directly in the browser or run them via a static server like **VS Code Live Server**.

### 7. API Endpoints

Here are the key API endpoints for the application:

#### **User Authentication**:
- **POST `/auth/register`**: Register a new user.
- **POST `/auth/login`**: Login and get JWT token for authentication.
- **POST `/auth/logout`**: Logout the user (removes JWT).

#### **BMI Calculation**:
- **POST `/bmi`**: Calculate BMI and save the record.
- **GET `/bmi/last_bmi`**: Get the last BMI record for the logged-in user.

#### **Recipe Features**:
- **GET `/recipes/by_ingredients`**: Get recipes based on user’s ingredients.
- **POST `/recipes/save_recipe`**: Save a recipe for the logged-in user.
- **GET `/recipes/saved_recipes`**: Get the saved recipes for the logged-in user.
- **DELETE `/recipes/delete_recipe/{id}`**: Delete a saved recipe by its ID.

## Testing
To test the application, use **Postman** or **Swagger UI** (available at `http://localhost:8000/docs` after running the backend server). Make sure to test the following actions:
- Register a user and login.
- Calculate BMI and fetch recommended recipes.
- Save, view, and delete recipes.

---

### **File Structure**:
Here is the basic structure of the project:
```
- /backend
  - /models
  - /schemas
  - /auth.py
  - /recipes.py
  - /bmi.py
  - /database.py
  - /main.py
  - /tables.sql
- /frontend
  - /index.html
  - /bmi.html
  - /recipe.html
  - /styles.css
- requirements.txt
- README.md
```

### **Dependencies**:
Below are the required packages for running the backend:

- **FastAPI**: For building the backend API.
- **Uvicorn**: For serving the FastAPI app.
- **SQLAlchemy**: For ORM and database handling.
- **MySQL**: For the MySQL database.
- **Passlib**: For password hashing.

Make sure these dependencies are installed using the `requirements.txt`.

