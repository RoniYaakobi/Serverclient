class vehicle:
    def __init__(self,name,number_of_wheels):
        self.name = name
        self.number_of_wheels = number_of_wheels

    def how_many_wheels(self):
        print(f"{self.name} has {self.number_of_wheels} wheels.")

    def change_name(self,newname):

        print(f"{self.name}'s new name is {newname}")
        self.name = newname


car = vehicle("Ferrari",4)
bike = vehicle("Bike",2)

for i in [car,bike]:
    i.how_many_wheels()


bike.change_name("Bicylce")

for i in [car,bike]:
    i.how_many_wheels()






class tricycle(vehicle):
    def __init__(self, name, seat_color):
        super().__init__(name, 3)
        self.seat_color = seat_color
    
    def get_seat_color(self):
        return(self.seat_color)

tcyc = tricycle("Tricycle","Black")


for i in [tcyc, car,bike]:
    try:
        print(i.get_seat_color())
    except AttributeError:
        print(f"Error: {i.name} has no attribute 'get_seat_color()'")
