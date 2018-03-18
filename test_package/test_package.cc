#include <stdio.h>
#include <string.h>
#include "mkdio.h"

int main()
{
	const char *text = "This is a _line_ of **Markdown**.";
	char *html;
	mkd_line((char *)text, strlen(text), &html, MKD_NOPANTS);
	printf("%s\n", html);
	return 0;
}
