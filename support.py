import math
import numpy as np
import statistics
import copy


class Movement:
    def __init__(self, rover):
        self.green_zone = None
        self.background = None
        self.min_y = None  # [0, 0]  # The minimum value y-coordinate of Green-zone
        self.max_y = None  # [0, 0]  # The maximum value y-coordinate of Green-zone
        self.top_critical = None
        self.bottom_critical = None
        self.current_y = None  # Current y-coordinate of rover center mass
        self.step = 3  # 6
        self.threshold = 12  # 25
        self.circular_sector = None
        self.set_sectors(5)

    def get_top_critical(self):
        return self.top_critical

    def get_bottom_critical(self):
        return self.bottom_critical

    def set_critical_cm_y(self, rover):
        """Set rover center_masses of green bottom and green top"""
        # print(f' self.min_y={ self.min_y} \t rover.rover_width={rover.rover_width}')
        self.top_critical = self.min_y+rover.rover_width/2+1
        self.bottom_critical = self.max_y-rover.rover_width/2-1

    def reset_movement(self, vel, max_step, deg):
        """This method changes 3 instances by using private setters:
         step as velocity, threshold as a max_step, and degree to watch neighbors."""
        self.set_step(vel)
        self.set_threshold(max_step)
        self.set_sectors(deg)

    def set_step(self, vel):
        self.step = vel

    def set_threshold(self, max_step):
        self.threshold = max_step

    def set_sectors(self, unit_angle):
        self.circular_sector = [x for x in range(0, 360, unit_angle)]

    def get_y(self):
        return self.current_y

    def update_y(self, delta_y):
        self.current_y += delta_y

    def set_y(self, y):
        self.current_y = y

    def create_r_matrix(self, degree):
        """Create Rotation Matrix for given angle"""
        theta = np.radians(-1 * degree)
        c, s = np.cos(theta), np.sin(theta)
        rot = np.matrix([[c, -s], [s, c]])
        return rot

    def rotation(self, bor, rot, copy_tl):
        """Rotate np.array data by the given angle"""
        new_arr = self.shift_to_origin(bor, copy_tl)
        original_array = np.asarray(new_arr)
        original_array = original_array.transpose(1, 0)
        rotated_array = rot * original_array
        rotated_array_list = rotated_array.tolist()
        lng = rotated_array_list[0]
        lat = rotated_array_list[1]
        rotated = []
        for item_1, item_2 in zip(lng, lat):
            rotated.append([item_1, item_2])
        back_arr = self.shift_back(bor, rotated)
        rotated_array_np = np.asarray(back_arr)
        return rotated_array_np

    def cm(self, arr):
        """Find a center mass"""
        xx = [x[0] for x in arr]
        yy = [y[1] for y in arr]
        ave_x = statistics.mean(xx)
        ave_y = statistics.mean(yy)
        return round(ave_x), round(ave_y)

    def rotate_fin_pos(self, bor, pos,  degree_rt):
        # STEP 1: create matrix rotation to rotate all points on degree_rt
        matrix_rt = self.create_r_matrix(degree_rt)

        # STEP 2: find a map center mass
        arr_tuple = bor  # copy.deepcopy(bor.positions)
        arr = [list(t) for t in arr_tuple]
        x, y = self.cm(arr)
        center_mass = [x, y]

        # STEP 3: shift all point to origin O(x, y) = (0, 0) Left Top Corner
        for item in arr:
            item[0] -= center_mass[0]
            item[1] -= center_mass[1]

        # STEP 4: convert list of array into np.array
        shifted_arr = np.asarray(arr)
        shifted_arr = shifted_arr.transpose(1, 0)

        # STEP 5: rotate shifted array
        rotated_array = matrix_rt * shifted_arr
        rotated_array_list = rotated_array.tolist()

        # STEP 6: shift rotated positions back to old center mass
        for item in rotated_array_list:
            item[0] += center_mass[0]
            item[1] += center_mass[1]

        # STEP 7: find a new center mass of green area
        x_new, y_new = self.cm(rotated_array_list)
        center_mass_new = [260+x_new, 700-y_new]
        return center_mass_new

    def rotate_fin_pos_old_2(self, bor, pos,  degree_rt):
        matrix_rt = self.create_r_matrix(degree_rt)
        num_elem = len(bor.positions)
        sum_x = 0
        sum_y = 0
        temp = copy.deepcopy(bor.positions)
        for item in temp:
            sum_x += item[0]
            sum_y += item[1]
        x = int(round(sum_x / num_elem))
        y = int(round(sum_y / num_elem))
        center_mass = [x, y]

        arr = copy.deepcopy(bor.positions)
        arr = [list(item) for item in arr]
        for item in arr:
            item[0] -= center_mass[0]
            item[1] -= center_mass[1]

        new_arr = arr

        original_array = np.asarray(new_arr)
        original_array = original_array.transpose(1, 0)
        rotated_array = matrix_rt * original_array
        rotated_array_list = rotated_array.tolist()
        lng = rotated_array_list[0]
        lat = rotated_array_list[1]
        rotated = []
        for item_1, item_2 in zip(lng, lat):
            rotated.append([item_1, item_2])
        sum_x = 0
        sum_y = 0
        for item in rotated:
            sum_x += item[0]
            sum_y += item[1]
        x = int(round(sum_x / num_elem))
        y = int(round(sum_y / num_elem))
        center_mass = [x, y]
        back = (pos[0] - center_mass[0], pos[1] - center_mass[1])
        return back

    def shift_back(self, bor, arr):
        """Move all points back to initial center"""
        center_mass = self.find_map_cm(bor)
        for item in arr:
            item[0] += center_mass[0]
            item[1] += center_mass[1]
        return arr

    def shift_to_origin(self, bor, arr):
        """Move all points to origin(0, 0)"""
        center_mass = self.find_map_cm(bor)
        for item in arr:
            item[0] -= center_mass[0]
            item[1] -= center_mass[1]
        return arr

    def shift_to_origin_new(self, bor, arr):
        """Move all points to origin(0, 0)"""
        x = int(arr[0][0])
        y = int(arr[1][0])
        center_mass = self.cm(arr)
        center_mass = (x - center_mass[0], y - center_mass[1])
        return center_mass

    def map_center_mass(self, bor):
        """Find center mass of green-area(bor.not_painted)"""
        num_elem = len(bor.positions)
        xx = [x[0] for x in bor.positions]
        yy = [y[1] for y in bor.positions]
        ave_x = statistics.mean(xx)
        ave_y = statistics.mean(yy)
        x = int(round(ave_x / num_elem))
        y = int(round(ave_y / num_elem))
        return x, y

    def find_map_cm(self, bor):
        """Find center mass of green-area(bor.not_painted)"""
        num_elem = len(bor.temp_list)
        sum_x = 0
        sum_y = 0
        for item in bor.temp_list:
            sum_x += item[0]
            sum_y += item[1]
        x = int(round(sum_x / num_elem))
        y = int(round(sum_y / num_elem))
        return x, y

    def find_dist(self, current, final):
        """Return a distance"""
        return math.pow((final[0] - current[0]), 2) + math.pow((final[1] - current[1]), 2)

    def heuristic(self, start, goal):
        """Return squared value; distance with extract square root"""
        heuristic_val = (goal[0] - start[0]) ** 2 + (goal[1] - start[1]) ** 2
        return heuristic_val

    def set_max_min_vertexes(self, pos):
        """Reset two Critical vertexes of our boarder"""
        max_x = max(pos, key=lambda t: t[0])
        min_x = min(pos, key=lambda t: t[0])
        max_y = max(pos, key=lambda t: t[1])
        min_y = min(pos, key=lambda t: t[1])
        top_left = [min_x[0], min_y[1]]
        top_right = [max_x[0], min_y[1]]
        bottom_left = [min_x[0], max_y[1]]
        bottom_right = [max_x[0], max_y[1]]
        return top_left, top_right, bottom_right, bottom_left

    def neighbour_center_mass(self, pos, alpha, vel):
        radian = math.pi / 180.0
        if alpha > 0:
            if alpha < 90:
                beta = 90 - alpha
                x = vel * math.cos(radian * beta)
                y = -vel * math.sin(radian * beta)
            elif alpha < 180:
                betta = 180 - alpha
                gamma = 90 - betta
                x = vel * math.cos(gamma * radian)
                y = vel * math.sin(gamma * radian)
            elif alpha < 270:
                betta = 270 - alpha
                x = -vel * math.cos(betta * radian)
                y = vel * math.sin(betta * radian)
            elif alpha < 360:
                betta = 360 - alpha
                x = -vel * math.sin(betta * radian)
                y = -vel * math.cos(betta * radian)
        elif alpha < 0:
            alpha = -alpha
            if alpha < 90:
                beta = 90 - alpha
                x = -vel * math.cos(radian * beta)
                y = -vel * math.sin(radian * beta)
            elif alpha < 180:
                betta = 180 - alpha
                gamma = 90 - betta
                x = -vel * math.cos(gamma * radian)
                y = vel * math.sin(gamma * radian)
            elif alpha < 270:
                betta = 270 - alpha
                x = vel * math.cos(betta * radian)
                y = vel * math.sin(betta * radian)
            elif alpha < 360:
                betta = 360 - alpha
                x = vel * math.sin(betta * radian)
                y = -vel * math.cos(betta * radian)
        else:
            x = 0
            y = -vel
        return x, y

    def get_min_x(self, y):
        """Return a position P(x, y) with minimum x-coordinate for given y"""
        pattern = [item for item in self.green_zone if item[0] == y]
        mi_x = min(pattern, key=lambda t: t[1])
        min_x = (mi_x[1], mi_x[0])
        return min_x

    def get_max_x(self, y):
        """Return a position P(x, y) with maximum x-coordinate for given y"""
        pattern = [item for item in self.green_zone if item[0] == y]
        ma_x = max(pattern, key=lambda t: t[1])
        max_x = (ma_x[1], ma_x[0])
        return max_x

    def find_min_max_x(self):
        """This method used to find min and max position of rover center mass with given y-coordinate."""
        pattern = [item for item in self.green_zone if item[0] == self.current_y]
        mi_x = min(pattern, key=lambda t: t[1])
        ma_x = max(pattern, key=lambda t: t[1])
        mi_x = (mi_x[1], mi_x[0])
        ma_x = (ma_x[1], ma_x[0])
        return mi_x, ma_x

    def extrema_green_zone(self):
        """Initialize extrema points with minimum and maximum value of y-coordinate"""
        pattern = [item for item in self.green_zone]
        minimum = min(pattern, key=lambda t: t[0])
        self.min_y = minimum[0]
        maximum = max(pattern, key=lambda t: t[0])
        self.max_y = maximum[0]

    def find_all_extremum(self, y, gap_len):
        """Find all extremums on the same line"""
        pattern = [item for item in self.green_zone if item[0] == y]
        extremums = list()
        last, curr = pattern[0][1], None
        for item in pattern[1:]:
            curr = item[1]
            if curr - last >= gap_len:
                extremums.append((item[0], last))
                extremums.append(item)
            last = curr
        return extremums

    def get_min_y(self):
        return self.min_y

    def get_max_y(self):
        return self.max_y

    def get_current_y(self):
        return self.current_y
