#include <stdio.h>

#define sum(n) (sum_helper(0, n))
int sum_helper (int acc, int n)
{
	if (n == 1) {
		return acc + 1;
	}
	return sum_helper(acc + n, n - 1);
}

int main()
{
	int n;
	scanf("%d", &n);
	printf("%d\n", sum(n));
	return 0;
}
