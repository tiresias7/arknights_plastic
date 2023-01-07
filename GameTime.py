import win32gui
import win32ui
import win32con
import win32api
from PIL import Image

from constants import *

class GameTime:
    hwnd = win32gui.FindWindow(None, "明日方舟 - MuMu模拟器")

    def get_screenshot(self):
        # 如果窗口被最小化，先将窗口解除最小化
        if win32gui.IsIconic(self.hwnd):
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        hwndDC = win32gui.GetWindowDC(self.hwnd)
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
        win32gui.ReleaseDC(self.hwnd, hwndDC)
        return img

    # get the current cost in the game
    def get_current_cost(self, screenshot = None):
        if screenshot is None:
            screenshot = self.get_screenshot()
        cost = screenshot.crop((COST_X1, COST_Y1, COST_X2, COST_Y2))
        # change the color of the cost picture to black and white
        for i in range(cost.size[0]):
            for j in range(cost.size[1]):
                if cost.getpixel((i, j)) < (200, 200, 200):
                    cost.putpixel((i, j), (0, 0, 0))
                else:
                    cost.putpixel((i, j), (255, 255, 255))
        
        import pytesseract
        text = pytesseract.image_to_string(cost, lang='arknights_digit', config='--psm 6')
        # print(text)
        text = ''.join([i for i in text if i.isdigit()])
        return int(text)

    # get the current tick in the game
    def get_current_tick(self, screenshot = None):
        if screenshot is None:
            screenshot = self.get_screenshot()
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

    def __init__(self, cost = None, tick = None):
        if cost is None or tick is None:
            screenshot = self.get_screenshot()
            cost = self.get_current_cost(screenshot)
            tick = self.get_current_tick(screenshot)
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

    def get_cost(self):
        return self.cost
    
    def get_tick(self):
        return self.tick
