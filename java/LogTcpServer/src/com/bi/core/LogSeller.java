package com.bi.core;

import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.concurrent.ConcurrentLinkedQueue;

import com.bi.LogTcpServer;

public class LogSeller implements Runnable {
	
	public static boolean isStoped = false;
	
	private final ConcurrentLinkedQueue<Object> queue;
	
	private int logFlushToFilePerNum;
	private String httpLogFilePath;
	private String biLogFilePath;
	
	private FileOutputStream biLogFileWriterHandle;
	private FileWriter httpLogFileWriterHandle;
	private FileWriter biLogIndexFileWriterHandle;
	
	private int biLogNum;
	private int biLogIndex;
	private int biLogMaxInterval;
	private int biLogStartTimestamp;
	
	private int httpLogNum;
	private int httpLogIndex;
	private String httpLogRecordDate;
	
	public LogSeller(ConcurrentLinkedQueue<Object> queue) throws IOException {
		this.queue = queue;
		
		this.logFlushToFilePerNum = Integer.parseInt(LogConfig.get("logFlushToFilePerNum").toString());
		this.biLogNum             = 0;
		this.biLogIndex           = Integer.parseInt(LogConfig.get("biLogIndex").toString());
		this.biLogMaxInterval     = Integer.parseInt(LogConfig.get("biLogMaxInterval").toString());
		this.biLogStartTimestamp  = LogUtil.getTimestamp();
		
		this.httpLogNum           = 0;
		this.httpLogIndex         = Integer.parseInt(LogConfig.get("httpLogIndex").toString());
		this.httpLogRecordDate    = LogUtil.getFormatDate("yyyy-MM-dd");
		
		this.biLogFileWriterHandle      = this.getBiLogFileWriter();
		this.httpLogFileWriterHandle    = this.getHttpLogFileWriter();
		this.biLogIndexFileWriterHandle = new FileWriter(LogConfig.get("biLogIndexFile").toString(), true);
	}
	
	private FileOutputStream getBiLogFileWriter() throws IOException {
		this.biLogFilePath = String.format("%s/bi_%d.log", LogConfig.get("biLogPath"), this.biLogIndex);
		return new FileOutputStream(this.biLogFilePath, true);
	}
	
	private FileWriter getHttpLogFileWriter() throws IOException {
		this.httpLogFilePath = String.format("%s/access_%s_%d.log", LogConfig.get("httpLogPath"), LogUtil.getFormatDate("yyyy-MM-dd"), this.httpLogIndex);
		return new FileWriter(this.httpLogFilePath, true);
		
	}
		
	@Override
	public void run() {
		try { 
            while (true) {
            	if (false == this.queue.isEmpty()) {
            		writeLog();
            	} else if (false == LogTcpServer.isStoped) {
            		Thread.sleep(3000);
            	} else {
            		break;
            	}
            }
        } catch (Exception e) {
        	Logger.except(e);
            cleanLogQueue();  
        }
        
        try {
        	//flush
            this.biLogFileWriterHandle.flush();
            this.httpLogFileWriterHandle.flush();
        } catch (Exception e) {
			Logger.except(e);
		}
		
		LogSeller.isStoped = true;
		System.out.printf("%s|logseller stoped!!\n", LogUtil.getFormatDate());
	}
	
