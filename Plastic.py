# get a screenshot from window called '明日方舟 - MuMu模拟器'

import win32gui
import win32ui
import win32con
import win32api
import time
import os
from PIL import Image

from constants import *
from GameTime import GameTime

class Plastic:

    hwnd = win32gui.FindWindow(None, "明日方舟 - MuMu模拟器")

    def __init__(self):
        # hwnd = win32gui.FindWindow(None, "明日方舟 - MuMu模拟器")
        if self.hwnd == 0:
            raise Exception("Cannot find window called '明日方舟 - MuMu模拟器'")
        win32gui.SetForegroundWindow(self.hwnd)

    def wait_between_keys(self):
        time.sleep(WAIT_BETWEEN_KEYS)
    def wait_for_feedback(self):
        time.sleep(WAIT_FOR_FEEDBACK)
    def take_a_nap(self):
        time.sleep(TAKE_A_NAP)

    # pause the game: press space
    def pause(self):
        win32api.SendMessage(self.hwnd, win32con.WM_KEYDOWN, win32con.VK_SPACE, 0)
        win32api.SendMessage(self.hwnd, win32con.WM_KEYUP, win32con.VK_SPACE, 0)

    # change game speed: press the *2 button in the game
    def change_speed(self):
        x = int(GAME_X1 + SPEED_X * (GAME_X2 - GAME_X1))
        y = int(GAME_Y1 + SPEED_Y * (GAME_Y2 - GAME_Y1))
        # send a left click message to the game window
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(x, y))
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(x, y))

    # proceed to the next tick
    # invariants:
    # 1. the game is paused
    # 2. the game is under bullet time
    def proceed_one_tick(self):
        # helper function to proceed to the next tick
        def goto_next_tick():
            # wait for the game to proceed to the next tick
            curGameTime = GameTime()
            while GameTime() == curGameTime:
                self.pause()
                self.wait_between_keys()
                self.pause()
                self.wait_for_feedback()
        
        goto_next_tick()


    # pause at the specified GameTime
    # invariants:
    # 1. the game is paused
    # 2. the game is under speed 1
    def pause_at(self, tarGameTime):
        curGameTime = GameTime()

        is_paused = True
        bullet_time_entered = False

        if curGameTime < tarGameTime - STAGE1:
            # means we are still far from the target
            # proceed with speed 2

            # change speed to 2
            self.change_speed()
            self.wait_between_keys()
            # resume if paused
            if is_paused:
                self.pause()
                self.wait_between_keys()
                is_paused = False
            # wait until the game time is closer to the target
            while GameTime() < tarGameTime - STAGE1:
                self.take_a_nap()
            # change speed back to 1
            self.change_speed()
            self.wait_between_keys()
        
        if curGameTime < tarGameTime - STAGE2:
            # means we are still a little away from the target
            # proceed with speed 1

            # resume if paused
            if is_paused:
                self.pause()
                self.wait_between_keys()
                is_paused = False
            # wait until the game time is closer to the target
            while GameTime() < tarGameTime - STAGE2:
                self.take_a_nap()
        
        if curGameTime < tarGameTime - STAGE3:
            # means we are kind of close to the target
            # proceed with bullet time
            
            # switch to bullet time
            self.click_operator()
            self.wait_between_keys()
            bullet_time_entered = True
            # resume if paused
            if is_paused:
                self.pause()
                self.wait_between_keys()
                is_paused = False
            # wait until the game time is closer to the target
            while GameTime() < tarGameTime - STAGE3:
                self.take_a_nap()
            self.wait_between_keys()

        if curGameTime < tarGameTime:
            # means we are very close to the target
            # proceed with one tick at a time
            
            # pause if not paused
            if not is_paused:
                self.pause()
                self.wait_between_keys()
                is_paused = True
            # switch to bullet time if not in bullet time
            if not bullet_time_entered:
                self.click_operator()
                self.wait_between_keys()
                bullet_time_entered = True
            # wait until the game time is closer to the target
            while GameTime() < tarGameTime:
                self.proceed_one_tick()
            # exit bullet time
            self.click_operator()
            self.wait_between_keys()
            bullet_time_entered = False

        if not is_paused:
            self.pause()
            self.wait_between_keys()
            is_paused = True
        if bullet_time_entered:
            self.click_operator()
            self.wait_between_keys()
            bullet_time_entered = False
        if curGameTime > tarGameTime:
            # give a warning
            print('Warning: pause_at goes past the target time: ' + str(tarGameTime))
        
        self.wait_for_feedback()

    # pause at the specified tick (another version of pause_at)
    def pause_at_CT(self, cost, tick):
        self.pause_at(GameTime(cost, tick))


    # click on the id-th operator
    def click_operator(self, id = 1, oper_num = 11):
        # click on the id-th operator
        oper_x = int(GAME_X1 + (oper_num - id + 0.5) / oper_num * (GAME_X2 - GAME_X1))
        oper_y = int(GAME_Y1 + OPERATOR_Y * (GAME_Y2 - GAME_Y1))
        # send a left click message to the game window
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(oper_x, oper_y))
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(oper_x, oper_y))

    # pause the game: press escape
    def esc(self):
        win32api.SendMessage(self.hwnd, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0)
        win32api.SendMessage(self.hwnd, win32con.WM_KEYUP, win32con.VK_ESCAPE, 0)


    # deploy the id-th operator
    # invariants:
    # 1. the game is paused
    # 2. the game is under speed 1
    # guaranteed to advance one tick
    def deploy_operator(self, tar_x, tar_y, dir, id = 1, oper_num = 11):
        beginTime = GameTime()

        while True:
            # click on the id-th operator
            self.click_operator(id, oper_num)
            self.wait_for_feedback()

            # resume
            self.pause()

            oper_x = int(GAME_X1 + (oper_num - id + 0.5) / oper_num * (GAME_X2 - GAME_X1))
            oper_y = int(GAME_Y1 + OPERATOR_Y * (GAME_Y2 - GAME_Y1))

            win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(oper_x, oper_y))
            self.wait_between_keys()
            # time.sleep(0.05) # todo: how to make this more accurate?
            # move the mouse upward a little bit
            win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, win32api.MAKELONG(oper_x, oper_y - 20))

            # pause
            self.esc()
            self.wait_for_feedback()

            # check if a tick has passed
            endTime = GameTime()
            if endTime > beginTime:
                if endTime > beginTime + 1:
                    print("Warning: more than one tick has passed when deploying operator at " + str(beginTime + 1))
                break
            else:
                win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(oper_x, oper_y))
                self.wait_for_feedback()

        # click on the target position
        win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, win32api.MAKELONG(tar_x, tar_y))
        self.wait_for_feedback()
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(tar_x, tar_y))

        # pull to the target direction
        drag_distance = int((GAME_Y2 - GAME_Y1) * DRAG)
        if dir == UP:
            delta_x = 0
            delta_y = -drag_distance
        elif dir == DOWN:
            delta_x = 0
            delta_y = drag_distance
        elif dir == LEFT:
            delta_x = -drag_distance
            delta_y = 0
        elif dir == RIGHT:
            delta_x = drag_distance
            delta_y = 0
        
        self.wait_for_feedback()
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(tar_x, tar_y))
        self.wait_between_keys()
        win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, win32api.MAKELONG(tar_x + delta_x, tar_y + delta_y))
        self.wait_between_keys()
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(tar_x + delta_x, tar_y + delta_y))
        self.wait_for_feedback()

    # retreat an operator
    # invariants:
    # 1. the game is paused
    # 2. the game is under speed 1
    # guaranteed to advance one tick
    def retreat_operator(self, tar_x, tar_y):
        beginTime = GameTime()

        # enter bullet time
        self.click_operator()
        self.wait_for_feedback()

        # resume
        self.pause()

        # click on the operator to retreat
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(tar_x, tar_y))
        self.wait_between_keys()
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(tar_x, tar_y))
        # now we are still in bullet time

        # pause
        self.esc()
        self.wait_for_feedback()

        curTime = GameTime()
        if curTime > beginTime:
            if curTime > beginTime + 1:
                print("Warning: more than one tick has passed when retreating operator at " + str(beginTime + 1))
        else:
            self.proceed_one_tick()
        
        # click on the retreat button
        retreat_x = int(GAME_X1 + (GAME_X2 - GAME_X1) * RETREAT_X)
        retreat_y = int(GAME_Y1 + (GAME_Y2 - GAME_Y1) * RETREAT_Y)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(retreat_x, retreat_y))
        self.wait_between_keys()
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(retreat_x, retreat_y))
        self.wait_for_feedback()

    # start an operator's skill
    # invariants:
    # 1. the game is paused
    # 2. the game is under speed 1
    # guaranteed to advance one tick
    def skill_operator(self, tar_x, tar_y):
        beginTime = GameTime()

        # enter bullet time
        self.click_operator()
        self.wait_for_feedback()

        # resume
        self.pause()

        # click on the operator to start skill
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(tar_x, tar_y))
        self.wait_between_keys()
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(tar_x, tar_y))
        # now we are still in bullet time

        # pause
        self.esc()
        self.wait_for_feedback()

        curTime = GameTime()
        if curTime > beginTime:
            if curTime > beginTime + 1:
                print("Warning: more than one tick has passed when starting skill of operator at " + str(beginTime + 1))
        else:
            self.proceed_one_tick()
        
        # click on the skill button
        skill_x = int(GAME_X1 + (GAME_X2 - GAME_X1) * SKILL_X)
        skill_y = int(GAME_Y1 + (GAME_Y2 - GAME_Y1) * SKILL_Y)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(skill_x, skill_y))
        self.wait_between_keys()
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(skill_x, skill_y))
        self.wait_for_feedback()





    # INTERFACE: deploy an operator
    # invariants:
    # 1. the game is paused
    # 2. the game is under speed 1
    def deploy(self, cost, tick, tar_x, tar_y, dir, id = 1, oper_num = 11):
        self.pause_at(GameTime(cost, tick) - 1)
        self.deploy_operator(tar_x, tar_y, dir, id, oper_num)


    # INTERFACE: retreat an operator
    # invariants:
    # 1. the game is paused
    # 2. the game is under speed 1
    def retreat(self, cost, tick, tar_x, tar_y):
        self.pause_at(GameTime(cost, tick) - 1)
        self.retreat_operator(tar_x, tar_y)

    # INTERFACE: start an operator's skill
    # invariants:
    # 1. the game is paused
    # 2. the game is under speed 1
    def skill(self, cost, tick, tar_x, tar_y):
        self.pause_at(GameTime(cost, tick) - 1)
        self.skill_operator(tar_x, tar_y)



# if __name__ == "__main__":
#     # make the window global
#     hwnd = win32gui.FindWindow(None, "明日方舟 - MuMu模拟器")
#     if hwnd == 0:
#         print("未找到游戏窗口")
#         exit()
    
#     win32gui.SetForegroundWindow(hwnd)

    

    # gt = GameTime(3, -1) - -1
    # print(gt)

    # get_screenshot().crop((GAME_X1, GAME_Y1, GAME_X2, GAME_Y2)).show()

    # for i in range(1, 13):
    #     click_operator(i)
    #     time.sleep(1)
    # pause_at(50, 0)

    # pause_at(16, 0)
    # time.sleep(0.5)
    # deploy_operator(1070, 570, LEFT, 4)
    # time.sleep(0.5)
    # pause_at(13, 5)
    # time.sleep(0.5)
    # deploy_operator(700, 510, RIGHT, 10)
    # time.sleep(0.5)
    # pause_at(4, 0)
    # time.sleep(0.5)
    # deploy_operator(945, 480, UP, 1)

    # proceed_one_tick()

    # get_current_cost()

    # retreat(9, 0, 1060, 344)

    # skill(15, 0, 1070, 570)
    
