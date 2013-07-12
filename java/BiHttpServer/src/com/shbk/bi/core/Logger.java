package com.shbk.bi.core;

import java.util.HashMap;
import com.shbk.bi.HttpServer;

public class Logger {
	
	public static void debug(String message) {
		if (null == LogConfig.get("isDebug") || LogConfig.get("isDebug").toString().equals("1")) {
			System.out.println(message);
		} else {
			Logger.log("debug", message);
		}
	}
	
	public static void debug(String format, Object ... args) {
		if (null == LogConfig.get("isDebug") || LogConfig.get("isDebug").toString().equals("1")) {
			System.out.println(String.format(format, args));
		} else {
			Logger.log("debug", String.format(format, args));
		}
	}
	
	public static void info(String message) {
		if (null == LogConfig.get("isDebug") || LogConfig.get("isDebug").toString().equals("1")) {
			System.out.println(message);
		} else {
			Logger.log("info", message);
		}
	}
	
	public static void info(String format, Object ... args) {
		if (null == LogConfig.get("isDebug") || LogConfig.get("isDebug").toString().equals("1")) {
			System.out.println(String.format(format, args));
		} else {
			Logger.log("info", String.format(format, args));
		}
	}
	
	public static void except(Exception e) {
		if (null == LogConfig.get("isDebug") || LogConfig.get("isDebug").toString().equals("1")) {
			System.out.println(e);
		} else {
			Logger.log("info", e.getMessage());
		}
	}
	
	
	public static void bi(String message) {
		Logger.log("bi", message);
	}
	
	
	public static void log(String type, String message) {
		HashMap<String, String> logMessage = new HashMap<String, String>();
		logMessage.put("time", String.valueOf(LogUtil.getTimestamp()));
		logMessage.put("date", LogUtil.getFormatDate());
		logMessage.put("type", type);
		logMessage.put("message", message);
		
		HttpServer.queue.add(logMessage);
	}
}
