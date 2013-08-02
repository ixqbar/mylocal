package com.bi.core;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;
import java.nio.charset.Charset;
import java.util.HashMap;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.TypeReference;

public class ClientHandler implements Handler {
	
	private ByteBuffer readBuffer;
	private ByteBuffer writeBuffer;
	private int p;
	private int l;
    
    public ClientHandler() {  
    	readBuffer = ByteBuffer.allocate(2048);
    	readBuffer.order(ByteOrder.BIG_ENDIAN);
    	
    	writeBuffer = ByteBuffer.allocate(1024);
    	writeBuffer.order(ByteOrder.BIG_ENDIAN);
    }  
    
	@Override
	public void execute(Selector selector, SelectionKey key) throws IOException {
		try {  
            if (key.isReadable()) {  
                this.handleRead(selector, key);  
            } else if (key.isWritable()) {  
                this.handleWrite(selector, key);  
            }  
        } catch (IOException e) {  
            key.cancel();  
            try { key.channel().close(); } catch (IOException ioe) { }  
        } 
	}
	
	
	private void handleRead(Selector selector, SelectionKey key) throws IOException {  
        SocketChannel client = (SocketChannel) key.channel();
        int n = 0;
        do {
        	int m = client.read(this.readBuffer);
        	if (m <= 0) {
        		break;
        	}
        	n += m;
        } while (true);
        
        this.readBuffer.flip();
        this.p = this.readBuffer.position();
        this.l = this.readBuffer.limit();
        Logger.debug("read data n=%d,p=%d,l=%d", n, this.p, this.l);
        
        if (0 == n) {
        	if (0 == this.l - this.p) {
	        	client.close();
	        	this.readBuffer.clear();
	        	this.writeBuffer.clear();
        	} else {
        		this.readBuffer.rewind();
        	}
        	return;
        } else if (n < this.l - this.p) {
        	this.readBuffer.rewind();
			return;
		}
        
        int dataLen = this.readBuffer.getInt();
        byte[] pack = new byte[dataLen];
        this.readBuffer.get(pack);
        
        String postData = new String(pack, "UTF-8");
        Logger.debug("receive data=%s", postData);
        
        String responseData = "ERROR";
        HashMap<String, String> requestData = JSON.parseObject(postData, new TypeReference<HashMap<String, String>>(){});
        if (1 == Integer.parseInt(LogConfig.get("biLogFormat").toString())) {
    		if (this.formatBiRequestData(requestData)) {
    			responseData = "OK";
    		}
    	} else {
    		Logger.bi(null != requestData.get("time") ? Integer.parseInt(requestData.get("time").toString()) : LogUtil.getTimestamp(), String.format("%s|%s\n", LogUtil.getFormatDate(), postData).getBytes());
    		responseData = "OK";
    	}
        
        this.writeBuffer.clear();
        this.writeBuffer.putInt(responseData.length());
		this.writeBuffer.put(responseData.getBytes());
		
        key.interestOps(SelectionKey.OP_WRITE);
    }  
    	
    private void handleWrite(Selector selector, SelectionKey key) throws IOException {  
        SocketChannel client = (SocketChannel) key.channel();
        this.writeBuffer.flip();
        while (this.writeBuffer.hasRemaining()) {
        	client.write(this.writeBuffer); 
        }
        key.interestOps(SelectionKey.OP_READ);
    }
    
    private Boolean formatBiRequestData(HashMap<String, String> requestData) {
    	Charset charset      = Charset.forName("UTF-8");
    	ByteBuffer biLogData = ByteBuffer.allocate(2048);
    	//timestamp
    	biLogData.putInt(LogUtil.getTimestamp());
    	//timestamp
    	if (null != requestData.get("time")) {
    		biLogData.putInt(Integer.parseInt(requestData.get("time").toString()));
    	} else {
    		biLogData.putInt(0);
    	}
    	//event
    	if (null != requestData.get("event")) {
    		biLogData.putInt(Integer.parseInt(requestData.get("event").toString()));
    	} else {
    		biLogData.putInt(-1);
    	}
    	//uid
    	String uid;
    	if (null != requestData.get("uid")) {
    		if (requestData.get("uid").toString().length() < 50) {
    			uid = String.format("%0" + (50 - requestData.get("uid").toString().length()) + "d%s", 0, requestData.get("uid"));
    		} else {
    			uid = requestData.get("uid").substring(0, 50);
    		}
    	} else {
    		uid = String.format("%050d", 0);
    	}
    	biLogData.put(uid.getBytes(charset));
    	
    	//p1->p16
    	short datalen  = 0;
    	String[] params = {"p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9", "p10"};
    	
    	for (String p : params) {
    		datalen += null != requestData.get(p) ? requestData.get(p).length() : 0;
		}    	
    	biLogData.putShort(datalen);
    	
    	for (String p : params) {
    		biLogData.putShort(null != requestData.get(p) ? (short)(requestData.get(p).length()) : 0);
    	}
    	
    	for (String p : params) {
	    	if (null != requestData.get(p)) {
	    		biLogData.put(requestData.get(p).toString().getBytes(charset));
	    	}
    	}
    	
    	//write to bi
    	biLogData.flip(); 
    	byte[] logContent = new byte[biLogData.limit()];
    	biLogData.get(logContent);
    	biLogData.clear();
    	
    	Logger.bi(null != requestData.get("time") ? Integer.parseInt(requestData.get("time")) : LogUtil.getTimestamp(), logContent);
    	
    	return true;
    }
}
