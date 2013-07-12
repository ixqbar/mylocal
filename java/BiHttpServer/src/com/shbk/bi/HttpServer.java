package com.shbk.bi;

import java.io.IOException;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import com.shbk.bi.core.*;

public class HttpServer {
	
	private final ExecutorService pool;
	public static ConcurrentLinkedQueue<Object> queue = new ConcurrentLinkedQueue<Object>();
	
	public HttpServer() {
		this.pool = Executors.newCachedThreadPool();
	}
	
	public void run() {
		try {
			pool.submit(new LogSeller(HttpServer.queue));
			pool.submit(new TcpServer(8080));
		} catch (Exception e) {
			pool.shutdown();
		}
	}
	
	/**
	 * 
	 * 
	 */
	public static void main(String[] args) throws IOException {
		if (args.length == 4) {
			LogConfig.set("address",     args[0]);
			LogConfig.set("port",        args[1]);
			LogConfig.set("biLogPath",   '/' == args[2].charAt(-1) ? args[2].substring(0, -1) : args[2]);
			LogConfig.set("httpLogPath", '/' == args[3].charAt(-1) ? args[2].substring(0, -1) : args[2]);
			LogConfig.set("isDebug",     0);			
		} else {	
			LogConfig.set("address",     "0.0.0.0");
			LogConfig.set("port",        8080);
			LogConfig.set("biLogPath",   System.getProperty("user.dir") + "/biLogs");
			LogConfig.set("httpLogPath", System.getProperty("user.dir") + "/httpLogs");
			LogConfig.set("isDebug",     1);			
		}
		
		LogConfig.set("biPerLogMaxNum",   10000);
		LogConfig.set("httpPerLogMaxNum", 10000);
		
		LogConfig.set("biLogCompress", 1);
		LogConfig.set("delBiLogFileAfterCompress", 0);
		LogConfig.set("httpLogCompress", 0);
		LogConfig.set("delHttpLogFileAfterCompress", 0);
		
		try {
			java.io.File biLogFolder = new java.io.File(LogConfig.get("biLogPath").toString());
			if (false == biLogFolder.exists() 
					|| false == biLogFolder.isDirectory()
					|| false == biLogFolder.canWrite()) {
				System.err.printf("%s|error|`%s` not exist or isn't directory or can't write\n", LogUtil.getFormatDate(), LogConfig.get("biLogPath"));
				return;
			}
			
			java.io.File httpLogFolder = new java.io.File(LogConfig.get("httpLogPath").toString());
			if (false == httpLogFolder.exists() 
					|| false == httpLogFolder.isDirectory()
					|| false == httpLogFolder.canWrite()) {
				System.err.printf("%s|error|`%s` not exist or isn't directory or can't write\n", LogUtil.getFormatDate(), LogConfig.get("httpLogPath"));
				return;
			}
		} catch (Exception e) {
			System.out.printf("%s|except|%s\n", LogUtil.getFormatDate(), e.getMessage());
			return;
		}
				
		System.out.printf("%s|info|address=%s,port=%d,logPath=%s\n", LogUtil.getFormatDate(), LogConfig.get("address"), LogConfig.get("port"), LogConfig.get("logPath"));		
		System.out.printf("%s|info|server start running\n", LogUtil.getFormatDate());
		new HttpServer().run();
	}

}
