package com.shbk.bi;

import java.io.IOException;
import java.util.TimeZone;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import sun.misc.Signal;

import com.shbk.bi.core.*;

public class HttpServer {
	
	private final ExecutorService pool;
	public static ConcurrentLinkedQueue<Object> queue = new ConcurrentLinkedQueue<Object>();
	public static boolean isStoped = false;
	
	public HttpServer() {
		this.pool = Executors.newCachedThreadPool();
	}
	
	public void run() {
		boolean error = false;
		try {
			pool.submit(new LogSeller(HttpServer.queue));
			pool.submit(new TcpServer(LogConfig.get("address").toString(), Integer.parseInt(LogConfig.get("port").toString())));
		} catch (Exception e) {
			pool.shutdown();
			e.printStackTrace();
			error = true;
		}
		
		if (error) {
			return;
		}
		
		LogSignalHandler logSignalHandler = new LogSignalHandler();
		Signal.handle(new Signal("TERM"), logSignalHandler);
		
		while (false == LogSeller.isStoped) {
			try {
				Thread.sleep(10000);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
		
		pool.shutdown();
		System.out.printf("%s|httpserver stoped!!\n", LogUtil.getFormatDate());
	}
	
	/**
	 * 
	 * 
	 */
	public static void main(String[] args) throws IOException {
		if (false == LogScriptOption.parseOption(args)) {
			return;
		}
		
		TimeZone.setDefault(TimeZone.getTimeZone(LogConfig.get("timeZone").toString()));
		
		Logger.info("server start running address=%s,port=%d,biLogPath=%s,httpLogPath=%s,serverLogIndexFile=%s", LogConfig.get("address"), LogConfig.get("port"), LogConfig.get("biLogPath"), LogConfig.get("httpLogPath"), LogConfig.get("serverLogIndexFile"));		
		System.out.printf("%s|server start running\n", LogUtil.getFormatDate());
		
		new HttpServer().run();
	}

}
