package com.shbk.bi;

import java.io.IOException;
import java.util.TimeZone;
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
		if (false == LogScriptOption.parseOption(args)) {
			return;
		}
		
		TimeZone.setDefault(TimeZone.getTimeZone(LogConfig.get("timeZone").toString()));
		
		Logger.info("address=%s,port=%d,biLogPath=%s,httpLogPath=%s", LogConfig.get("address"), LogConfig.get("port"), LogConfig.get("biLogPath"), LogConfig.get("httpLogPath"));		
		Logger.info("server start running");
		
		new HttpServer().run();
	}

}
