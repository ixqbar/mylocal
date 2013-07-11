package com.shbk.bi.core;

public class Logger {
	
	public static void debug(Object message) {
		System.out.println(message);
	}
	
	public static void debug(String format, Object ... message) {
		//System.out.printf(format + "\n", message);
	}
	
	public static void info(Object message) {
		System.out.println(message);
	}
	
	public static void info(String format, Object ... message) {
		System.out.printf(format + "\n", message);
	}
	
	public static void except(Exception e) {
		System.out.println(e);
	}
}
