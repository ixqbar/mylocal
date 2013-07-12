package com.shbk.bi.core;

import java.util.HashMap;

public class LogConfig {
	
	private static final HashMap<String, Object> logConfig = new HashMap<String, Object>();
	
	public static Object get(String key) {
		return logConfig.get(key);
	}
	
	public static Object get(String key, Object defaultValue) {
		return null != logConfig.get(key) ? logConfig.get(key) : defaultValue;
	}
	
	public static void set(String key, Object value) {
		logConfig.put(key, value);
	}
}
