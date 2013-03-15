package com.xingqiba;

import org.jboss.netty.buffer.ChannelBuffer;
import org.jboss.netty.buffer.ChannelBuffers;
import org.jboss.netty.channel.Channel;
import org.jboss.netty.channel.ChannelHandlerContext;
import org.jboss.netty.handler.codec.oneone.OneToOneEncoder;

/**
 * 
 * @author ixqbar@gmail.com
 *
 */
public class MessageEncoder extends OneToOneEncoder {
	
    @Override
    protected Object encode(ChannelHandlerContext ctx, Channel channel, Object msg) throws Exception {
        byte[] response = (byte[])msg;
        ChannelBuffer buffer = ChannelBuffers.dynamicBuffer();
        buffer.writeInt(response.length);
        buffer.writeBytes(response);
        
        return buffer;
    }
}