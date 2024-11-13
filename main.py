# Windows API example windows
"""
theForger's excellent Win32 API Tutorial: http://www.winprog.org/tutorial/
Microsoft official documentation: 
https://learn.microsoft.com/en-us/windows/win32/api/winuser/
Useful tutorial:
https://learn.microsoft.com/en-us/windows/win32/learnwin32/your-first-windows-program
Helpful example (constants were taken from here for convienience)
https://gist.github.com/syegulalp/7cf217677e893881a18d10020f2966e4
"""
from ctypes import c_int, c_uint, WinDLL, Structure, pointer, byref
from ctypes import WINFUNCTYPE, sizeof, windll
from ctypes.wintypes import HANDLE, LPCWSTR, LPARAM, WPARAM, HWND, MSG

# globals
WS_EX_APPWINDOW = 0x40000
WS_OVERLAPPEDWINDOW = 0xcf0000
WS_CAPTION = 0xc00000
SW_SHOWNORMAL = 1
SW_SHOW = 5
CS_HREDRAW = 2
CS_VREDRAW = 1
CW_USEDEFAULT = 0x80000000
WM_DESTROY = 2
WHITE_BRUSH = 0

user32 = WinDLL('user32', use_last_error=True)
gdi32 = WinDLL('gdi32', use_last_error=True)
kernel32 = WinDLL('kernel32', use_last_error=True)

WNDPROCTYPE = WINFUNCTYPE(c_int, HWND, c_uint, WPARAM, LPARAM)
user32.DefWindowProcW.argtypes = [HWND, c_uint, WPARAM, LPARAM]


class WNDCLASSEX(Structure):
    # This is not an ordinary python class!
    # It represents the "struct" type in c.
    # This is how we work with c structs in when using ctypes

    _fields_ = [("cbSize", c_uint),
                ("style", c_uint),
                ("lpfnWndProc", WNDPROCTYPE),
                ("cbClsExtra", c_int),
                ("cbWndExtra", c_int),
                ("hInstance", HANDLE),
                ("hIcon", HANDLE),
                ("hCursor", HANDLE),
                ("hBrush", HANDLE),
                ("lpszMenuName", LPCWSTR),
                ("lpszClassName", LPCWSTR),
                ("hIconSm", HANDLE)]


def messagebox(text: str, title: str) -> int:
    """
    This is a nice simple wrapper for the MessageBox function from User32.dll
    Note that I am using MessageBoxW.
    The W suffix in these windows stands for Wide (unicode) strings
    If we were using c the macros and compiler will take care of everything
    Since we are directly calling the functions directly,
    we need to be careful not to pass a unicode (LPCWSTR)
    string to a function expecting ansi (PCSTR)

    Returns int for the messagebox status, although it's probably useless here
    """
    return user32.MessageBoxW(None, text, title, 0)


# okay let's create a proper class for the window with sane defaults

class PythonWindow:
    def __init__(self, wndClass, classname, callback_f, inst: LPARAM):
        self.wndClass = wndClass
        self.classname = classname
        self.callback_f = callback_f
        self.inst = inst
        self.hWnd = None

    def setupWindow(self):
        self.wndClass.cbSize = sizeof(WNDCLASSEX)
        self.wndClass.style = CS_HREDRAW | CS_VREDRAW
        self.wndClass.lpfnWndProc = self.callback_f
        self.wndClass.cbClsExtra = 0
        self.wndClass.cbWndExtra = 0
        self.wndClass.hInstance = self.inst
        self.wndClass.hIcon = 0
        self.wndClass.hCursor = 0
        self.wndClass.hBrush = gdi32.GetStockObject(WHITE_BRUSH)
        self.wndClass.lpszMenuName = 0
        self.wndClass.lpszClassName = self.classname
        self.wndClass.hIconSm = 0
        user32.RegisterClassExW(byref(self.wndClass))

    def createWindow(self, window_name: str, x: int, y: int, width: int, height: int):
        self.hWnd = windll.user32.CreateWindowExW(
            0, self.classname, window_name,
            WS_OVERLAPPEDWINDOW | WS_CAPTION,
            x, y,
            width, height, 0, 0, self.inst, 0)
        if not self.hWnd:
            print('Failed to create window')
            exit(0)
        return self.hWnd

    def showWindow(self):
        user32.ShowWindow(self.hWnd, SW_SHOWNORMAL)
        user32.UpdateWindow(self.hWnd)
        return self.hWnd

    def run(self, msg: MSG):
        while user32.GetMessageW(byref(msg), 0, 0, 0) != 0:
            user32.TranslateMessage(byref(msg))
            user32.DispatchMessageW(byref(msg))
        return


def win_callback(hWnd: HWND, Msg: MSG, wParam: WPARAM, lParam: LPARAM):
    if Msg == WM_DESTROY:
        user32.PostQuitMessage(0)
        return 0
    return user32.DefWindowProcW(hWnd, Msg, wParam, lParam)


def main():
    WndProc = WNDPROCTYPE(win_callback)
    hInst = kernel32.GetModuleHandleW(0)
    wndClass = WNDCLASSEX()
    wndclassname = "my window class"
    # Use the class
    window = PythonWindow(wndClass, wndclassname, WndProc, hInst)
    window.setupWindow()
    window.createWindow("hello, I'm a window!", 0, 0, 800, 600)
    window.showWindow()
    msg = MSG()
    window.run(msg)

    _ = messagebox("Goodbye!", "I'm a messagebox!")


if __name__ == "__main__":
    main()
