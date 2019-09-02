#include <Windows.h>

typedef int(*msg_box) (void *, char *, char *, unsigned int);

int main()
{
	HMODULE user32_dll = LoadLibrary("user32.dll");
	if (!user32_dll) {
		ExitProcess(-1);
	}
	msg_box MsgBox = (msg_box)GetProcAddress(user32_dll, "MessageBoxA");
	if (!MsgBox) {
		ExitProcess(-1);
	}
	MsgBox(NULL, "HIDDEN", NULL, MB_OK);
	ExitProcess(0);
	return 0;
}
