# get a screenshot from window called '明日方舟 - MuMu模拟器'

import win32gui
import win32ui
import win32con
import win32api
import time
import os
from PIL import Image

from constants import *

class GameTime:
    def __init__(self, cost = None, tick = None):
        if cost is None or tick is None:
            screenshot = get_screenshot()
            cost = get_current_cost(screenshot)
            tick = get_current_tick(screenshot)
        # self.cost = cost
        # self.tick = tick
        # if tick >= MAX_TICK:
        self.cost = tick // MAX_TICK + cost
        self.tick = tick % MAX_TICK
        if self.cost < 0:
            self.cost = 0
            self.tick = 0

    def __str__(self):
        return 'cost: {}, tick: {}'.format(self.cost, self.tick)

    def __add__(self, other):
        # first check if other is a GameTime object
        if isinstance(other, GameTime):
            return GameTime(self.cost + other.cost, self.tick + other.tick)
        elif isinstance(other, int):
            return GameTime(self.cost, self.tick + other)
        else:
            raise TypeError('unsupported operand type(s) for +: \'GameTime\' and \'{}\''.format(type(other)))

    def __sub__(self, other):
        if isinstance(other, GameTime):
            return GameTime(self.cost - other.cost, self.tick - other.tick)
        elif isinstance(other, int):
            return GameTime(self.cost, self.tick - other)
        else:
            raise TypeError('unsupported operand type(s) for -: \'GameTime\' and \'{}\''.format(type(other)))
    
    def __lt__(self, other):
        if isinstance(other, GameTime):
            if self.cost < other.cost:
                return True
            elif self.cost == other.cost:
                return self.tick < other.tick
            else:
                return False
        else:
            raise TypeError('unsupported operand type(s) for <: \'GameTime\' and \'{}\''.format(type(other)))

    def __eq__(self, other):
        if isinstance(other, GameTime):
            return self.cost == other.cost and self.tick == other.tick
        else:
            raise TypeError('unsupported operand type(s) for ==: \'GameTime\' and \'{}\''.format(type(other)))

    def __gt__(self, other):
        return not self.__lt__(other) and not self.__eq__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)
    
    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)
    
    def __ne__(self, other):
        return not self.__eq__(other)


def get_screenshot():
    # 如果窗口被最小化，先将窗口解除最小化
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    MoniterDev = win32api.EnumDisplayMonitors(None, None)
    w = MoniterDev[0][2][2]
    h = MoniterDev[0][2][3]
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
    signedIntsArray = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer(
        'RGB',
        (saveBitMap.GetInfo()['bmWidth'], saveBitMap.GetInfo()['bmHeight']),
        signedIntsArray, 'raw', 'BGRX', 0, 1)
    # 释放内存
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    return img

# get the current cost in the game
def get_current_cost(screenshot = None):
    if screenshot is None:
        screenshot = get_screenshot()
    cost = screenshot.crop((COST_X1, COST_Y1, COST_X2, COST_Y2))
    # change all pixels ...
    for i in range(cost.size[0]):
        for j in range(cost.size[1]):
            if cost.getpixel((i, j)) < (200, 200, 200):
                cost.putpixel((i, j), (0, 0, 0))
            else:
                cost.putpixel((i, j), (255, 255, 255))
    
    # # raise dpi to exactly 300
    # cost = cost.resize((cost.size[0] * 5, cost.size[1] * 5), Image.ANTIALIAS)
    import pytesseract
    text = pytesseract.image_to_string(cost, lang='arknights_digit', config='--psm 6')
    print(text)
    # save the cost image (while testing)
    # cost.save('cost/cost9.png')
    # replace all sorts of misinterpretation, and remove all non-digit characters
    # text = text.replace('O', '0').replace('Q', '0').replace('@', '0').replace('©', '0')
    # text = text.replace('l', '1').replace('|', '1').replace('I', '1')
    # text = text.replace('S', '5').replace('B', '8').replace('Z', '2').replace('G', '6')
    text = ''.join([i for i in text if i.isdigit()])
    return int(text)

# get the current tick in the game
def get_current_tick(screenshot = None):
    if screenshot is None:
        screenshot = get_screenshot()
    costbar = screenshot.crop((COSTBAR_X1, COSTBAR_Y1, COSTBAR_X2, COSTBAR_Y2))
    # costbar.show()
    w, h = costbar.size
    pix = costbar.load()
    # count the number of white pixels
    white = 0
    for i in range(w):
        if pix[i, 0] > (200, 200, 200):
            white += 1
    return round(white / w * 29)

# pause the game: press space
def pause():
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_SPACE, 0)
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_SPACE, 0)

# change game speed: press the *2 button in the game
def change_speed():
    x = int(GAME_X1 + SPEED_X * (GAME_X2 - GAME_X1))
    y = int(GAME_Y1 + SPEED_Y * (GAME_Y2 - GAME_Y1))
    # send a left click message to the game window
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(x, y))
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(x, y))

# proceed to the next tick
# invariants:
# 1. the game is paused
# 2. the game is under bullet time
def proceed_one_tick():
    # helper function to proceed to the next tick
    def goto_next_tick():
        # wait for the game to proceed to the next tick
        curGameTime = GameTime()
        while GameTime() == curGameTime:
            pause()
            time.sleep(0.05)
            pause()
    
    goto_next_tick()


