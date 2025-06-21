# Projet_12 - EpicEvents

## Database Configuration

This project uses **SQLite** as the default database.

### Installation and Initialization

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database**:
   ```bash
   python init_db.py
   ```

3. **Seed the database with sample data**:
   ```bash
   python seed_db.py
   ```

### Database Structure

The project uses SQLAlchemy with the following models:
- **Employee**: Employees with different departments (Commercial, Support, Management)
- **Client**: Company clients
- **Contract**: Contracts between clients and sales representatives
- **Event**: Events related to contracts

### SQLite Advantages

- **Simplicity**: No database server installation required
- **Portability**: The database file can be easily moved
- **Development**: Ideal for development and testing
- **Performance**: Excellent performance for medium-sized applications 
