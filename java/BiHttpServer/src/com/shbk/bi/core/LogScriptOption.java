package com.shbk.bi.core;

public class LogScriptOption {
	
	public static boolean showUsage() {
		System.err.println("You can usage like java -jar HttpServer.jar Options");
		System.err.println("Options Detail:");
		System.err.println("\t--address                 default 0.0.0.0");
		System.err.println("\t--port                    default 2011");
		System.err.println("\t--biLogPath               default /var/logs");
		System.err.println("\t--httpLogPath             default /var/logs");
		System.err.println("\t--biLogToCompress         like 0 or 1 default 1");
		System.err.println("\t--httpLogTocompress       like 0 or 1 default 0");
		System.err.println("\t--delBiLogAfterCompress   like 0 or 1 default 1");
		System.err.println("\t--delHttpLogAfterCompress like 0 or 1 default 0");
		System.err.println("\t--biPerLogMaxNum          default 10000");
		System.err.println("\t--httpPerLogMaxNum        default 10000");
		System.err.println("\t--serverLogToFile         default 0");
		
		return false;
	}
	
	public static boolean errorOptionValue(String option, String value) {
		System.err.printf("Invalid HttpServer Option name `%s` vlaue `%s`\n", option, value);
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
		LogConfig.set("biLogToCompress",             1);		
		LogConfig.set("httpLogToCompress",           0);
		LogConfig.set("delBiLogFileAfterCompress",   1);
		LogConfig.set("delHttpLogFileAfterCompress", 0);
		LogConfig.set("biPerLogMaxNum",              10000);
		LogConfig.set("httpPerLogMaxNum",            10000);
		LogConfig.set("serverLogToFile",             0);
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
					} else if (tmp[0].equals("--biLogToCompress")) {
						LogConfig.set("biLogToCompress", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--httpLogTocompress")) {
						LogConfig.set("httpLogTocompress", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--delBiLogFileAfterCompress")) {
						LogConfig.set("delBiLogFileAfterCompress", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--delHttpLogFileAfterCompress")) {
						LogConfig.set("delHttpLogFileAfterCompress", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--biPerLogMaxNum")) {
						LogConfig.set("biPerLogMaxNum", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--httpPerLogMaxNum")) {
						LogConfig.set("httpPerLogMaxNum", Integer.parseInt(tmp[1]));
					} else if (tmp[0].equals("--serverLogToFile")) {
						LogConfig.set("serverLogToFile", Integer.parseInt(tmp[1]));
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
		
		if (Integer.parseInt(LogConfig.get("biLogToCompress").toString()) != 0 
				&& Integer.parseInt(LogConfig.get("biLogToCompress").toString()) != 1) {
			return LogScriptOption.errorOptionValue("--biLogToCompress", LogConfig.get("biLogToCompress").toString());
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
		
		if (Integer.parseInt(LogConfig.get("biPerLogMaxNum").toString()) <= 0) {
			return LogScriptOption.errorOptionValue("--biPerLogMaxNum", LogConfig.get("biPerLogMaxNum").toString());
		}
		
		if (Integer.parseInt(LogConfig.get("httpPerLogMaxNum").toString()) <= 0) {
			return LogScriptOption.errorOptionValue("--httpPerLogMaxNum", LogConfig.get("httpPerLogMaxNum").toString());
		}
		
		if (Integer.parseInt(LogConfig.get("serverLogToFile").toString()) != 0 
				&& Integer.parseInt(LogConfig.get("serverLogToFile").toString()) != 1) {
			return LogScriptOption.errorOptionValue("--serverLogToFile", LogConfig.get("serverLogToFile").toString());
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
		} catch (Exception e) {
			System.out.printf("%s|except|%s\n", LogUtil.getFormatDate(), e.getMessage());
			return false;
		}
		
		return true;
	}
}
