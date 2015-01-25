package cs5300.proj1a.utils;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;
import java.util.Date;
import java.util.Set;



public class Utils {

	public static long getCurrentTimeInMillis(){
		Date date= new Date();
		Timestamp currentTimestamp= new Timestamp(date.getTime());
		return currentTimestamp.getTime();
	}

	public static boolean hasSessionExpired(Date d){
		long currenttime = getCurrentTimeInMillis();
		Timestamp dateinnumber = new Timestamp(d.getTime());
		if ( currenttime  > dateinnumber.getTime()){
			return true;
		}else{
			return false;
		}
	}

	public static List<String> splitAndTrim(String arg,String delRegex){

		String[] l = arg.split(delRegex);
		List<String> newList = new ArrayList<String>();
		for( int i = 0; i < l.length ; i++){
			if( l[i].trim().length() > 0){
				newList.add(l[i].trim());
			}
		}
		return newList;
	} 

	public static String generateDelimitedStringFromList(
			char delimiter, ArrayList<String> l){

		if( l.size() == 0)
			return " ";
		String retvalString = l.get(0);

		for( int i = 1; i < l.size(); i++){
			retvalString += delimiter + l.get(i);
		}
		return retvalString;
	}

	public static String generateDelimitedStringFromList(
			String delimiter, ArrayList<String> l){

		if( l.size() == 0)
			return " ";
		String retvalString = l.get(0);

		for( int i = 1; i < l.size(); i++){
			retvalString += delimiter + l.get(i);
		}
		return retvalString;
	}

	public static String printStringList( List<String> s){

		String retString = "[";
		for (String string : s) {
			retString += string+",";
		} 
		retString += "]";
		return retString;
	}

	public static String printStringSet(Set<String> s){
		String retString = "[";
		for (String string : s) {
			retString += string + ",";
		}
		retString += "]";
		return retString;
	}
}

