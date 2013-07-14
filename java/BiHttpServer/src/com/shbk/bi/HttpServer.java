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
		//参数解析
		if (false == LogScriptOption.parseOption(args)) {
			return;
		}
				
		System.out.printf("%s|info|address=%s,port=%d,logPath=%s\n", LogUtil.getFormatDate(), LogConfig.get("address"), LogConfig.get("port"), LogConfig.get("logPath"));		
		System.out.printf("%s|info|server start running\n", LogUtil.getFormatDate());
		new HttpServer().run();
	}

}
