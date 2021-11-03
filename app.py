import cv2
import cvui
import os
import numpy as np
import copy
import time

from canvas import Canvas
from rover import Rover
from mask import Mask
from border import Border
from support import Movement


class GUI:
    def __init__(self):
        # Flags used to define direction and ability move the rover
        self.MIN_FLAG = 'minimum'
        self.MAX_FLAG = 'maximum'
        self.FLAG_LR = 'from_left_to_right'
        self.FLAG_Rl = 'from_right_to_left'
        self.mouse_mode = [False]  # by default we cannot use mouse to define start position x and y coordinates
        self.border_side = [True]  # by default left side of border
        self.state = 0
        self.ready = False
        self.name = ''
        self.files = []

    def onmap(self, cursor_x, cursor_y):
        if 260 < cursor_x < 1600:
            if 50 < cursor_y < 900:
                return True
        return False

    def update_frame(self, canvas):
        canvas.mask.draw_map()
        cvui.update()
        cv2.imshow(canvas.mask.WINDOW_NAME, canvas.mask.frame)
        cv2.waitKey(1)

    def main(self, canvas):
        cvui.init(canvas.mask.WINDOW_NAME, 20)
        width = 175
        floatValueWidth = [12.]
        floatValueLength = [18.]
        floatValueDegree = [5.]
        floatValueRotation = [0.]
        x = 50
        cursor_position = cvui.Point()
        cursor_position_end = cvui.Point()
        while True:
            canvas.mask.frame[:] = (49, 52, 49)
            cvui.text(canvas.mask.frame, 50, 30, 'To exit this app press Q.')

            cvui.text(canvas.mask.frame, x, 350, 'Set Rover Width')
            cvui.trackbar(canvas.mask.frame, x, 375, width, floatValueWidth, 0, 20)
            canvas.rover.rover_width = round(floatValueWidth[0])
            cvui.text(canvas.mask.frame, x, 450, 'Set Rover Length')
            cvui.trackbar(canvas.mask.frame, x, 475, width, floatValueLength, 0, 20)
            canvas.rover.rover_length = round(floatValueLength[0])
            cvui.text(canvas.mask.frame, x, 550, 'Set Degree Cost ')
            cvui.trackbar(canvas.mask.frame, x, 575, width, floatValueDegree, 0, 20)
            canvas.degree_cost = round(floatValueDegree[0])

            cvui.text(canvas.mask.frame, x, 650, 'Set Rotation Degree')
            cvui.trackbar(canvas.mask.frame, x, 675, width, floatValueRotation, -180, 180)

            # Render a rectangle on the screen.
            cvui.rect(canvas.mask.frame, canvas.mask.rectangle.x, canvas.mask.rectangle.y,
                      canvas.mask.rectangle.width, canvas.mask.rectangle.height, 0xff0000)
            canvas.mask.background[:] = (100, 0, 0)
            img = canvas.mask.background

            localMap = canvas.mask.frame[canvas.mask.rectangle.y: canvas.mask.rectangle.y + 850,
                       canvas.mask.rectangle.x:canvas.mask.rectangle.x + 1300]
            localMap[:] = 100, 0, 0
            img[:] = (100, 0, 0)
            localMap[:] = img[:]

            cvui.checkbox(canvas.mask.frame, 50, 750, 'Mouse Active Mod', self.mouse_mode)
            cvui.checkbox(canvas.mask.frame, 50, 775, 'Select Border Side', self.border_side)

            # Check what is the current status of the mouse cursor
            status = cvui.iarea(canvas.mask.rectangle.x, canvas.mask.rectangle.y,
                                canvas.mask.rectangle.width, canvas.mask.rectangle.height)
            if status == cvui.CLICK: print('Rectangle was clicked!')
            if status == cvui.DOWN:  cvui.printf(canvas.mask.frame, 280, 800, "Mouse is: DOWN")
            if status == cvui.OVER:  cvui.printf(canvas.mask.frame, 280, 800, "Mouse is: OVER")
            if status == cvui.OUT:   cvui.printf(canvas.mask.frame, 280, 800, "Mouse is: OUT")

            if self.mouse_mode == [True]:
                if self.state == 0:
                    self.state = 1
                    print('initial cursor pos', cursor_position.x, cursor_position.y)
                elif 1 == self.state and cvui.mouse(cvui.CLICK) and self.onmap(cvui.mouse().x, cvui.mouse().y):
                    self.state = 2
                    cursor_position.x = cvui.mouse().x
                    cursor_position.y = cvui.mouse().y
                    print(f'start pos: {cursor_position.y}')
                elif 2 == self.state and cvui.mouse(cvui.CLICK) and self.onmap(cvui.mouse().x, cvui.mouse().y):
                    self.state = 0
                    cursor_position_end.x = cvui.mouse().x
                    cursor_position_end.y = cvui.mouse().y
                    print(f'end pos: {cursor_position_end.y}')
                    self.mouse_mode = [False]
                    self.ready = True

            # Show the coordinates of the mouse pointer on the screen
            cvui.printf(canvas.mask.frame, 280, 825, "Mouse position: (%d,%d)", cvui.mouse().x, cvui.mouse().y)

            if cvui.button(canvas.mask.frame, 50, 75, "        &Quit        "):
                break

            if cvui.button(canvas.mask.frame, 50, 125, " &Create CSV Files:  "):
                canvas.create_files()

            if cvui.button(canvas.mask.frame, 50, 175, " &Read CSV File:  "):
                name = 'rotation_0.csv'
                canvas.read_file(name)
                canvas.mask.copy_to_local_map(canvas)  # canvas.bor
                canvas.movement.green_zone = canvas.mask.copy_color_area(canvas.mask.mazeStatus, [0, 255, 0])
                canvas.movement.background = canvas.mask.copy_color_area(canvas.mask.mazeStatus, [100, 0, 0])
                canvas.movement.extrema_green_zone()  # canvas.movement.green_zone

            if cvui.button(canvas.mask.frame, 50, 225, "&Rotate the map:"):
                # files = []
                for file in os.listdir("."):
                    if file.endswith(".csv"):
                        self.files.append(file)

                if len(self.files) > 0:
                    temp = self.files[0]
                    self.files = self.files[1:]
                    self.files.append(temp)

                self.name = self.files[0]
                print(self.name)
                canvas.read_file(self.name)
                canvas.mask.copy_to_local_map(canvas)
                canvas.movement.green_zone = canvas.mask.copy_color_area(canvas.mask.mazeStatus, [0, 255, 0])
                canvas.movement.background = canvas.mask.copy_color_area(canvas.mask.mazeStatus, [100, 0, 0])

            # update all windows
            self.update_frame(canvas)


if __name__ == '__main__':
    border = Border()
    mask = Mask()
    rover = Rover()
    movement = Movement(rover)
    canvas = Canvas(border, mask, rover, movement)
    control = GUI()
    control.main(canvas)
