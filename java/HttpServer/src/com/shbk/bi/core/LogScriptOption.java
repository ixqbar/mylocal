package com.shbk.bi.core;

import java.io.BufferedReader;
import java.io.FileReader;

public class LogScriptOption {
	
	public static boolean showUsage() {
		System.err.println("You can usage like java -jar HttpServer.jar Options");
		System.err.println("Options Detail:");
		System.err.println("\t--address                 default 0.0.0.0");
		System.err.println("\t--port                    default 2011");
		System.err.println("\t--biLogPath               default /var/logs");
		System.err.println("\t--httpLogPath             default /var/logs");
		System.err.println("\t--serverLogIndexFile      default /var/logs/serverLogIndex.log");
		System.err.println("\t--biLogIndexFile          default /var/logs/biLogIndex.log");
		System.err.println("\t--biLogToCompress         like 0 or 1 default 1");
		System.err.println("\t--biLogFormat             like 0 or 1 default 1");
		System.err.println("\t--httpLogTocompress       like 0 or 1 default 0");
		System.err.println("\t--delBiLogAfterCompress   like 0 or 1 default 1");
		System.err.println("\t--delHttpLogAfterCompress like 0 or 1 default 0");
		System.err.println("\t--biLogMaxInterval        default 3600");
		System.err.println("\t--biPerLogMaxNum          default 10000");
		System.err.println("\t--httpPerLogMaxNum        default 10000");
		System.err.println("\t--serverLogToFile         default 0");
		System.err.println("\t--timeZone                default Asia/Shanghai");
		System.err.println("\t--httLogLevel             default all you can usage like debug,info,warn,error,except");
		
		return false;
	}
	
	public static boolean errorOptionValue(String option, String value) {
		System.err.printf("Invalid HttpServer Option name `%s` value `%s`\n", option, value);
		System.err.println("You can usage like java -jar HttpServer.jar --help to see more information");
		
		return false;
	}
	
	public static boolean errorOptionName(String option) {
		System.err.printf("Invalid HttpServer Option name `%s`\n", option);
		System.err.println("You can usage like java -jar HttpServer.jar --help to see more information");
		
		return false;
	}
	
