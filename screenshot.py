# get a screenshot from window called '明日方舟 - MuMu模拟器'

import win32gui
import win32ui
import win32con
import win32api
import time
import os
from PIL import Image

from constants import *

# def window_capture(filename):
#     # 窗口的类名可以用spy++工具获取
#     # 窗口的标题可以用win32gui工具获取

#     # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
#     hwndDC = win32gui.GetWindowDC(hwnd)
#     # 根据窗口的DC获取mfcDC
#     mfcDC = win32ui.CreateDCFromHandle(hwndDC)
#     # mfcDC创建可兼容的DC
#     saveDC = mfcDC.CreateCompatibleDC()
#     # 创建bigmap准备保存图片
#     saveBitMap = win32ui.CreateBitmap()
#     # 获取监控器信息
#     MoniterDev = win32api.EnumDisplayMonitors(None, None)
#     w = MoniterDev[0][2][2]
#     h = MoniterDev[0][2][3]
#     # print w,h　　　#图片大小
#     # 为bitmap开辟空间
#     saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
#     # 高度saveDC，将截图保存到saveBitmap中
#     saveDC.SelectObject(saveBitMap)
#     # 截取从左上角（0，0）长宽为（w，h）的图片
#     saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
#     saveBitMap.SaveBitmapFile(saveDC, filename)

def get_screenshot():
    # 如果窗口被最小化，先将窗口解除最小化
    # if win32gui.IsIconic(hwnd):
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

# truncate captured image: 1640, 680 to 1798, 750
# def truncate_image(image, x1, y1, x2, y2):
#     img = Image.open(filename)
#     img = img.crop((x1, y1, x2, y2))
#     img.save(new_filename)
#     return img

# OCR: get the number on the image
# def ocr_image(filename):
#     from PIL import Image
#     import pytesseract
#     img = Image.open(filename)
#     text = pytesseract.image_to_string(img)
#     # print(text)
#     # replace O with 0, l with 1, I with 1, S with 5, B with 8, Z with 2, Q with 0, G with 6, and remove all non-digit characters
#     text = text.replace('O', '0').replace('l', '1').replace('|', '1').replace('I', '1').replace('S', '5').replace('B', '8').replace('Z', '2').replace('Q', '0').replace('G', '6')
#     text = ''.join([i for i in text if i.isdigit()])
#     return text

# get the current cost in the game
def get_current_cost():
    cost = get_screenshot().crop((COST_X1, COST_Y1, COST_X2, COST_Y2))
    import pytesseract
    text = pytesseract.image_to_string(cost)
    # print(text)
    # replace O with 0, l with 1, I with 1, | with 1, S with 5, B with 8, Z with 2, Q with 0, G with 6, and remove all non-digit characters
    text = text.replace('O', '0').replace('l', '1').replace('|', '1').replace('I', '1').replace('S', '5').replace('B', '8').replace('Z', '2').replace('Q', '0').replace('G', '6')
    text = ''.join([i for i in text if i.isdigit()])
    return text

# get the current tick in the game
def get_current_tick():
    costbar = get_screenshot().crop((COSTBAR_X1, COSTBAR_Y1, COSTBAR_X2, COSTBAR_Y2))
    costbar.show()
    # get the width and height of the image
    w, h = costbar.size
    # get the pixel map
    pix = costbar.load()
    # count the number of white pixels
    white = 0
    for i in range(w):
        if pix[i, 0] > (200, 200, 200):
            white += 1
    return round(white / w * 29)

# press space in the game window
def press_space():
    # find the window
    # hwnd = win32gui.FindWindow(None, "明日方舟 - MuMu模拟器")
    # print(hwnd)
    # press the button IN THE WINDOW
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_SPACE, 0)
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_SPACE, 0)

if __name__ == "__main__":
    # make the window global
    hwnd = win32gui.FindWindow(None, "明日方舟 - MuMu模拟器")
    if hwnd == 0:
        print("未找到游戏窗口")
        exit()
    
    win32gui.SetForegroundWindow(hwnd)
    
    # get_screenshot().show()
    # print(get_current_tick())
    # window_capture("capture.png")
    # truncate_image("capture.png", "cost.png", COST_X1, COST_Y1, COST_X2, COST_Y2)
    # truncate_image("capture.png", "costbar.png", COSTBAR_X1, COSTBAR_Y1, COSTBAR_X2, COSTBAR_Y2)
    press_space()
    # S = {}
    # while len(S) < 30:
    #     window_capture("test.png")
    #     get_cost_image("test.png", "cost.png")
    #     get_cost_bar_image("test.png", "cost_bar.png")
    #     # use absolute path
    #     print(ocr_image("D:\\projects\\cost.png"))
    #     (num, tick) = get_cost_bar_percentage("D:\\projects\\cost_bar.png")
    #     S[num] = 1
    #     print(tick)
    #     print(round(tick * 29))
    #     press_space()
    #     time.sleep(0.1)
    #     press_space()
    # S = sorted(list(S))
    # print(S)
    # press_esc()
    # wait for 0.1 second
    # 
    # press_space()

