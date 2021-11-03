import math


class Rover:
    def __init__(self, width=12, length=18):
        self.rover_width = width
        self.rover_length = length
        self.center_mass = [0, 0]
        self.front_1 = None
        self.front_2 = None
        self.rare_2 = None
        self.rare_1 = None
        self.angle = 90

    def find_rover_upset(self, pos, alpha):
        """Define four corners of rover and central mass point. Rover is Rectangle"""
        half_width = self.rover_width / 2.0
        half_length = self.rover_length / 2.0
        if 0 == alpha:
            front_1 = [pos[0] - half_width, pos[1] - half_length]
            front_2 = [pos[0] + half_width, pos[1] - half_length]
            rare_1 = [pos[0] - half_width, pos[1] + half_length]
            rare_2 = [pos[0] + half_width, pos[1] + half_length]
            intersect_1 = [pos[0], pos[1]+half_length]
            intersect_2 = [pos[0], pos[1] - half_length]
        elif alpha < 90:
            betta = 90 - alpha
            x = half_length * math.cos(betta*math.pi/180.0)
            y = half_length * math.sin(betta*math.pi/180.0)
            intersect_1 = [pos[0] + x, pos[1] - y]
            intersect_2 = [pos[0] - x, pos[1] + y]
            x2 = half_width * math.sin(betta*math.pi/180.0)
            y2 = half_width * math.cos(betta*math.pi/180.0)
            front_1 = [intersect_1[0] - x2, intersect_1[1] - y2]
            front_2 = [intersect_1[0] + x2, intersect_1[1] + y2]
            rare_1 = [intersect_2[0] - x2, intersect_2[1] - y2]
            rare_2 = [intersect_2[0] + x2, intersect_2[1] + y2]
        elif alpha < 180:
            betta = 180 - alpha
            gamma = 90 - betta
            x = half_length * math.cos(gamma*math.pi/180.0)
            y = half_length * math.sin(gamma*math.pi/180.0)
            intersect_1 = [pos[0] + x, pos[1] + y]
            intersect_2 = [pos[0] - x, pos[1] - y]
            x2 = half_width * math.cos(betta*math.pi/180.0)
            y2 = half_width * math.sin(betta*math.pi/180.0)
            front_1 = [intersect_1[0] + x2, intersect_1[1] - y2]
            front_2 = [intersect_1[0] - x2, intersect_1[1] + y2]
            rare_1 = [intersect_2[0] + x2, intersect_2[1] - y2]
            rare_2 = [intersect_2[0] - x2, intersect_2[1] + y2]
        elif alpha < 270:
            betta = 270 - alpha
            gamma = 90 - betta
            x = half_length * math.cos(betta * math.pi / 180.0)
            y = half_length * math.sin(betta * math.pi / 180.0)
            intersect_1 = [pos[0] - x, pos[1] + y]
            intersect_2 = [pos[0] + x, pos[1] - y]
            y2 = half_width * math.sin(gamma * math.pi / 180.0)
            x2 = half_width * math.cos(gamma * math.pi / 180.0)
            front_1 = [intersect_1[0] + x2, intersect_1[1] + y2]
            front_2 = [intersect_1[0] - x2, intersect_1[1] - y2]
            rare_1 = [intersect_2[0] + x2, intersect_2[1] + y2]
            rare_2 = [intersect_2[0] - x2, intersect_2[1] - y2]
        elif alpha <= 360:
            betta = 360 - alpha
            gamma = 90 - betta
            x = half_length * math.sin(betta*math.pi / 180.0)
            y = half_length * math.cos(betta*math.pi / 180.0)
            intersect_1 = [pos[0] - x,pos[1] - y]
            intersect_2 = [pos[0] + x, pos[1] + y]
            x2 = half_width * math.sin(gamma*math.pi / 180.0)
            y2 = half_width * math.cos(gamma*math.pi / 180.0)
            front_1 = [intersect_1[0] - x2, intersect_1[1] + y2]
            front_2 = [intersect_1[0] + x2, intersect_1[1] - y2]
            rare_1 = [intersect_2[0] - x2, intersect_2[1] + y2]
            rare_2 = [intersect_2[0] + x2, intersect_2[1] - y2]
        else:
            raise IndexError('Error: angle bigger than 360 degree')

        self.front_1 = (math.floor(front_1[0]), math.floor(front_1[1]))
        self.front_2 = (math.floor(front_2[0]), math.floor(front_2[1]))
        self.rare_1 = (math.floor(rare_1[0]), math.floor(rare_1[1]))
        self.rare_2 = (math.floor(rare_2[0]), math.floor(rare_2[1]))
        return [self.front_1, self.front_2, self.rare_2, self.rare_1, pos, alpha]

    def set_rover_angle(self, deg):
        """Change the rover movement direction"""
        self.angle = deg

    def get_angle(self):
        return self.angle

    def get_rover_width(self):
        return self.rover_width

    def get_rover_length(self):
        return self.rover_length
