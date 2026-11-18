# Juliet's Sweet Treats 🍰

A bakery order management system built to help Juliet's Sweet Treats manage customer orders, payments, products, and business reports.

## Features

- Create and manage customer orders.
- Add multiple products to an order.
- Calculate order totals automatically.
- Record full and partial payments.
- Track paid, unpaid, and outstanding balances.
- View, search, edit, and delete orders.
- Manage customer information.
- View and print order receipts.
- Generate Excel business reports.
- Automatically back up the database.

## Technologies Used

- Python
- FastAPI
- SQLite
- HTML and CSS
- Jinja2
- OpenPyXL
- Git and GitHub

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/juinalegwu/JulietEne.git
cd JulietEne
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

Linux/macOS:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

Start the application with:

```bash
uvicorn app.main:app --reload
```

Open your browser and visit:

http://127.0.0.1:8000

## Database and Backups

The application uses SQLite to store customer, order, product, and payment information.

Automatic database backups are created when the application starts.

Backups are stored in the `backups/` directory. The application keeps the seven most recent automatic backups.

## Project Status

The application is under active development.

Built for Juliet's Sweet Treats.
