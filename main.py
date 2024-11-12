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


def win_callback(hWnd, Msg, wParam, lParam):
    if Msg == WM_DESTROY:
        user32.PostQuitMessage(0)
        return 0
    return user32.DefWindowProcW(hWnd, Msg, wParam, lParam)


# Todo: put this in a proper class
def setupWindow(wndClass: WNDCLASSEX, classname: str, callback_f, inst):
    """
    This just sets up the window with mostly default values
    """
    wndClass.cbSize = sizeof(WNDCLASSEX)
    wndClass.style = CS_HREDRAW | CS_VREDRAW
    wndClass.lpfnWndProc = callback_f
    wndClass.cbClsExtra = 0
    wndClass.cbWndExtra = 0
    wndClass.hInstance = inst
    wndClass.hIcon = 0
    wndClass.hCursor = 0
    wndClass.hBrush = gdi32.GetStockObject(WHITE_BRUSH)
    wndClass.lpszMenuName = 0
    wndClass.lpszClassName = classname
    wndClass.hIconSm = 0


def main():
    WndProc = WNDPROCTYPE(win_callback)
    hInst = kernel32.GetModuleHandleW(0)
    wndClass = WNDCLASSEX()
    wndclassname = "my window class"
    window_name = "window"
    setupWindow(wndClass, wndclassname,
                WndProc, hInst)
    user32.RegisterClassExW(byref(wndClass))

    hWnd = windll.user32.CreateWindowExW(
        0, wndclassname, window_name,
        WS_OVERLAPPEDWINDOW | WS_CAPTION,
        CW_USEDEFAULT, CW_USEDEFAULT,
        300, 300, 0, 0, hInst, 0)

    if not hWnd:
        print('Failed to create window')
        exit(0)
    user32.ShowWindow(hWnd, SW_SHOW)
    user32.UpdateWindow(hWnd)

    msg = MSG()
    lpmsg = pointer(msg)

    print('Starting message loop')
    while user32.GetMessageA(lpmsg, 0, 0, 0) != 0:
        user32.TranslateMessage(lpmsg)
        user32.DispatchMessageA(lpmsg)

    _ = messagebox("Goodbye!", "I'm a messagebox!")


if __name__ == "__main__":
    main()
