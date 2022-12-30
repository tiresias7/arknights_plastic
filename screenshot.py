# get a screenshot from window called '明日方舟 - MuMu模拟器'

import win32gui
import win32ui
import win32con
import win32api
import time
import os

def window_capture(filename):
    hwnd = 0
    # 窗口的类名可以用spy++工具获取
    # 窗口的标题可以用win32gui工具获取
    hwnd = win32gui.FindWindow(None, "明日方舟 - MuMu模拟器")
    if hwnd != 0:
        # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
        hwndDC = win32gui.GetWindowDC(hwnd)
        # 根据窗口的DC获取mfcDC
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        # mfcDC创建可兼容的DC
        saveDC = mfcDC.CreateCompatibleDC()
        # 创建bigmap准备保存图片
        saveBitMap = win32ui.CreateBitmap()
        # 获取监控器信息
        MoniterDev = win32api.EnumDisplayMonitors(None, None)
        w = MoniterDev[0][2][2]
        h = MoniterDev[0][2][3]
        # print w,h　　　#图片大小
        # 为bitmap开辟空间
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
        # 高度saveDC，将截图保存到saveBitmap中
        saveDC.SelectObject(saveBitMap)
        # 截取从左上角（0，0）长宽为（w，h）的图片
        saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
        saveBitMap.SaveBitmapFile(saveDC, filename)

# truncate captured image: 1640, 680 to 1798, 750
def truncate_image(filename):
    from PIL import Image
    img = Image.open(filename)
    img = img.crop((1640, 680, 1798, 750))
    img.save(filename)

# get the cost part of the image: 1700, 680 to 1780, 740
def get_cost_image(filename, new_filename):
    from PIL import Image
    img = Image.open(filename)
    img = img.crop((1690, 680, 1790, 740))
    img.save(new_filename)

# get the cost bar of the image: 1640, 745 to 1798, 749
def get_cost_bar_image(filename, new_filename):
    from PIL import Image
    img = Image.open(filename)
    img = img.crop((1641, 745, 1798, 749))
    img.save(new_filename)

# OCR: get the number on the image
def ocr_image(filename):
    from PIL import Image
    import pytesseract
    img = Image.open(filename)
    text = pytesseract.image_to_string(img)
    # print(text)
    # replace O with 0, l with 1, I with 1, S with 5, B with 8, Z with 2, Q with 0, G with 6, and remove all non-digit characters
    text = text.replace('O', '0').replace('l', '1').replace('|', '1').replace('I', '1').replace('S', '5').replace('B', '8').replace('Z', '2').replace('Q', '0').replace('G', '6')
    text = ''.join([i for i in text if i.isdigit()])
    return text

# get the percentage of the white part of the cost bar
def get_cost_bar_percentage(filename):
    from PIL import Image
    import pytesseract
    img = Image.open(filename)
    # get the width and height of the image
    w, h = img.size
    print(w, h)
    # get the pixel map
    pix = img.load()
    # count the number of white pixels
    white = 0
    for i in range(w):
        for j in range(h):
            if pix[i, j] > (200, 200, 200):
                white += 1
    print(white)
    return (white, white / (w * h))

# press the pause button of the game, located at 1700, 100
def press_pause_button():
    # find the window
    hwnd = win32gui.FindWindow(None, "明日方舟 - MuMu模拟器")
    print(hwnd)
    # press the button IN THE WINDOW
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, 1700 + 65536 * 100)
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, 1700 + 65536 * 100)

# press space in the game window
def press_space():
    # find the window
    hwnd = win32gui.FindWindow(None, "明日方舟 - MuMu模拟器")
    # print(hwnd)
    # press the button IN THE WINDOW
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_SPACE, 0)
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_SPACE, 0)

# press esc in the game window
def press_esc():
    # find the window
    hwnd = win32gui.FindWindow(None, "明日方舟 - MuMu模拟器")
    # press the button IN THE WINDOW
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0)
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_ESCAPE, 0)
    
if __name__ == "__main__":
    S = {}
    while len(S) < 30:
        window_capture("test.png")
        get_cost_image("test.png", "cost.png")
        get_cost_bar_image("test.png", "cost_bar.png")
        # use absolute path
        print(ocr_image("D:\\projects\\cost.png"))
        (num, tick) = get_cost_bar_percentage("D:\\projects\\cost_bar.png")
        S[num] = 1
        print(tick)
        print(round(tick * 29))
        press_space()
        time.sleep(0.1)
        press_space()
    S = sorted(list(S))
    print(S)
    # press_esc()
    # wait for 0.1 second
    # 
    # press_space()

