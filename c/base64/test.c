#include <stdio.h>
#include <string.h>
#include "base64.h"

int main(int argc, char **argv)
{
    char src[1000] = {0};
    char en[1000] = {0},de[1000];

    if(argc == 1) {
		printf("You can usage like ./base64 params");
        return 1;
    } else {
        strcpy(src, argv[1]);
	}

    base64en(src, en);
    printf("%s => %s\n", src, en);

    base64de(en, de);
    printf("%s => %s\n", en, de);

    return 0;
}