	public static boolean parseOption(String args[]) {
		//默认参数
		LogConfig.set("address",                     "0.0.0.0");		
		LogConfig.set("port",                        2011);
		LogConfig.set("biLogPath",                   "/var/logs");
		LogConfig.set("httpLogPath",                 "/var/logs");
		LogConfig.set("serverLogIndexFile",          "/var/logs/serverLogIndex.log");
		LogConfig.set("biLogIndexFile",              "/var/logs/biLogIndex.log");
		LogConfig.set("biLogToCompress",             1);	
		LogConfig.set("biLogFormat",                 1);	
		LogConfig.set("httpLogToCompress",           0);
		LogConfig.set("delBiLogFileAfterCompress",   1);
		LogConfig.set("delHttpLogFileAfterCompress", 0);
		LogConfig.set("biLogMaxInterval",            3600);
		LogConfig.set("biPerLogMaxNum",              10000);
		LogConfig.set("httpPerLogMaxNum",            10000);
		LogConfig.set("serverLogToFile",             0);
		LogConfig.set("timeZone",                    "Asia/Shanghai");
		LogConfig.set("httpLogLevel",                "all");
		
		LogConfig.set("httpStartTimestamp",          LogUtil.getTimestamp());
		LogConfig.set("biLogStartTimestamp",         null);
		
		//参数解析
		if (args.length > 0) {
			String[] tmp;
			for (int i = 0, l = args.length; i < l; i++) {
				tmp = args[i].split("=", 2);
				if (2 == tmp.length && tmp[0].length() > 0 && tmp[1].length() > 0) {
					if (tmp[0].equals("--address")) {
						LogConfig.set("address", tmp[1]);
					} else if (tmp[0].equals("--port")) {
						LogConfig.set("port", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--biLogPath")) {
						LogConfig.set("biLogPath", '/' == tmp[1].charAt(tmp[1].length() - 1) ? tmp[1].substring(0, tmp[1].length() - 1) : tmp[1]);;
					} else if (tmp[0].equals("--httpLogPath")) {
						LogConfig.set("httpLogPath", '/' == tmp[1].charAt(tmp[1].length() - 1) ? tmp[1].substring(0, tmp[1].length() - 1) : tmp[1]);;
					} else if (tmp[0].equals("--serverLogIndexFile")) {
						LogConfig.set("serverLogIndexFile", tmp[1]);
					} else if (tmp[0].equals("--biLogIndexFile")) {
						LogConfig.set("biLogIndexFile", tmp[1]);
					} else if (tmp[0].equals("--biLogToCompress")) {
						LogConfig.set("biLogToCompress", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--biLogFormat")) {
						LogConfig.set("biLogFormat", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--httpLogTocompress")) {
						LogConfig.set("httpLogTocompress", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--delBiLogFileAfterCompress")) {
						LogConfig.set("delBiLogFileAfterCompress", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--delHttpLogFileAfterCompress")) {
						LogConfig.set("delHttpLogFileAfterCompress", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--biLogMaxInterval")) {
						LogConfig.set("biLogMaxInterval", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--biPerLogMaxNum")) {
						LogConfig.set("biPerLogMaxNum", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--httpPerLogMaxNum")) {
						LogConfig.set("httpPerLogMaxNum", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--serverLogToFile")) {
						LogConfig.set("serverLogToFile", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--timeZone")) {
						LogConfig.set("timeZone", tmp[1]);
					} else if (tmp[0].equals("--httpLogLevel")) {
						LogConfig.set("httpLogLevel", tmp[1]);
					} else if (tmp[0].equals("--help")) {
						return LogScriptOption.showUsage();
					} else {
						return LogScriptOption.errorOptionName(args[i]);
					}
				} else {
					if (tmp[0].equals("--help")) {
						return LogScriptOption.showUsage();
					} else {
						return LogScriptOption.errorOptionName(args[i]);
					}
				}
			}
		}
		
		if (4 != LogConfig.get("address").toString().split("\\.").length) {
			return LogScriptOption.errorOptionValue("--address", LogConfig.get("address").toString());
		}
		
		if (Integer.parseInt(LogConfig.get("port").toString()) <= 1024) {
			return LogScriptOption.errorOptionValue("--port", LogConfig.get("port").toString());
		}
		
		if (LogConfig.get("biLogPath").toString().length() <= 0) {
			return LogScriptOption.errorOptionValue("--biLogPath", LogConfig.get("biLogPath").toString());
		}
		
		if (LogConfig.get("httpLogPath").toString().length() <= 0) {
			return LogScriptOption.errorOptionValue("--httpLogPath", LogConfig.get("httpLogPath").toString());
		}
		
		if (LogConfig.get("serverLogIndexFile").toString().length() <= 0) {
			return LogScriptOption.errorOptionValue("--serverLogIndexFile", LogConfig.get("serverLogIndexFile").toString());
		}
		
		if (LogConfig.get("biLogIndexFile").toString().length() <= 0) {
			return LogScriptOption.errorOptionValue("--biLogIndexFile", LogConfig.get("biLogIndexFile").toString());
		}
		
		if (Integer.parseInt(LogConfig.get("biLogToCompress").toString()) != 0 
				&& Integer.parseInt(LogConfig.get("biLogToCompress").toString()) != 1) {
			return LogScriptOption.errorOptionValue("--biLogToCompress", LogConfig.get("biLogToCompress").toString());
		}
		
		if (Integer.parseInt(LogConfig.get("biLogFormat").toString()) != 0 
				&& Integer.parseInt(LogConfig.get("biLogFormat").toString()) != 1) {
			return LogScriptOption.errorOptionValue("--biLogFormat", LogConfig.get("biLogFormat").toString());
		}
		
		if (Integer.parseInt(LogConfig.get("httpLogToCompress").toString()) != 0 
				&& Integer.parseInt(LogConfig.get("httpLogToCompress").toString()) != 1) {
			return LogScriptOption.errorOptionValue("--httpLogToCompress", LogConfig.get("httpLogToCompress").toString());
		}
		
		if (Integer.parseInt(LogConfig.get("delBiLogFileAfterCompress").toString()) != 0 
				&& Integer.parseInt(LogConfig.get("delBiLogFileAfterCompress").toString()) != 1) {
			return LogScriptOption.errorOptionValue("--delBiLogFileAfterCompress", LogConfig.get("delBiLogFileAfterCompress").toString());
		}
		
		if (Integer.parseInt(LogConfig.get("delHttpLogFileAfterCompress").toString()) != 0 
				&& Integer.parseInt(LogConfig.get("delHttpLogFileAfterCompress").toString()) != 1) {
			return LogScriptOption.errorOptionValue("--delHttpLogFileAfterCompress", LogConfig.get("delHttpLogFileAfterCompress").toString());
		}
		
		if (Integer.parseInt(LogConfig.get("biLogMaxInterval").toString()) <= 0) {
			return LogScriptOption.errorOptionValue("--biLogMaxInterval", LogConfig.get("biLogMaxInterval").toString());
		}
		
		if (Integer.parseInt(LogConfig.get("biPerLogMaxNum").toString()) <= 1) {
			return LogScriptOption.errorOptionValue("--biPerLogMaxNum", LogConfig.get("biPerLogMaxNum").toString());
		}
		
		if (Integer.parseInt(LogConfig.get("httpPerLogMaxNum").toString()) <= 1) {
			return LogScriptOption.errorOptionValue("--httpPerLogMaxNum", LogConfig.get("httpPerLogMaxNum").toString());
		}
		
		if (Integer.parseInt(LogConfig.get("serverLogToFile").toString()) != 0 
				&& Integer.parseInt(LogConfig.get("serverLogToFile").toString()) != 1) {
			return LogScriptOption.errorOptionValue("--serverLogToFile", LogConfig.get("serverLogToFile").toString());
		}
		
		if (0 == LogConfig.get("timeZone").toString().length()) {
			return LogScriptOption.errorOptionValue("--timeZone", LogConfig.get("timeZone").toString());
		}
		
		if (0 == LogConfig.get("httpLogLevel").toString().length()) {
			return LogScriptOption.errorOptionValue("--httpLogLevel", LogConfig.get("httpLogLevel").toString());
		} else {
			String[] logLevel = LogConfig.get("httpLogLevel").toString().split(",");
			for (String level : logLevel) {
				if (false == level.equals("all") 
						&& false == level.equals("info") 
						&& false == level.equals("error") 
						&& false == level.equals("debug") 
						&& false == level.equals("warn") 
						&& false == level.equals("except")) {
					return LogScriptOption.errorOptionValue("--httpLogLevel", LogConfig.get("httpLogLevel").toString());
				}
			}
		}
		
		try {
			java.io.File biLogFolder = new java.io.File(LogConfig.get("biLogPath").toString());
			if (false == biLogFolder.exists() 
					|| false == biLogFolder.isDirectory()
					|| false == biLogFolder.canWrite()) {
				System.err.printf("%s|error|`%s` not exist or isn't directory or can't write\n", LogUtil.getFormatDate(), LogConfig.get("biLogPath"));
				return false;
			}
			
			java.io.File httpLogFolder = new java.io.File(LogConfig.get("httpLogPath").toString());
			if (false == httpLogFolder.exists() 
					|| false == httpLogFolder.isDirectory()
					|| false == httpLogFolder.canWrite()) {
				System.err.printf("%s|error|`%s` not exist or isn't directory or can't write\n", LogUtil.getFormatDate(), LogConfig.get("httpLogPath"));
				return false;
			}
			
			java.io.File serverLogIndexFile = new java.io.File(LogConfig.get("serverLogIndexFile").toString());
			if (true == serverLogIndexFile.exists()) {
				if (false == serverLogIndexFile.isFile()
					|| false == serverLogIndexFile.canRead()
					|| false == serverLogIndexFile.canWrite()) {
					System.err.printf("%s|error|`%s` not exist or isn't directory or can't write or can't read\n", LogUtil.getFormatDate(), LogConfig.get("logIndexFile"));
					return false;
				}
				
				BufferedReader logIndexFileReader = new BufferedReader(new FileReader(serverLogIndexFile));
				String logIndexFileContent = logIndexFileReader.readLine().trim();
				logIndexFileReader.close();
				
				if (logIndexFileContent.length() > 0) {
					String[] logIndex = logIndexFileContent.split(",");
					if (2 == logIndex.length) {
						LogConfig.set("biLogIndex",   Integer.parseInt(logIndex[0]) + 1);
						LogConfig.set("httpLogIndex", Integer.parseInt(logIndex[1]) + 1);
					} else {
						System.err.printf("%s|error|`%s` invalid content\n", LogUtil.getFormatDate(), LogConfig.get("logIndexFile"));
						return false;
					}
				} else {
					LogConfig.set("biLogIndex",   0);
					LogConfig.set("httpLogIndex", 0);
				}
			} else {
				LogConfig.set("biLogIndex",   0);
				LogConfig.set("httpLogIndex", 0);
			}
			
			java.io.File biLogIndexFile = new java.io.File(LogConfig.get("biLogIndexFile").toString());
			if (biLogIndexFile.exists() 
					&& (false == biLogIndexFile.isFile() || false == biLogIndexFile.canWrite())) {
				System.err.printf("%s|error|`%s` not exist or isn't file or can't write\n", LogUtil.getFormatDate(), LogConfig.get("biLogIndexFile"));
				return false;
			}
		} catch (Exception e) {
			System.out.printf("%s|parse option except|%s\n", LogUtil.getFormatDate(), e.getMessage());
			return false;
		}
		
		return true;
	}
}
