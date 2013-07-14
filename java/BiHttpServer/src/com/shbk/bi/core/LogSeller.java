package com.shbk.bi.core;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.concurrent.ConcurrentLinkedQueue;

public class LogSeller implements Runnable {
	
	private final ConcurrentLinkedQueue<Object> queue;
	private HashMap<String, Object> biLogRecordInfo = new HashMap<String, Object>();
	private HashMap<String, Object> httpLogRecordInfo = new HashMap<String, Object>();	
	private String logRecordDate = LogUtil.getFormatDate("yyyy-MM-dd");
	private FileWriter biLogFileWriterHandle;
	private FileWriter httpLogFileWriterHandle;
	
	public LogSeller(ConcurrentLinkedQueue<Object> queue) throws IOException {
		this.queue = queue;
		
		this.biLogRecordInfo.put("num", 0);
		this.biLogRecordInfo.put("index", 0);
		this.httpLogRecordInfo.put("num", 0);
		this.httpLogRecordInfo.put("index", 0);
		
		this.biLogFileWriterHandle   = this.getLogFileWriter("bi");
		this.httpLogFileWriterHandle = this.getLogFileWriter("http");
	}
	
	private FileWriter getLogFileWriter(String type) throws IOException {
		String httpLogFile;
		if (type.equals("http")) {
			httpLogFile = String.format("%s/access_%s_%d.log",
					LogConfig.get("httpLogPath"),
					LogUtil.getFormatDate("yyyy-MM-dd"),
					this.httpLogRecordInfo.get("index"));
			this.httpLogRecordInfo.put("file", httpLogFile);
		} else { 
			httpLogFile = String.format("%s/http_%s_%d.log",
					LogConfig.get("biLogPath"),
					LogUtil.getFormatDate("yyyy-MM-dd"),
					this.biLogRecordInfo.get("index"));
			this.biLogRecordInfo.put("file", httpLogFile);			
		}	
		
		return new FileWriter(httpLogFile, true);
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
        catch (Exception e) {  
            cleanLogQueue();  
        }  		
	}
	
	private void writeLog() throws InterruptedException, IOException {
		Object log = this.queue.poll();
		if (null == log) {
			return;
		}
		
		HashMap<String, String> logMessage = (HashMap<String, String>)log;
		if (logMessage.get("type").equals("bi")) {
			if (false == this.logRecordDate.equals(LogUtil.getFormatDate("yyyy-MM-dd")) 
					|| Integer.parseInt(this.biLogRecordInfo.get("num").toString()) >= Integer.parseInt(LogConfig.get("biPerLogMaxNum").toString())) {
				this.biLogRecordInfo.put("index", Integer.parseInt(this.biLogRecordInfo.get("index").toString()) + 1);
				this.biLogRecordInfo.put("num", 0);
				if (LogConfig.get("biLogToCompress").toString().equals("1")) {
					LogUtil.gzcompress(new File(this.biLogRecordInfo.get("file").toString()), LogConfig.get("delBiLogFileAfterCompress").toString().equals("1"));
				}
				this.biLogFileWriterHandle = this.getLogFileWriter("bi");
			}
			this.biLogFileWriterHandle.write(String.format("%s|%s\n", logMessage.get("date"), logMessage.get("message")));
			this.biLogFileWriterHandle.flush();
			this.biLogRecordInfo.put("num", Integer.parseInt(this.biLogRecordInfo.get("num").toString()) + 1);
		} else {
			if (false == this.logRecordDate.equals(LogUtil.getFormatDate("yyyy-MM-dd")) 
					|| Integer.parseInt(this.httpLogRecordInfo.get("num").toString()) >= Integer.parseInt(LogConfig.get("httpPerLogMaxNum").toString())) {
				this.httpLogRecordInfo.put("index", Integer.parseInt(this.httpLogRecordInfo.get("index").toString()) + 1);
				this.httpLogRecordInfo.put("num", 0);
				if (LogConfig.get("httpLogToCompress").toString().equals("1")) {
					LogUtil.gzcompress(new File(this.httpLogRecordInfo.get("file").toString()), LogConfig.get("delHttpLogFileAfterCompress").toString().equals("1"));
				}
				this.httpLogFileWriterHandle = this.getLogFileWriter("http");
			}
			this.httpLogFileWriterHandle.write(String.format("%s|%s\n", logMessage.get("date"), logMessage.get("message")));
			this.httpLogFileWriterHandle.flush();
			this.httpLogRecordInfo.put("num", Integer.parseInt(this.httpLogRecordInfo.get("num").toString()) + 1);
		}
	}
	
	private void cleanLogQueue() {  
        try {  
            while (this.queue.size() > 0) {  
            	writeLog();  
            }  
        }  catch (Exception e) {  
            Logger.except(e);  
        }  
    }  
}
