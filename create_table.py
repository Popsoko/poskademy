import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

# Create Table users
# Create Table users
conn.execute('''
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  username TEXT,
  email TEXT,
  created_at TIMESTAMP,
  password_hash TEXT
)
''')

print("Created 'users' table successfully!")

# Create Table universities
conn.execute('''
CREATE TABLE universities (
  id INTEGER PRIMARY KEY,
  name TEXT,
  location TEXT,
  ranking INTEGER,
  picture_url TEXT
)
''')
print("Created 'universities' table successfully!")

# Create Table applications
conn.execute('''
CREATE TABLE applications (
  id INTEGER PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  course_id INTEGER REFERENCES courses(id),
  intake TEXT,
  year INTEGER
             
)
''')
print("Created 'applications' table successfully!")

# Create Table courses
conn.execute('''
CREATE TABLE courses (
  id INTEGER PRIMARY KEY,
  name TEXT,
  duration_semesters INTEGER,
  university_id INTEGER REFERENCES universities(id),
  description TEXT  -- Add this line
)
''')
print("Created 'courses' table successfully!")

# Create Table events
conn.execute('''
CREATE TABLE events (
  id INTEGER PRIMARY KEY,
  name TEXT,
  city TEXT,
  date TIMESTAMP,
  university_id INTEGER REFERENCES universities(id)
)
''')
print("Created 'events' table successfully!")

# Create Table user_follows
conn.execute('''
CREATE TABLE user_follows (
  id INTEGER PRIMARY KEY,
  follower_user_id INTEGER REFERENCES users(id),
  followed_user_id INTEGER REFERENCES users(id),
  created_at TIMESTAMP
)
''')
print("Created 'user_follows' table successfully!")

conn.close()
