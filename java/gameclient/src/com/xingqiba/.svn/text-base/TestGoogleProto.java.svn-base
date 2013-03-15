package com.xingqiba;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.log4j.PropertyConfigurator;

import com.google.protobuf.InvalidProtocolBufferException;
import com.xingqiba.MessageProtoHandler.ChatMessage;

public class TestGoogleProto {
	
	private static final Log log = LogFactory.getLog(TestGoogleProto.class);
	
	/**
	 * @param args
	 * @throws InvalidProtocolBufferException 
	 */
	public static void main(String[] args) throws InvalidProtocolBufferException {
		PropertyConfigurator.configure("config/log4j.properties");	
		ChatMessage chatMessage = ChatMessage.newBuilder()
				.setChatChannel(1)
				.setFromId("110")
				.setToId("120")
				.setGroupId("1")
				.setName("ixqbar@gmail.com")
				.setMessage("Hello Proto")
				.build();
		
		byte[] message = chatMessage.toByteArray();
		
		log.info(message);
		
		ChatMessage clientMessage = ChatMessage.parseFrom(message);
		System.out.print(clientMessage);

	}

}
