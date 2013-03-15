package com.xingqiba;

import org.jboss.netty.buffer.ChannelBuffer;
import org.jboss.netty.channel.Channel;
import org.jboss.netty.channel.ChannelHandlerContext;
import org.jboss.netty.handler.codec.frame.FrameDecoder;

/**
 * 
 * @author ixqbar@gmail.com
 *
 */
public class MessageDecoder extends FrameDecoder {
	
	@Override
    protected Object decode(ChannelHandlerContext ctx, Channel channel, ChannelBuffer buffer) throws Exception {
		if (buffer.readableBytes() < 4) {
            return null;
        }
        
        int dataLength = buffer.getInt(buffer.readerIndex());
        if (buffer.readableBytes() < dataLength + 4) {
            return null;
        }
        
        buffer.skipBytes(4);
        byte[] byteMessage = new byte[dataLength];
        buffer.readBytes(byteMessage);
        
        return byteMessage;
    }
}
