#include <stdio.h>
#include <unistd.h>

int main(){
	
	static char buff[100];
	sprintf(buff,"Miniproject1");
	//puts(buff);
	write(1, buff, sizeof(buff));
	fflush(stdout);

	buff[0] = '\0';
	sprintf(buff,"\nMini");
	//puts(buff);
	write(1, buff, sizeof(buff));
	fflush(stdout);

	return 0;
}