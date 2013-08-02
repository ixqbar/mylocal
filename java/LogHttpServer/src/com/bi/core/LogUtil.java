package com.bi.core;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.zip.GZIPOutputStream;

public class LogUtil {
	
	public static String getFormatDate() {
		return new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS.Z").format(new Date());
	}
	
	public static String getFormatDate(String format) {
		return new SimpleDateFormat(format).format(new Date());
	}
	
	public static int getTimestamp() {
		return (int) (System.currentTimeMillis() / 1000);
	}
	
	public static boolean gzcompress(File file, boolean delete) {
		boolean result;
		try {
			FileInputStream fis = new FileInputStream(file);  
	        FileOutputStream fos = new FileOutputStream(file.getPath().concat(".gz"));  
	  
	        result = LogUtil.gzcompress(fis, fos);  
	  
	        fis.close();  
	        fos.flush();  
	        fos.close();  
	  
	        if (result && delete) {  
	            file.delete();  
	        }
		} catch (Exception e) {
			Logger.except(e);
			result = false;
		}
		
		return result;		
	}
	
	public static boolean gzcompress(InputStream is, OutputStream os) {
		boolean result = true;
		try {
			GZIPOutputStream gos = new GZIPOutputStream(os);  
			  
	        int count;  
	        int BUFFER = 1024;
	        byte data[] = new byte[BUFFER];  
	        while ((count = is.read(data, 0, BUFFER)) != -1) {  
	            gos.write(data, 0, count);  
	        }  
	  
	        gos.finish(); 
	        gos.flush();  
	        gos.close();
		} catch (Exception e) {
			Logger.except(e);
			result = false;
		}
		
		return result;
	}
	
}
