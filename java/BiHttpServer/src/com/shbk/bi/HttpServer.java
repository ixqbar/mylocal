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
			pool.submit(new TcpServer(LogConfig.get("address").toString(), Integer.parseInt(LogConfig.get("port").toString())));
		} catch (Exception e) {
			pool.shutdown();
		}
	}
	
	/**
	 * 
	 * 
	 */
	public static void main(String[] args) throws IOException {
		if (args.length >= 4) {
			LogConfig.set("address",     args[0]);
			LogConfig.set("port",        Integer.parseInt(args[1]));
			LogConfig.set("biLogPath",   '/' == args[2].charAt(args[2].length() - 1) ? args[2].substring(0, args[2].length() - 1) : args[2]);
			LogConfig.set("httpLogPath", '/' == args[3].charAt(args[3].length() - 1) ? args[3].substring(0, args[3].length() - 1) : args[3]);
			LogConfig.set("isDebug",     0);			
		} else {	
			System.err.println("You can usage like java -jar HttpServer.jar address port biLogPath httpLogPath [biLogToCompress, httpLogToCompress, delBiLogAfterCompress, delHttpLogAfterCompress]");
			System.err.println("Detail:");
			System.err.println("\taddress                 like 127.0.0.1");
			System.err.println("\tprot                    like 8080");
			System.err.println("\tbiLogPath               like /data/logs/bi");
			System.err.println("\thttpLogPath             like /data/logs/http");
			System.err.println("\tbiLogToCompress         like 0 or 1 default 1");
			System.err.println("\thttpLogTocompress       like 0 or 1 default 0");
			System.err.println("\tdelBiLogAfterCompress   like 0 or 1 default 1");
			System.err.println("\tdelHttpLogAfterCompress like 0 or 1 default 0");
			return;			
		}
		
		LogConfig.set("biPerLogMaxNum",   10000);
		LogConfig.set("httpPerLogMaxNum", 10000);
		
		LogConfig.set("biLogCompress",   args.length >= 5 ? Integer.parseInt(args[4]) : 1);		
		LogConfig.set("httpLogCompress", args.length >= 6 ? Integer.parseInt(args[5]) : 0);
		
		LogConfig.set("delBiLogFileAfterCompress",   args.length >= 7 ? Integer.parseInt(args[6]) : 1);
		LogConfig.set("delHttpLogFileAfterCompress", args.length >= 8 ? Integer.parseInt(args[7]) : 0);
		
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
