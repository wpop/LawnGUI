import xlrd
import numpy as np
import math
import copy

from bresenham import bresenham


class Border:
    def __init__(self):
        self.file_name = "GPS_Map_1.xlsx"
        self.latitudes = []
        self.longitudes = []
        self.lng_pos_map = []  # obstacle x
        self.lat_pos_map = []  # obstacle y
        self.positions = None
        self.difference_lat = None
        self.difference_lng = None
        self.lat_min = None
        self.lng_min = None
        self.lat_max = None
        self.lng_max = None
        self.MULTFACTOR = math.pow(10, 7)
        self.width_map = 1300
        self.height_map = 850
        self.map = np.zeros((self.height_map, self.width_map, 3), np.uint8)  # 3d-array
        self.maze = np.ones((850, 1300), np.uint8)
        self.maze_not_painted = []
        self.not_painted = []
        self.temp_list = []

    def read_data(self):
        """Read GPS Data from .xlsx file"""
        wb = xlrd.open_workbook(self.file_name)
        sheet = wb.sheet_by_index(0)
        sheet.cell_value(0, 0)
        for i in range(5, sheet.nrows):
            self.latitudes.append(sheet.cell_value(i, 3))
            self.longitudes.append(sheet.cell_value(i, 4))

    def refactor(self):
        """Multiply latitudes by 10^8; "Multiply longitudes by 10^7"""
        latitude, longitude = [], []
        for (lat, lng) in zip(self.latitudes, self.longitudes):
            latitude.append(round(self.MULTFACTOR * lat))
            longitude.append(round(self.MULTFACTOR * lng))
        self.latitudes = copy.copy(latitude)
        self.longitudes = copy.copy(longitude)

    def find_difference(self):
        self.lat_min = min(self.latitudes)
        self.lat_max = max(self.latitudes)
        self.difference_lat = self.lat_max - self.lat_min
        self.lng_min = min(self.longitudes)
        self.lng_max = max(self.longitudes)
        self.difference_lng = self.lng_max - self.lng_min

    def rescale(self):
        """Find pixel by santimeter rate"""
        self.rate_lat = 1.5  # self.difference_lat#/self.height_map
        self.rate_lng = 1.5  # self.difference_lng#/self.height_map

    def subtract_origin(self):
        lats, lngs = [], []
        origin_lat = self.lat_min
        origin_lng = self.lng_min
        for (lat, lng) in zip(self.latitudes, self.longitudes):
            current_lat = lat - origin_lat
            current_lng = lng - origin_lng
            lats.append(round(current_lat/self.rate_lat))
            lngs.append(round(current_lng/self.rate_lng * math.cos(origin_lat/10000000*math.pi/180.0)))
        self.lat_pos_map = copy.copy(lats)
        self.lng_pos_map = copy.copy(lngs)
        self.positions = list(zip(self.lng_pos_map, self.lat_pos_map))

    def find_dist(self, pos_1, pos_2):
        dist = math.sqrt(math.pow((pos_1[0] - pos_2[0]), 2) + math.pow((pos_1[1] - pos_2[1]), 2))
        return dist

    def create_border_list(self):
        """Create Map as a list with border without duplications"""
        start_pos = self.positions[0]
        indexes = []  # list of position indexes
        distances = []
        for indx, item in enumerate(self.positions):
            if 0 == indx:
                pass
            else:
                dist = self.find_dist(start_pos, item)
                indexes.append(indx)
                distances.append(round(dist))
        min_dist = min(distances)
        start_pos = self.positions[0]
        reduced_pos_list = [start_pos]
        reduced_dist_list = []
        count_min_dist = 0
        new_index_list = []
        for indx, item in enumerate(self.positions):
            if 0 == indx:
                pass
            else:
                dist = round(self.find_dist(start_pos, item))
                if dist == min_dist:
                    count_min_dist += 1
                if count_min_dist >= 1 and count_min_dist < 3:
                    reduced_pos_list.append(item)
                    new_index_list.append(indx)
                    reduced_dist_list.append(dist)
        start_pos = reduced_pos_list[0]
        self.positions = reduced_pos_list[1:]
        bresenham_list = []

        # Using Bresenham algorithm to convert Math line into Raster line
        for pos in reduced_pos_list:
            lb = list(bresenham(start_pos[0], start_pos[1], pos[0], pos[1]))
            bresenham_list.append(lb)
            start_pos = pos

        # convert list of lists into one list
        flat_list = [item for sublist in bresenham_list for item in sublist]

        # Eliminate duplicates
        flat_list = list(set(flat_list))
        dt = np.dtype('int,int')

        # convert to np.array
        flat_list = np.asarray(flat_list, dt)
        for item in flat_list:
            self.maze[(item[0] - 1):(item[0] + 1), (item[1] - 1):(item[1] + 1)] = 0

        new_positions = np.asarray(reduced_pos_list, dtype=np.int32)
        shape = new_positions.shape
        positions = new_positions.reshape((1, shape[0], shape[1]))
        self.not_painted = copy.copy(positions)
        for raw in self.not_painted:
            for item in raw:
                item[0] = item[0] + 300
                item[1] = 700 - item[1]

        temp = self.not_painted.reshape((336, 2))
        temp_list = temp.tolist()
        self.temp_list = copy.copy(temp_list)

    def create_border(self):
        start_pos = self.positions[0]
        indexes = []  # list of position indexes
        distances = []
        for indx, item in enumerate(self.positions):
            if 0 == indx:
                pass
            else:
                dist = classmethod.find_dist(start_pos, item)
                indexes.append(indx)
                distances.append(round(dist))
        min_dist = min(distances)
        start_pos = self.positions[0]
        reduced_pos_list = [start_pos]
        reduced_dist_list = []
        count_min_dist = 0
        new_index_list = []
        for indx, item in enumerate(self.positions):
            if 0 == indx:
                pass
            else:
                dist = round(self.find_dist(start_pos, item))
                if dist == min_dist:
                    count_min_dist += 1
                if count_min_dist >= 1 and count_min_dist < 3:
                    reduced_pos_list.append(item)
                    new_index_list.append(indx)
                    reduced_dist_list.append(dist)
        start_pos = reduced_pos_list[0]
        self.positions = reduced_pos_list[1:]
        bresenham_list = []

        # Using Bresenham algorithm to convert Math line into Raster line
        for pos in reduced_pos_list:
            lb = list(bresenham(start_pos[0], start_pos[1], pos[0], pos[1]))
            bresenham_list.append(lb)
            start_pos = pos

        # convert list of lists into one list
        flat_list = [item for sublist in bresenham_list for item in sublist]

        # Eliminate duplicates
        flat_list = list(set(flat_list))
        dt = np.dtype('int,int')

        # convert to np.array
        flat_list = np.asarray(flat_list, dt)
        for item in flat_list:
            self.maze[(item[0] - 1):(item[0] + 1), (item[1] - 1):(item[1] + 1)] = 0

        new_positions = np.asarray(reduced_pos_list, dtype=np.int32)
        shape = new_positions.shape
        positions = new_positions.reshape((1, shape[0], shape[1]))
        self.not_painted = copy.copy(positions)
        for raw in self.not_painted:
            for item in raw:
                item[0] = item[0] + 300
                item[1] = 700 - item[1]

    def prepare_map_data(self):
        self.read_data()
        self.refactor()
        self.find_difference()
        self.rescale()
        self.subtract_origin()
        self.create_border_list()
