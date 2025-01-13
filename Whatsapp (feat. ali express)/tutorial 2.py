# bike
NAME = "bike"
number_of_wheels = 2

def how_many_wheels():
    print(f"{NAME} has {number_of_wheels} wheels.")

def change_name(newname):
    print(f"{NAME}'s new name is {newname}")
    name = newname

how_many_wheels()

change_name("Bicylce")

how_many_wheels()

# after creating the tcyc object

try:
    print(get_seat_color())
except AttributeError:
    print(f"Error: {name} has no attribute 'get_seat_color()'")