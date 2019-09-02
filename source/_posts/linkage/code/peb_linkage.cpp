/*
* Tested with Visual Studio 2015 Community Edition.
*
* Compiler optimization (Project->Properties->C/C++->Optimization) and
* debugging (Project->Properties->Linker->Debugging) have to be disabled.
* Also, the entry point has to be set to main (Project->Properties->Linker->Advanced).
* I chose to use global variables because they are not allocated on the stack, thus it was easier for me to
* predict the state of the stack at a given time.
*/

#define MZ 0x5a4d
#define E_LFANEW 0x3c
#define PE_SIGNATURE 0x00004550

typedef void *(*GetProcAddress_t)(void *hModule, char *lpProcName);
typedef void(*ExitProcess_t)(unsigned int uExitCode);
typedef void *(*LoadLibrary_t)(char *lpFileName);
typedef int(*MessageBox_t)(void *hWnd, char *lpText, char *lpCaption, unsigned int uType);

/*
* Use globals in order to prevent the compiler from storing variables in registers or pushing them on the stack.
* This keeps it from intervening with the inline assembly.
*/
unsigned int kernel32_base;
void *user32_base;
void *peb;

GetProcAddress_t GetProcAddress;
ExitProcess_t ExitProcess;
LoadLibrary_t LoadLibrary;
MessageBox_t MessageBox;

int wstrcmp(wchar_t *a, wchar_t *b) {
	int index = 0;
	while (a[index] && b[index] && a[index] == b[index]) {
		++index;
	}
	if (a[index] < b[index]) {
		return -1;
	}
	if (a[index] > b[index]) {
		return 1;
	}
	return 0;
}

/* Given the PEB address, find the address of a module. */
unsigned int GetModuleBase(void *peb, wchar_t *name)
{
	void *Ldr = *(void **)((unsigned char *)peb + 0xc);
	void **InMemoryOrderModuleList = *(void ***)((unsigned char *)Ldr + 0x14);
	void *Flink = *InMemoryOrderModuleList;
	do {
		wchar_t *FullDllName = (wchar_t *)*(void **)((unsigned char *)Flink + 0x28);
		if (wstrcmp(FullDllName, name) == 0) {
			/* Retrieve Base Address */
			return (unsigned int)*(void **)((unsigned char *)Flink + 0x10);
		}
		Flink = *(void **)(unsigned char *)Flink;
	} while (Flink != InMemoryOrderModuleList);
	return 0;
}

int strcmp(char *a, char *b)
{
	int index = 0;
	while (a[index] && b[index] && a[index] == b[index]) {
		++index;
	}
	if (a[index] < b[index]) {
		return -1;
	}
	if (a[index] > b[index]) {
		return 1;
	}
	return 0;
}


/* Given the address of kernel32 module, find the address of GetProcAddress. */
GetProcAddress_t FindGetProcAddress(unsigned int kernel32_base)
{
	/* PE Header */
	unsigned int pe_header = kernel32_base + *(unsigned int *)(kernel32_base + E_LFANEW);
	if (*(unsigned int *)pe_header != PE_SIGNATURE) {
		return 0;
	}
	/* Export Directory */
	unsigned int export_directory = kernel32_base + *(unsigned int *)(pe_header + 0x78);
	unsigned int number_of_names = *(unsigned int*)(export_directory + 0x18);
	unsigned int *address_of_names = (unsigned int *)(kernel32_base + *(unsigned int*)(export_directory + 0x20));

	/* Search within exported functions. */
	unsigned int index = 0;
	for (unsigned int index = 0; index < number_of_names; ++index) {
		if (strcmp((char *)(kernel32_base + address_of_names[index]), "GetProcAddress") == 0) {

			/* Found GetProcAddress. */
			unsigned short *address_of_ordinals = (unsigned short *)(kernel32_base + *(unsigned int*)(export_directory + 0x24));
			unsigned short ordinal = address_of_ordinals[index];
			unsigned int *address_of_functions = (unsigned int *)(kernel32_base + *(unsigned int*)(export_directory + 0x1c));
			return (GetProcAddress_t)(kernel32_base + address_of_functions[ordinal]);
		}
	}
	return 0;
}

int main()
{
	/* Get PEB address. */
	__asm {
		mov eax, fs:[0x30];
		mov peb, eax;
	}

	kernel32_base = GetModuleBase(peb, L"KERNEL32.DLL");
	if (kernel32_base == 0) {
		return 0;
	}

	GetProcAddress = FindGetProcAddress(kernel32_base);

	ExitProcess = (ExitProcess_t)GetProcAddress((void *)kernel32_base, "ExitProcess");

	LoadLibrary = (LoadLibrary_t)GetProcAddress((void *)kernel32_base, "LoadLibraryA");
	user32_base = LoadLibrary("user32.dll");
	if (!user32_base) {
		ExitProcess(1);
	}

	MessageBox = (MessageBox_t)GetProcAddress(user32_base, "MessageBoxA");
	if (!MessageBox) {
		ExitProcess(1);
	}
	MessageBox(0, "HIDDEN", 0, 0);
	ExitProcess(0);
	return 0;
}