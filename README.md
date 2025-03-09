# Hotel Management System

## Overview
The **Hotel Management System** is a comprehensive software designed to manage hotel operations such as guest check-in, room assignments, billing, and room services. It integrates a **MySQL database** for storing customer details and transactions, ensuring efficient management of hotel resources.

---

## Features
### Guest Management
- Register new guests with personal details and room preferences.
- Assign rooms dynamically based on availability.
- Store guest check-in details in the database.

### Room Service
- Order food from the in-house restaurant via an integrated menu.
- Automatic bill updates for services used.

### Billing & Checkout
- Generate invoices for customers based on room charges and additional services.
- Manage payments and checkout processes.

### Admin Features
- View available and occupied rooms.
- Generate revenue reports.
- Manage food menu and room service offerings.

---

## Technologies Used
- **Backend:** Python (MySQL Connector)
- **Database:** MySQL
- **Frontend (CLI-based):** Python Input/Output Operations

---

## Setup & Installation
### Prerequisites
- Install Python (version 3.x recommended).
- Install MySQL and set up the database.
- Install required Python libraries using:
  ```bash
  pip install mysql-connector-python
  ```

### Steps to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hotel-management.git
   cd hotel-management
   ```
2. Set up the MySQL database:
   - Create a database named `hotel_`.
   - Import the provided SQL schema file to create tables.
3. Configure database connection:
   - Update `host`, `user`, `password`, and `database` values in the `Database` class inside `hotel.py`.
4. Run the application:
   ```bash
   python hotel.py
   ```

---

## Database Schema
### Tables Used
- `cust` (Stores customer details)
- `info` (Manages room service and billing information)
- `revenue` (Maintains daily revenue records)

---

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to enhance the system.

---

## License
This project is licensed under the MIT License.