# pause at the specified cost and tick
# invariants:
# 1. the game is paused
# 2. the game is under speed 1
def pause_at(cost, tick):
    curGameTime = GameTime()
    tarGameTime = GameTime(cost, tick)

    is_paused = True
    bullet_time_entered = False

    if curGameTime < tarGameTime - STAGE1:
        # means we are still far from the target
        # proceed with speed 2

        # change speed to 2
        change_speed()
        time.sleep(0.1)
        # resume if paused
        if is_paused:
            pause()
            time.sleep(0.1)
            is_paused = False
        # wait until the game time is closer to the target
        while GameTime() < tarGameTime - STAGE1:
            time.sleep(0.1)
        # change speed back to 1
        change_speed()
    
    if curGameTime < tarGameTime - STAGE2:
        # means we are still a little away from the target
        # proceed with speed 1

        # resume if paused
        if is_paused:
            pause()
            time.sleep(0.1)
            is_paused = False
        # wait until the game time is closer to the target
        while GameTime() < tarGameTime - STAGE2:
            time.sleep(0.1)
    
    if curGameTime < tarGameTime - STAGE3:
        # means we are kind of close to the target
        # proceed with bullet time
        
        # switch to bullet time
        click_operator()
        bullet_time_entered = True
        time.sleep(0.1)
        # resume if paused
        if is_paused:
            pause()
            time.sleep(0.1)
            is_paused = False
        # wait until the game time is closer to the target
        while GameTime() < tarGameTime - STAGE3:
            time.sleep(0.1)

    if curGameTime < tarGameTime:
        # means we are very close to the target
        # proceed with one tick at a time
        
        # pause if not paused
        if not is_paused:
            pause()
            time.sleep(0.1)
            is_paused = True
        # switch to bullet time if not in bullet time
        if not bullet_time_entered:
            click_operator()
            bullet_time_entered = True
            time.sleep(0.1)
        # wait until the game time is closer to the target
        while GameTime() < tarGameTime:
            proceed_one_tick()
        # exit bullet time
        click_operator()


# click on the id-th operator
def click_operator(id = 1, oper_num = 11):
    # click on the id-th operator
    oper_x = int(GAME_X1 + (oper_num - id + 0.5) / oper_num * (GAME_X2 - GAME_X1))
    oper_y = int(GAME_Y1 + OPERATOR_Y * (GAME_Y2 - GAME_Y1))
    # send a left click message to the game window
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(oper_x, oper_y))
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(oper_x, oper_y))

# pause the game: press escape
def esc():
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0)
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_ESCAPE, 0)


# deploy the id-th operator
# invariants:
# 1. the game is paused
# 2. the game is under speed 1
def deploy_operator(tar_x, tar_y, dir, id = 1, oper_num = 11):
    # click on the id-th operator
    time.sleep(0.5)
    click_operator(id, oper_num)
    time.sleep(1)

    # resume
    pause()

    oper_x = int(GAME_X1 + (oper_num - id + 0.5) / oper_num * (GAME_X2 - GAME_X1))
    oper_y = int(GAME_Y1 + OPERATOR_Y * (GAME_Y2 - GAME_Y1))

    win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(oper_x, oper_y))
    time.sleep(0.05) # todo: how to make this more accurate?
    # move the mouse upward a little bit
    win32api.SendMessage(hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, win32api.MAKELONG(oper_x, oper_y - 20))

    # pause
    esc()

    # click on the target position
    time.sleep(0.5)
    win32api.SendMessage(hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, win32api.MAKELONG(tar_x, tar_y))
    time.sleep(0.5)
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(tar_x, tar_y))

    # pull to the target direction
    if dir == UP:
        delta_x = 0
        delta_y = -200
    elif dir == DOWN:
        delta_x = 0
        delta_y = 200
    elif dir == LEFT:
        delta_x = -200
        delta_y = 0
    elif dir == RIGHT:
        delta_x = 200
        delta_y = 0
    time.sleep(0.5)
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(tar_x, tar_y))
    time.sleep(0.5)
    win32api.SendMessage(hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, win32api.MAKELONG(tar_x + delta_x, tar_y + delta_y))
    time.sleep(0.5)
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(tar_x + delta_x, tar_y + delta_y))
    

if __name__ == "__main__":
    # make the window global
    hwnd = win32gui.FindWindow(None, "明日方舟 - MuMu模拟器")
    if hwnd == 0:
        print("未找到游戏窗口")
        exit()
    
    win32gui.SetForegroundWindow(hwnd)

    

    # gt = GameTime(3, -1) - -1
    # print(gt)

    # get_screenshot().crop((GAME_X1, GAME_Y1, GAME_X2, GAME_Y2)).show()

    # for i in range(1, 13):
    #     click_operator(i)
    #     time.sleep(1)
    # pause_at(50, 0)

    pause_at(16, 0)
    time.sleep(0.5)
    deploy_operator(1070, 570, LEFT, 2)
    time.sleep(0.5)
    pause_at(13, 5)
    time.sleep(0.5)
    deploy_operator(700, 510, RIGHT, 1)
    time.sleep(0.5)
    pause_at(4, 0)
    time.sleep(0.5)
    deploy_operator(945, 480, UP, 1)

    # get_current_cost()
    
