package com.shbk.bi;

import java.io.IOException;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import com.shbk.bi.core.*;

public class HttpServer {
	
	private final ExecutorService pool;
	public static ConcurrentLinkedQueue<String> queue = new ConcurrentLinkedQueue<String>();
	
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
		System.out.println("running .....");
		new HttpServer().run();
	}

}
