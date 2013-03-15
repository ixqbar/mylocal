package com.xingqiba;

import java.net.InetSocketAddress;
import java.util.concurrent.Executors;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.log4j.PropertyConfigurator;
import org.jboss.netty.bootstrap.ClientBootstrap;
import org.jboss.netty.channel.Channel;
import org.jboss.netty.channel.ChannelFuture;
import org.jboss.netty.channel.socket.nio.NioClientSocketChannelFactory;

import com.xingqiba.MessageClientPipelineFactory;
import com.xingqiba.MessageProtoHandler.ChatMessage;

public class MessageClient {
	private static final Log log = LogFactory.getLog(MessageClient.class);
	
	
	public static void main(String[] args) throws Exception {
		PropertyConfigurator.configure("config/log4j.properties");	
		
        // Configure the client.
        ClientBootstrap bootstrap = new ClientBootstrap(
                new NioClientSocketChannelFactory(
                        Executors.newCachedThreadPool(),
                        Executors.newCachedThreadPool()));
        // Set up the event pipeline factory.
        bootstrap.setPipelineFactory(new MessageClientPipelineFactory());
        // Start the connection attempt.
        ChannelFuture future = bootstrap.connect(new InetSocketAddress("127.0.0.1", 8088));
        
        ChatMessage chatInitMessage = ChatMessage.newBuilder()
				.setChatChannel(100)
				.setFromId("110")
				.setName("ixqbar@gmail.com")
				.build();
		
        Channel client = future.getChannel();
        client.write(chatInitMessage.toByteArray());
        
        
        ChatMessage chatWorldMessage = ChatMessage.newBuilder()
				.setChatChannel(1)
				.setFromId("110")
				.setName("ixqbar@gmail.com")
				.setMessage("Hello Proto")
				.build();
        
        client.write(chatWorldMessage.toByteArray());
        
        
        
        // Wait until the connection is closed or the connection attempt fails.
        future.getChannel().getCloseFuture().awaitUninterruptibly();
        // Shut down thread pools to exit.
        bootstrap.releaseExternalResources();
        
        
        
        log.info("end");
    }
}
