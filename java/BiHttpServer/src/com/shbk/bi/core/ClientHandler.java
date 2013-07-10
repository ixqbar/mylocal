package com.shbk.bi.core;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;

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
        int n = client.read(buffer);  
        if (-1 == n) {
        	buffer.clear();
        	client.close();
        } else if (n > 0) {
            buffer.flip();
            
            byte[] pack = new byte[n];
            buffer.get(pack);
            buffer.rewind();
            
            String[] header = (new String(pack)).split("\r\n");
            for (String str : header) {
            	System.out.println(str);
            }
                        
            key.interestOps(SelectionKey.OP_READ | SelectionKey.OP_WRITE);
        }  
    }  
    
	
    private void handleWrite(Selector selector, SelectionKey key) throws IOException {  
        SocketChannel client = (SocketChannel) key.channel();  
        client.write(buffer);  
        if (buffer.remaining() == 0) {  
            buffer.clear();  
            //key.interestOps(SelectionKey.OP_READ);
            client.close();
        }  
    }  
}
