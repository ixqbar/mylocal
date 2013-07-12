package com.shbk.bi.core;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;

import com.shbk.bi.HttpServer;

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
        	Logger.info("close|%s", client.getRemoteAddress());
        	client.close();
        	return;
        }
        
        Logger.info("connect|%s", client.getRemoteAddress());
        
        buffer.flip();        
        byte[] pack = new byte[n];
        buffer.get(pack);
        
        Logger.debug("header|total_length=%d|\n%s", n, new String(pack));
        
        String request_method = "";
        String request_uri    = "";
        String request_data   = "";
        
        int last = n - 1;
        if (pack[0] == (byte) 'G' 
        		&& pack[1] == (byte) 'E' 
        		&& pack[2] == (byte) 'T') {        	
            if (pack[last] == (byte) 0x0A
            		&& pack[last - 1] == (byte) 0x0D  
                    && pack[last - 2] == (byte) 0x0A  
                    && pack[last - 3] == (byte) 0x0D) {
            	//GET
            	String[] header = (new String(pack)).split("\r\n"); 
            	request_method  = "GET";            	
            	request_uri     = header[0].substring(5, header[0].length() - 9);
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
            	String[] header = (new String(pack, 0, eofp - 4)).split("\r\n");            	
            	for (String txt : header) {
            		if (txt.contains("Content-Length:")) {
            			Logger.debug("content_length_text|%s", txt);
            			data_length = Integer.parseInt(txt.substring(2 + txt.lastIndexOf(":")));
            			break;
            		}
            	}
            	Logger.debug("content_length|%d|%d", tmp_data_length, data_length);
            	if (data_length == tmp_data_length) {
            		request_method = "POST";
            		request_uri    = header[0].substring(5, header[0].length() - 9);
            		request_data   = new String(pack, eofp, data_length);
            	}
            }            
        }
        
        String response_data   = "";
        if (request_method.equals("POST") || request_method.equals("GET")) {
        	if (null == LogConfig.get("isDebug") || LogConfig.get("isDebug").toString().equals("1")) {
        		response_data = String.format("nmethod=%s<br>uri=%s<br>data=%s", request_method, request_uri, request_data);
        	} else {
        		response_data = "OK";
        	}
        } else {
        	response_data = "ERROR";
		}
        
        Logger.bi(request_uri);
        
        String response_header = String.format("HTTP/1.1 200OK\r\nContent-Type:text/html; charset=utf-8\r\nContent-Length: %d\r\n\r\n%s", response_data.length(), response_data); 
        
        buffer.clear();
		buffer.put(response_header.getBytes());
		        
        key.interestOps(SelectionKey.OP_WRITE);
    }  
    
	
    private void handleWrite(Selector selector, SelectionKey key) throws IOException {  
        SocketChannel client = (SocketChannel) key.channel();
        buffer.flip();
        client.write(buffer);  
        client.close();
        buffer.clear();
    }  
}
