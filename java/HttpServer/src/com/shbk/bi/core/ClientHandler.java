package com.shbk.bi.core;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;
import java.nio.charset.Charset;
import java.util.HashMap;
import java.lang.String;

public class ClientHandler implements Handler {
	
	private ByteBuffer buffer; 
    
    public ClientHandler() {  
        buffer = ByteBuffer.allocate(2048);  
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
        	int m = client.read(buffer);
        	if (-1 == m) {
        		break;
        	}
        	if (0 == m) {
        		break;
        	}
        	n += m;
        } while (true);
                       
        if (0 == n) {
        	Logger.info("close|%s", client.socket().getRemoteSocketAddress());
        	client.close();
        	return;
        }
        
        Logger.info("connect|%s", client.socket().getRemoteSocketAddress());
        
        buffer.flip();        
        byte[] pack = new byte[n];
        buffer.get(pack);
        
        Logger.debug("header|total_length=%d|\n%s", n, new String(pack, "UTF-8"));
        
        String clientRequestMethod = "";
        String clientRequestUri    = "";
        String clientRequestData   = "";
        
        int last = n - 1;
        if (pack[0] == (byte) 'G' 
        		&& pack[1] == (byte) 'E' 
        		&& pack[2] == (byte) 'T') {        	
            if (pack[last] == (byte) 0x0A
            		&& pack[last - 1] == (byte) 0x0D  
                    && pack[last - 2] == (byte) 0x0A  
                    && pack[last - 3] == (byte) 0x0D) {
            	//GET
            	String[] header     = (new String(pack, "UTF-8")).split("\r\n"); 
            	clientRequestMethod = "GET";            	
            	clientRequestUri    = header[0].substring(5, header[0].length() - 9);
            }
        } else if (pack[0] == (byte) 'P' 
        		&& pack[1] == (byte) 'O' 
        		&& pack[2] == (byte) 'S' 
        		&& pack[3] == (byte) 'T') {
        	int eofp = -1;  
            for (int i = last; i > 2; i--) {  
                if (pack[i] == (byte) 0x0A 
                		&& pack[i - 1] == (byte) 0x0D  
                        && pack[i - 2] == (byte) 0x0A  
                        && pack[i - 3] == (byte) 0x0D) {  
                	eofp = i + 1;  
                    break;  
                }  
            }  
            
            Logger.debug("header_post_data_position=%d|header_data_length=%d", eofp, n); 
            if (eofp > 0) {
            	int tmp_data_length = n - eofp;
            	int data_length = 0;
            	String[] header = (new String(pack, 0, eofp - 4, "UTF-8")).split("\r\n");            	
            	for (String txt : header) {
            		if (txt.contains("Content-Length:")) {
            			Logger.debug("content_length_text|%s", txt);
            			data_length = Integer.parseInt(txt.substring(2 + txt.lastIndexOf(":")));
            			break;
            		}
            	}
            	Logger.debug("content_length|%d|%d", tmp_data_length, data_length);
            	if (data_length == tmp_data_length) {
            		clientRequestMethod = "POST";
            		clientRequestUri    = header[0].substring(5, header[0].length() - 9);
            		clientRequestData   = new String(pack, eofp, data_length, "UTF-8");
            	}
            }            
        }
        
        String responseData = "ERROR";
        if (clientRequestMethod.equals("POST") || clientRequestMethod.equals("GET")) {
        	HashMap<String, String> requestData = this.parseBiRequestData(clientRequestMethod.equals("POST") ? clientRequestData : clientRequestUri);
        	if (null != requestData) {
	        	if (1 == Integer.parseInt(LogConfig.get("biLogFormat").toString())) {
	        		if (this.formatBiRequestData(requestData)) {
	        			responseData = "OK";
	        		}
	        	} else {
	        		Logger.bi(null != requestData.get("time") ? Integer.parseInt(requestData.get("time").toString()) : LogUtil.getTimestamp(), String.format("%s|%s,%s\n", LogUtil.getFormatDate(), clientRequestUri, clientRequestData).getBytes());
	        		responseData = "OK";
	        	}
        	}
        }
        
        String response_header = String.format("HTTP/1.1 200OK\r\nContent-Type:text/html; charset=utf-8\r\nContent-Length: %d\r\n\r\n%s", responseData.length(), responseData); 
        
        buffer.clear();
		buffer.put(response_header.getBytes());
		        
        key.interestOps(SelectionKey.OP_WRITE);
    }  
    
	
    private void handleWrite(Selector selector, SelectionKey key) throws IOException {  
        SocketChannel client = (SocketChannel) key.channel();
        buffer.flip();
        while (buffer.hasRemaining()) {
        	client.write(buffer);  
        }
        client.close();
        buffer.clear();
    }
    
    private HashMap<String, String> parseBiRequestData(String clientRequestData) {
    	int startPosition = 1 + clientRequestData.indexOf('?');
    	if (0 == startPosition 
    			|| startPosition == clientRequestData.length()) {
    		return null;
    	}
    	
    	HashMap<String, String> requestData = new HashMap<String, String>();
    	String[] data = clientRequestData.substring(startPosition).split("&");
    	for (String param : data) {
    		String[] tmp = param.split("=", 2);
    		if (2 != tmp.length) {
    			return null;
    		}
    		requestData.put(tmp[0], tmp[1]);
    	}
    	
    	//记录第一个请求
    	if (null != requestData.get("time")) {
    		if (null == LogConfig.get("biLogStartTimestamp")) {
    			LogConfig.set("biLogStartTimestamp", requestData.get("time"));
    		}
    	} else {
    		if (null == LogConfig.get("biLogStartTimestamp")) {
    			LogConfig.set("biLogStartTimestamp", LogUtil.getTimestamp());
    		}
    	}
    	
    	return requestData;
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
    	
    	//endl
    	biLogData.put("\n".getBytes());
    	
    	//write to bi
    	biLogData.flip(); 
    	byte[] logContent = new byte[biLogData.limit()];
    	biLogData.get(logContent);
    	biLogData.clear();
    	
    	Logger.bi(null != requestData.get("time") ? Integer.parseInt(requestData.get("time")) : LogUtil.getTimestamp(), logContent);
    	
    	return true;
    }
}
