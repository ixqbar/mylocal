package com.shbk.bi.core;

import java.util.HashMap;

import com.shbk.bi.HttpServer;

public class Logger {
	
	private static final boolean serverLogToFile = LogConfig.get("serverLogToFile").toString().equals("1");
	private static final String httpLogLevel = LogConfig.get("httpLogLevel").toString();
	
	public static void debug(String message) {
		if (-1 == Logger.httpLogLevel.indexOf("debug") && -1 == Logger.httpLogLevel.indexOf("all")) {
			return;
		}
		
		if (false == serverLogToFile) {
			System.out.println(message);
		} else {
			Logger.log("debug", message);
		}
	}
	
	public static void debug(String format, Object ... args) {
		if (-1 == Logger.httpLogLevel.indexOf("debug") && -1 == Logger.httpLogLevel.indexOf("all")) {
			return;
		}
		
		if (false == serverLogToFile) {
			System.out.println(String.format(format, args));
		} else {
			Logger.log("debug", String.format(format, args));
		}
	}
	
	public static void info(String message) {
		if (-1 == Logger.httpLogLevel.indexOf("info") && -1 == Logger.httpLogLevel.indexOf("all")) {
			return;
		}
		
		if (false == serverLogToFile) {
			System.out.println(message);
		} else {
			Logger.log("info", message);
		}
	}
	
	public static void info(String format, Object ... args) {
		if (-1 == Logger.httpLogLevel.indexOf("info") && -1 == Logger.httpLogLevel.indexOf("all")) {
			return;
		}
		
		if (false == serverLogToFile) {
			System.out.println(String.format(format, args));
		} else {
			Logger.log("info", String.format(format, args));
		}
	}
	
	public static void error(String message) {
		if (-1 == Logger.httpLogLevel.indexOf("error") && -1 == Logger.httpLogLevel.indexOf("all")) {
			return;
		}
		
		if (false == serverLogToFile) {
			System.out.println(message);
		} else {
			Logger.log("error", message);
		}
	}
	
	public static void error(String format, Object ... args) {
		if (-1 == Logger.httpLogLevel.indexOf("error") && -1 == Logger.httpLogLevel.indexOf("all")) {
			return;
		}
		
		if (false == serverLogToFile) {
			System.out.println(String.format(format, args));
		} else {
			Logger.log("error", String.format(format, args));
		}
	}
	
	public static void warn(String message) {
		if (-1 == Logger.httpLogLevel.indexOf("warn") && -1 == Logger.httpLogLevel.indexOf("all")) {
			return;
		}
		
		if (false == serverLogToFile) {
			System.out.println(message);
		} else {
			Logger.log("warn", message);
		}
	}
	
	public static void warn(String format, Object ... args) {
		if (-1 == Logger.httpLogLevel.indexOf("warn") && -1 == Logger.httpLogLevel.indexOf("all")) {
			return;
		}
		
		if (false == serverLogToFile) {
			System.out.println(String.format(format, args));
		} else {
			Logger.log("warn", String.format(format, args));
		}
	}
	
	public static void except(Exception e) {
		if (-1 == Logger.httpLogLevel.indexOf("except") && -1 == Logger.httpLogLevel.indexOf("all")) {
			return;
		}
		
		if (false == serverLogToFile) {
			e.printStackTrace();
		} else {
			StackTraceElement [] exceptionMessage = e.getStackTrace();
			for (int i = 0, len = exceptionMessage.length; i < len; ++i) {
				Logger.log("except", exceptionMessage[i].toString());
			}
		}
	}
		
	public static void log(String type, String message) {
		HttpServer.queue.add(String.format("todo=%s|%s|%s\n", LogUtil.getFormatDate(), type, message));
	}
	
	public static void bi(int timestamp, byte[] message) {
		HashMap<String, Object> log = new HashMap<String, Object>();
		log.put("time", timestamp);
		log.put("log", message);
		
		HttpServer.queue.add(log);
	}	
}
