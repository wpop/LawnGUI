import copy
import numpy as np
import csv
import os
import re


class Canvas:
    def __init__(self, border, mask, rover, movement): #, rover, movement, path, plan, test):
        self.bor = border
        self.mask = mask
        self.rover = rover
        self.movement = movement
        self.flag_paint = True   # Activate rover to paint
        self.line_parity = True  # Parity equals to True when rover move from the left to the right

    @staticmethod
    def atoi(text):
        return int(text) if text.isdigit() else text

    @staticmethod
    def natural_keys(text):
        """alist.sort(key=natural_keys) sorts in human order"""
        return [Canvas.atoi(c) for c in re.split(r'(\d+)', text)]

    def create_files(self):
        """This method creates files with rotated ot_painted data"""
        self.bor.prepare_map_data()
        for degree in self.movement.circular_sector:
            original_pos = copy.deepcopy(self.bor.temp_list)
            rot = self.movement.create_r_matrix(degree)
            data = self.movement.rotation(self.bor, rot, original_pos)
            file_name = 'rotation_' + str(degree) + '.csv'
            # Save Numpy array to csv
            np.savetxt(file_name, data, delimiter=',', fmt='%s')

    def read_all_files(self):
        """Read all rotaation_n.csv files to test movement with different degrees"""
        dir_path = os.path.dirname(os.path.realpath(__file__))
        files_sorted = []
        with os.scandir(dir_path) as entries:
            for entry in entries:
                print("-.-" * 20, entry)
                if entry.name.endswith(".csv"):
                    files_sorted.append(entry.name)
        files_sorted.sort(key=Canvas.natural_keys)  # key=natural_keys
        return files_sorted

    def read_file(self, file_name):
        positions = []
        indx = 0
        with open(file_name) as csvfile:
            read_csv = csv.reader(csvfile, delimiter=',')
            for row in read_csv:
                lng = int(round(float(row[0])))
                lat = int(round(float(row[1])))
                positions.append((lng, lat))
                indx += 1
            self.bor.positions = positions