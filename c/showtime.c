#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <time.h>

int main(int argc,char *argv[]) {
    time_t newtime;
    
    if (2 == argc) {    
        newtime = strtol(argv[1],NULL,10);        
        char szBuff[30];
        strftime(szBuff, sizeof(szBuff), "%Y/%m/%d %X", localtime(&newtime)); 
        printf("%s\n",szBuff); 
    }
    else {
        time(&newtime);
        printf("%ld\n",newtime);
    }

    exit(0);
}
