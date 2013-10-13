//
//  LSLog.h
//  HelloGame
//
//  Created by venkman on 13-10-13.
//
//

#ifndef HelloGame_LSLog_h
#define HelloGame_LSLog_h

#include "cocos2d.h"

enum{
	LSLOG_VERBOSE = 0,
	LSLOG_DEBUG,
	LSLOG_INFO,
	LSLOG_WARN,
	LSLOG_ERROR,
	LSLOG_COUNT,
};

const std::string lsLog_name[LSLOG_COUNT] = {
    "verbose",
    "debug",
    "info",
    "warn",
    "error"
};

const std::string lsLog_androidMethod[LSLOG_COUNT] = {
    "v",
    "d",
    "i",
    "w",
    "e"
};

/**
 @brief 自定义日志系统，前期使用，以后可以优化
 */
class LSLog: public cocos2d::CCObject {
public:
	/// verbose 详细日志，一般常用的打印信息
	static void verbose(const char * pszFormat, ...);
	/// debug 调试 ,调试过程所注意的信息
	static void debug(const char * pszFormat, ...);
	/// info 一般信息,
	static void info(const char * pszFormat, ...);
	///  warn 警告信息
	static void warn(const char * pszFormat, ...);
	/// error 错误信息
	static void error(const char * pszFormat, ...);
private:
	static const int LOG_VALUE;
	static void printLog(int type, const char* format, va_list ap);
    
	static void printAndroidLog(const char* methodName, const char* log);
};

#define LOG_INFO(fmt,...) LSLog::info("File(%s),Line(%d),%s", __FILE__, __LINE__, CCString::createWithFormat(fmt, ##__VA_ARGS__)->getCString());

#endif /* LSLOG_H_ */

