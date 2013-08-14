
/**
 * @author ixqbar@gmail.com
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdarg.h>
#include <time.h>
#include <signal.h>

#include <lualib.h>
#include <lua.h>
#include <lauxlib.h>
#include "md5.h"

int chello(lua_State* L)
{
	size_t l;
	const char *message = luaL_checklstring(L, 1, &l);
	lua_pushstring(L, message);
	return 1;
}

int cmd5(lua_State* L)
{
	size_t msg_len;
	const char *msg = lua_tolstring(L,1,&msg_len);

	if (msg_len) {
		char buff[16];
		md5(msg, msg_len, buff);
		char md5buff[33];
		int i;
		static char map[16] = {'0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'};
		unsigned char byte,half_byte;
		for(i = 0; i < 16; i++) {
			byte = buff[i];
			half_byte = byte >> 4;
			md5buff[2*i] = map[half_byte];
			half_byte = byte & 0x0f;
			md5buff[2*i + 1] = map[half_byte];
		}
		md5buff[32] = '\0';

		lua_pushstring(L, md5buff);
	} else {
		lua_pushstring(L, "");
	}

	return 1;
}

static int cToLuaFunc (lua_State* L)
{
	lua_register(L, "chello", chello);
	lua_register(L, "cmd5", cmd5);

	return 1;
}


void error(lua_State *L, const char *fmt, ...)
{
	char nowTimeBuff[64];
    time_t now = time(NULL);
	strftime(nowTimeBuff,sizeof(nowTimeBuff),"%d %b %H:%M:%S",localtime(&now));

    char msg[1024];
	va_list ap;
    va_start(ap, fmt);
    vsnprintf(msg, sizeof(msg), fmt, ap);
    va_end(ap);

    FILE *fp = stdout;
    fprintf(fp,"[%d] %s %s\n", getpid(), nowTimeBuff, msg);
    fflush(fp);

	if (L) lua_close(L);

	exit(EXIT_FAILURE);
}

/**
 *
 * callLuaFunc(L, "f", "dd>d", x, y, &z);
 *
 *
 */
void callLuaFunc(lua_State *L, const char *func, const char *sig, ...)
{
	va_list vl;
	int narg, nres;  /* number of arguments and results */

	va_start(vl, sig);
	lua_getglobal(L, func);  /* get function */

	/* push arguments */
	narg = 0;
	while (*sig) {  /* push arguments */
		switch (*sig++) {

			case 'd':  /* double argument */
				lua_pushnumber(L, va_arg(vl, double));
				break;

			case 'i':  /* int argument */
				lua_pushnumber(L, va_arg(vl, int));
				break;

			case 's':  /* string argument */
				lua_pushstring(L, va_arg(vl, char *));
				break;

			case '>':
				goto endwhile;

			default:
				error(L, "invalid option (%c)", *(sig - 1));
				break;
		}
		narg++;
		luaL_checkstack(L, 1, "too many arguments");
	} endwhile:

	/* do the call */
	nres = strlen(sig);  /* number of expected results */
	if (lua_pcall(L, narg, nres, 0) != 0)  /* do the call */
	error(L, "error running function `%s': %s",	func, lua_tostring(L, -1));

	/* retrieve results */
	nres = -nres;  /* stack index of first result */
	while (*sig) {  /* get results */
		switch (*sig++) {

			case 'd':  /* double result */
				if (!lua_isnumber(L, nres))
				error(L, "wrong result type");
				*va_arg(vl, double *) = lua_tonumber(L, nres);
				break;

			case 'i':  /* int result */
				if (!lua_isnumber(L, nres))
				error(L, "wrong result type");
				*va_arg(vl, int *) = (int)lua_tonumber(L, nres);
				break;

			case 's':  /* string result */
				if (!lua_isstring(L, nres))
				error(L, "wrong result type");
				*va_arg(vl, const char **) = lua_tostring(L, nres);
				break;

			default:
				error(L, "invalid option (%c)", *(sig - 1));
				break;
		}
		nres++;
	}
	va_end(vl);
}

/*
 *
 */
int main(int argc, char** argv)
{

    lua_State *L = luaL_newstate();

    luaL_openlibs(L);
    cToLuaFunc(L);
    luaL_loadfile(L, "./test.lua");
	lua_pcall(L, 0, 0, 0);

	int result;
	callLuaFunc(L, "sum", "ii>i", 10, 20, &result);

	printf("result=%d\n", result);

    lua_close(L);

    return (EXIT_SUCCESS);
}
