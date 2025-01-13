# tcyc
name = "tricycle"
number_of_wheels = 3

def how_many_wheels():
    print(f"{name} has {number_of_wheels} wheels.")

def change_name(newname):
    print(f"{name}'s new name is {newname}")
    name = newname

SEAT_COLOR = "black"

def get_seat_color():
    return SEAT_COLOR

# after creating the tcyc object

try:
    print(get_seat_color())
except AttributeError:
    print(f"Error: {name} has no attribute 'get_seat_color()'")