	private void writeLog() throws InterruptedException, IOException {
		Object log = this.queue.poll();
		if (null == log) {
			return;
		}
		
		Boolean flushLog = false;
		Boolean writeServerLogIndexToFile = false;
		String logType = log.getClass().getSimpleName();
		
		if (false == logType.equals("String")) {
			@SuppressWarnings("unchecked")
			HashMap<String, Object> logContent = (HashMap<String, Object>)log;
			//写入			
			this.biLogFileWriterHandle.write((byte[])logContent.get("log"));
			if (this.biLogNum > 0 && 0 == this.biLogNum % this.logFlushToFilePerNum) {
				this.biLogFileWriterHandle.flush();
				flushLog = true;
			}
			//增加LOG统计数量
			this.biLogNum += 1;
			//拆分,压缩
			if (this.biLogNum >= Integer.parseInt(LogConfig.get("biPerLogMaxNum").toString())
					|| this.biLogStartTimestamp + this.biLogMaxInterval <= LogUtil.getTimestamp()) {
				if (false == flushLog) {
					this.biLogFileWriterHandle.flush();
				}
				
				String biLogIndexFileContent = "";
				//压缩
				if (LogConfig.get("biLogToCompress").toString().equals("1")) {
					LogUtil.gzcompress(new File(this.biLogFilePath), LogConfig.get("delBiLogFileAfterCompress").toString().equals("1"));
					String newBiLogIndexFilePath = this.biLogFilePath.concat(".gz");
					biLogIndexFileContent = String.format("%s,%s,%s,%s,%s,%s,%s\n", 
							LogConfig.get("httpStartTimestamp"), 
							LogConfig.get("biLogStartTimestamp"), 
							LogUtil.getTimestamp(),
							logContent.get("time"),
							this.biLogNum,
							newBiLogIndexFilePath,
							Md5.getFileMD5String(newBiLogIndexFilePath));
				} else {
					biLogIndexFileContent = String.format("%s,%s,%s,%s,%s,%s,%s\n", 
							LogConfig.get("httpStartTimestamp"), 
							LogConfig.get("biLogStartTimestamp"), 
							LogUtil.getTimestamp(),
							logContent.get("time"),
							this.biLogNum,
							this.biLogFilePath,
							Md5.getFileMD5String(this.biLogFilePath));
				}
				
				//索引文件
				this.biLogIndexFileWriterHandle.write(biLogIndexFileContent);
				this.biLogIndexFileWriterHandle.flush();
				
				//重新设置开始时间
				LogConfig.set("biLogStartTimestamp", logContent.get("time"));
				
				this.biLogNum            = 0;
				this.biLogIndex         += 1;
				this.biLogStartTimestamp = LogUtil.getTimestamp();
				
				LogConfig.set("biLogIndex", this.biLogIndex);
				
				writeServerLogIndexToFile = true;
				
				this.biLogFileWriterHandle = this.getBiLogFileWriter();
			}			
		} else {
			//写入LOG
			this.httpLogFileWriterHandle.write((String)log);
			if (this.httpLogNum > 0 && 0 == this.httpLogNum % this.logFlushToFilePerNum) {
				this.httpLogFileWriterHandle.flush();
				flushLog = true;
			}
			//增加LOG统计数量
			this.httpLogNum += 1;
			//拆分,压缩
			if (false == this.httpLogRecordDate.equals(LogUtil.getFormatDate("yyyy-MM-dd")) 
					|| this.httpLogNum >= Integer.parseInt(LogConfig.get("httpPerLogMaxNum").toString())) {
				if (false == flushLog) {
					this.httpLogFileWriterHandle.flush();
				}
				
				this.httpLogNum        = 0;
				this.httpLogIndex     += 1;
				this.httpLogRecordDate = LogUtil.getFormatDate("yyyy-MM-dd");
				
				LogConfig.set("httpLogIndex", this.httpLogIndex);				
				
				writeServerLogIndexToFile = true;
				
				if (LogConfig.get("httpLogToCompress").toString().equals("1")) {
					LogUtil.gzcompress(new File(this.httpLogFilePath), LogConfig.get("delHttpLogFileAfterCompress").toString().equals("1"));
				}
				this.httpLogFileWriterHandle = this.getHttpLogFileWriter();
			}
		}
		
		if (writeServerLogIndexToFile) {
			try {				
				FileWriter logIndexFileWriterHandle = new FileWriter(LogConfig.get("serverLogIndexFile").toString());
				logIndexFileWriterHandle.write(String.format("%s,%s\n", this.biLogIndex, this.httpLogIndex));
				logIndexFileWriterHandle.flush();
				logIndexFileWriterHandle.close();
			} catch (Exception e) {
				Logger.except(e);
			}
		}
	}
		
	private void cleanLogQueue() {  
        try {  
            while (false == this.queue.isEmpty()) {  
            	writeLog();  
            }            
        }  catch (Exception e) {  
            Logger.except(e);  
        }  
    }  
}
