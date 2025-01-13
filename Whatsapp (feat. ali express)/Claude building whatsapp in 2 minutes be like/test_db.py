from database_manager import DatabaseManager

db = DatabaseManager()

# Create a test user
db.create_user("test", "password123", "test@example.com")

# Create some test rooms
general_room = db.create_room("General", "General discussion room")
random_room = db.create_room("Random", "Random discussions")

# Add user to rooms
db.add_user_to_room(1, general_room)  # user_id 1 to general room
db.add_user_to_room(1, random_room)   # user_id 1 to random room

print("Test user and rooms created successfully!")
print("You can now log in with:")
print("Username: test")
print("Password: password123")