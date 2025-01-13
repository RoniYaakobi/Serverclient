# Car
name = "ferrari"
number_of_wheels = 4

def how_many_wheels():
    print(f"{name} has {number_of_wheels} wheels.")

def change_name(newname):
    print(f"{name}'s new name is {newname}")
    name = newname

how_many_wheels()

# after bike changes name

how_many_wheels()

# after creating the tcyc object

try:
    print(get_seat_color())
except AttributeError:
    print(f"Error: {name} has no attribute 'get_seat_color()'")