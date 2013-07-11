package com.shbk.bi.core;

import java.util.concurrent.ConcurrentLinkedQueue;

public class LogSeller implements Runnable {
	
	private final ConcurrentLinkedQueue<String> queue;
	
	public LogSeller(ConcurrentLinkedQueue<String> queue) {
		this.queue = queue;
	}
	
	@Override
	public void run() {
		try { 
            while (true) {
            	if (this.queue.size() > 0) {
            		writeLog();  
            	} else {
            		Thread.sleep(3000);
            	}
            }  
        }  
        catch (InterruptedException e) {  
            cleanLogQueue();  
        }  		
	}
	
	private void writeLog() throws InterruptedException {
		String log = this.queue.poll();
		if (null == log) {
			return;
		}
		
		Logger.info("log-to-file|%s", log);
	}
	
	private void cleanLogQueue() {  
        try {  
            while (this.queue.size() > 0) {  
            	writeLog();  
            }  
        }  catch (InterruptedException e) {  
            Logger.except(e);  
        }  
    }  
}
