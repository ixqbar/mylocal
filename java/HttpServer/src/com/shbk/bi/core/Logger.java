package com.shbk.bi.core;

import java.util.HashMap;

import com.shbk.bi.HttpServer;

public class Logger {
	
	private static final boolean serverLogToFile = LogConfig.get("serverLogToFile").toString().equals("1");
	private static final String httpLogLevel = LogConfig.get("httpLogLevel").toString();
	public static void debug(String message) {
		if (false == serverLogToFile) {
			System.out.println(message);
		} else if (Logger.httpLogLevel.indexOf("debug") >= 0 || Logger.httpLogLevel.indexOf("all") >= 0) {
			Logger.log("debug", message);
		}
	}
	
	public static void debug(String format, Object ... args) {
		if (false == serverLogToFile) {
			System.out.println(String.format(format, args));
		} else if (Logger.httpLogLevel.indexOf("debug") >= 0 || Logger.httpLogLevel.indexOf("all") >= 0) {
			Logger.log("debug", String.format(format, args));
		}
	}
	
	public static void info(String message) {
		if (false == serverLogToFile) {
			System.out.println(message);
		} else if (Logger.httpLogLevel.indexOf("info") >= 0 || Logger.httpLogLevel.indexOf("all") >= 0) {
			Logger.log("info", message);
		}
	}
	
	public static void info(String format, Object ... args) {
		if (false == serverLogToFile) {
			System.out.println(String.format(format, args));
		} else if (Logger.httpLogLevel.indexOf("info") >= 0 || Logger.httpLogLevel.indexOf("all") >= 0) {
			Logger.log("info", String.format(format, args));
		}
	}
	
	public static void error(String message) {
		if (false == serverLogToFile) {
			System.out.println(message);
		} else if (Logger.httpLogLevel.indexOf("error") >= 0 || Logger.httpLogLevel.indexOf("all") >= 0) {
			Logger.log("error", message);
		}
	}
	
	public static void error(String format, Object ... args) {
		if (false == serverLogToFile) {
			System.out.println(String.format(format, args));
		} else if (Logger.httpLogLevel.indexOf("error") >= 0 || Logger.httpLogLevel.indexOf("all") >= 0) {
			Logger.log("error", String.format(format, args));
		}
	}
	
	public static void warn(String message) {
		if (false == serverLogToFile) {
			System.out.println(message);
		} else if (Logger.httpLogLevel.indexOf("warn") >= 0 || Logger.httpLogLevel.indexOf("all") >= 0) {
			Logger.log("warn", message);
		}
	}
	
	public static void warn(String format, Object ... args) {
		if (false == serverLogToFile) {
			System.out.println(String.format(format, args));
		} else if (Logger.httpLogLevel.indexOf("warn") >= 0 || Logger.httpLogLevel.indexOf("all") >= 0) {
			Logger.log("warn", String.format(format, args));
		}
	}
	
	public static void except(Exception e) {
		if (false == serverLogToFile) {
			e.printStackTrace();
		} else if (Logger.httpLogLevel.indexOf("except") >= 0 || Logger.httpLogLevel.indexOf("all") >= 0) {
			StackTraceElement [] exceptionMessage = e.getStackTrace();
			for (int i = 0, len = exceptionMessage.length; i < len; i++) {
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
