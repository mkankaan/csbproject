# Chat app

This project requires Python, Flask and Sqlite3. This project is a simple chat application. Users can create chat rooms, invite members to chat rooms and send messages. Inviting members and deleting a room can only be done by the owner. Users are not supposed to be able to view eachothers' profiles or access chat rooms that they're not a member of.

The project demonstrates 6 security flaws from the OWASP Top 10 list (2021):

1. Broken Access Control
2. Injection
3. CSRF (not on the list)
4. Cryptographic Failures
5. Security Logging and Monitoring Failures
6. Identification and Authentication Failures

## Installation

### Activate a virtual environment (Linux/MacOS):

```
python3 -m venv venv
source venv/bin/activate
```



### Activate a virtual environment (Windows):

```
python3 -m venv venv
venv\Scripts\activate
```

### Run the application

Run the following commands in the project folder:

```
sqlite3 database.db < schema.sql
pip install flask
flask run
```

The application will open in http://127.0.0.1:5000
