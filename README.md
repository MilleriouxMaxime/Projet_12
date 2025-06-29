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
   python utils/init_db.py
   ```
   *Creates the database structure and all necessary tables (employees, clients, contracts, events)*

3. **Seed the database with sample data**:
   ```bash
   python utils/seed_db.py
   ```
   *Populates the database with sample employees across all departments (Commercial, Support, Management) for testing*

4. **Seed the database with sample business data**:
   ```bash
   python utils/seed_events.py
   ```
   *Creates sample clients, contracts, and events for comprehensive testing of the CRM functionality*

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

## Available Commands


### Authentication
- `login`: Log in to the system
- `logout`: Log out of the system

### Employee Management (Management Team Only)
- `employee create`: Create a new employee
  - Options: `--employee-number`, `--full-name`, `--email`, `--department`, `--role`
- `employee update`: Update an existing employee
  - Options: `--employee-number`, `--full-name`, `--email`, `--department`, `--role`
- `employee delete`: Delete an employee
- `employee list`: List all employees

### Client Management
- `client create`: Create a new client (Commercial Team Only)
  - Options: `--full-name`, `--email`, `--phone`, `--company-name`
- `client update`: Update an existing client (Commercial Team Only)
  - Options: `--full-name`, `--email`, `--phone`, `--company-name`
- `client list`: List all clients (Commercial Team sees only their clients)

### Contract Management
- `contract create`: Create a new contract (Management Team Only)
  - Options: `--client-id`, `--commercial-id`, `--total-amount`, `--remaining-amount`
- `contract update`: Update an existing contract
  - Management Team: Can update any contract
  - Commercial Team: Can only update their clients' contracts
  - Options: `--total-amount`, `--remaining-amount`, `--is-signed`
- `contract list`: List contracts with filters
  - Options: `--unsigned`, `--unpaid`
  - Commercial Team: Sees only their clients' contracts

### Event Management
- `event create`: Create a new event (Commercial/Management Team Only)
  - Options: `--contract-id`, `--client-id`, `--support-id`, `--name`, `--start-date`, `--end-date`, `--location`, `--attendees`, `--notes`
- `event update`: Update an existing event
  - Management Team: Can update any event
  - Commercial Team: Can only update events for their clients' contracts
  - Support Team: Can only update events assigned to them
  - Options: `--name`, `--start-date`, `--end-date`, `--location`, `--attendees`, `--notes`
- `event list`: List events with filters
  - Options: 
    - `--contract-id`: Filter by contract
    - `--client-id`: Filter by client
    - `--without-support`: Show events without support (Management Team)
    - `--my-events`: Show only assigned events (Support Team)
  - Commercial Team: Sees only their clients' events
  - Support Team: Sees all events but can filter to their assignments

## Department Permissions

### Management Team
- Full access to employee management
- Full access to contract management
- Can create and modify all events
- Can view all data
- Can filter events without support

### Commercial Team
- Can create and update their clients
- Can update their clients' contracts
- Can create events for signed contracts
- Can update events for their clients' contracts
- Can view their clients' data
- Can filter contracts by unsigned/unpaid status

### Support Team
- Can view all events
- Can update events assigned to them
- Can filter events to show only their assignments

## Notes
- All dates should be in format: YYYY-MM-DD HH:MM
- All monetary amounts should be in decimal format (e.g., 1000.00)
- Email addresses must be unique
- Contract events can only be created for signed contracts
- Support employees must be from the support department

## Sentry Integration

The application uses Sentry for error tracking and monitoring. To set up Sentry:

1. Create a Sentry account at https://sentry.io if you don't have one already.

2. Create a new project in Sentry and get your DSN (Data Source Name).

3. Add your Sentry DSN to the `.env` file:
```env
SENTRY_DSN=your-sentry-dsn-here
```

4. The application will automatically log:
   - All unexpected exceptions with context
   - Employee creation, updates, and deletions
   - Contract signatures
   - Event-related operations

5. You can view all logs and errors in your Sentry dashboard at https://sentry.io

Note: Make sure to keep your Sentry DSN secure and never commit it to version control.