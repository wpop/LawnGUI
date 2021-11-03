import cvui
import copy
import cv2
import math
import numpy as np


class Mask:
    def __init__(self, height=950, width=1600):
        self.WINDOW_NAME = 'Create a local map'
        self.height = height
        self.width = width
        self.width_map = 1300
        self.height_map = 850

        # The whole GUI
        self.frame = np.zeros((self.height, self.width, 3), np.uint8)

        # Black frame and blue map with green area
        self.mazeStatus = np.zeros((self.height, self.width, 3), np.uint8)

        # Black and white pattern of my map
        self.mazeStatusMask = np.zeros((self.height, self.width), np.uint8)

        # opencv primitive cut my map from frame by move it to x->260 pixels, y->50pixels:
        self.rectangle = cvui.Rect(260, 50, 1300, 850)

        # My blue map inside of GUI frame with green area
        self.background = np.zeros((self.height_map,  self.width_map, 3), np.uint8)

        self.color = [(0, 255, 255), (0, 200, 255)]  # first to right, second to left
        self.set_background((100, 0, 0))  # keep a copy

        self.copied_maze = copy.deepcopy(self.mazeStatus)
        self.copied_bg = copy.deepcopy(self.background)

    def reset(self, canvas):
        cv2.rectangle(self.mazeStatusMask, (260, 50), (1300, 850), 255, -1)
        cv2.copyTo(self.mazeStatus, self.mazeStatusMask, self.frame)
        localMap = self.mazeStatus[self.rectangle.y: self.rectangle.y + 850, self.rectangle.x:self.rectangle.x + 1300]
        localMap[:] = self.background[:]

    def set_background(self, color):
        """Swap black color to a new color"""
        self.mazeStatus[:] = color

    def copy_to_local_map(self, canvas):
        temp = np.asarray(canvas.bor.positions)
        r, c = temp.shape
        temp_3d = np.reshape(temp, (1, r, c))
        canvas.bor.not_painted = copy.copy(temp_3d)
        canvas.bor.not_painted = temp_3d

        for raw in canvas.bor.not_painted:
            for item in raw:
                canvas.bor.maze_not_painted.append([item[0] + 260, item[1] + 50])
        cv2.fillPoly(self.background, canvas.bor.not_painted, (0, 255, 0))

        localMap = self.mazeStatus[self.rectangle.y: self.rectangle.y + 850, self.rectangle.x:self.rectangle.x + 1300]
        localMap[:] = self.background[:]

    def copy_color_area(self, arr, color):
        """Extract location vertices with given color"""
        arr_color = np.where(np.all(arr == color, axis=-1))
        location_color = list(zip(arr_color[0], arr_color[1]))
        return location_color

    def is_walkable(self,
                    move,    # object of class Movement
                    rover,   # object of class Rover
                    pos,     # current position of center mass
                    alpha):  # current direction in degrees
        """Is it possible to move the rover in this position"""
        solution_lt = rover.find_rover_upset(pos, alpha)
        solution_lt = solution_lt[:-2]
        solution = [list(elem) for elem in solution_lt]
        places_np = np.asarray([solution])
        mask_rov = np.zeros((900, 1600), np.uint8)
        cv2.fillPoly(mask_rov, np.int32(places_np), 250)
        top_left, top_right, bottom_right, bottom_left = move.set_max_min_vertexes(solution_lt)
        positions = []
        positions.append(top_left)
        positions.append(top_right)
        positions.append(bottom_right)
        positions.append(bottom_left)
        min_x = min(positions, key=lambda t: t[0])
        max_x = max(positions, key=lambda t: t[0])
        max_y = max(positions, key=lambda t: t[1])
        min_y = min(positions, key=lambda t: t[1])
        start_x = min_x[0]
        start_y = min_y[1]
        end_x = max_x[0]
        end_y = max_y[1]
        mask_rov = mask_rov[start_y:end_y, start_x:end_x]
        frame = self.mazeStatus[start_y:end_y, start_x:end_x]
        dst = cv2.bitwise_and(frame, frame, mask=mask_rov)
        state = np.any(dst[:, :, 0] == 100)
        if state:
            return False
        else:
            return True

    def get_vertex_neighbours(self, move, rover, pos):
        vel = move.step
        local_neighbors = []
        for degree in move.circular_sector:
            dx, dy = move.neighbour_center_mass(pos, degree, vel)
            x = pos[0]+dx
            y = pos[1]+dy
            degree = degree - rover.get_angle()
            if degree > 180:
                alpha = degree - 360
            else:
                alpha = degree
            if alpha > 360 or alpha < -360:
                print(f'alpha = {alpha}')
                print('\n' * 2)
            distance = math.sqrt(math.pow(pos[0]-x, 2) + math.pow(pos[1]-y, 2))
            if self.is_walkable(move, rover, pos, alpha):
                local_neighbors.append((int(round(x)), int(round(y)), alpha, int(round(distance))))
        return local_neighbors

    def draw_map(self):
        # draw grean area on the map
        cv2.rectangle(self.mazeStatusMask, (260, 50), (1300, 850), 255, -1)
        cv2.copyTo(self.mazeStatus, self.mazeStatusMask, self.frame)
        cv2.imshow(self.WINDOW_NAME, self.frame)

    def draw_rover_path(self,
                        rover,
                        road,  # object of class WSTAR
                        line_parity,  # instance of class Planning
                        apath):
        if line_parity:
            path_color = self.color[0]
        else:
            path_color = self.color[1]
        if apath is not None:
            rov_positions = []
            cm = []
            road.path.extend(apath)
            for item, degree in apath:
                rov_data = rover.find_rover_upset(item, degree)
                rov_positions.append(rov_data[:-2])
                cm.append(rov_data[-2])

            for item in rov_positions:
                places_np = np.asarray([item])
                cv2.fillPoly(self.mazeStatus, np.int32(places_np), path_color)
            for item in cm:
                cv2.circle(self.mazeStatus, (int(item[0]), int(item[1])), 0, (200, 0, 0), -1)

            self.draw_map()
            cvui.update()
            cv2.imshow(self.WINDOW_NAME, self.frame)
            cv2.waitKey(1)
