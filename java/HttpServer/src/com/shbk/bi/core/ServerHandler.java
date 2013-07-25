package com.shbk.bi.core;

import java.io.IOException;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;

public class ServerHandler implements Handler {

	@SuppressWarnings("unused")
	@Override
	public void execute(Selector selector, SelectionKey key) throws IOException {
		ServerSocketChannel server = (ServerSocketChannel) key.channel();  
        SocketChannel client = null;  
        try {  
            client = server.accept();  
        } catch (IOException e) {  
            Logger.except(e);
            return;  
        }  
          
        SelectionKey clientKey = null;  
        try { 
            client.configureBlocking(false);  
            clientKey = client.register(selector, SelectionKey.OP_READ);  
            clientKey.attach(new ClientHandler());  
        } catch (IOException e) { 
        	if (null != clientKey) {
        		clientKey.cancel();
        	}
            try { client.close(); } catch (IOException ioe) { Logger.except(ioe); }  
        } 
	}

}
