package cs5300.proj1b.managers;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.logging.Logger;

import cs5300.proj1a.objects.HostInformation;
import cs5300.proj1a.objects.ServerView;
import cs5300.proj1a.servelets.WebServer;
import cs5300.proj1a.utils.Utils;

//Author - Piyush

public class ServerViewManager {

	public static final String SIMPLE_DB_DELIMITER = "_";
	public static final String REGEX_SIMPLE_DB_DELIMITER = "_";
	public static final String NETWORK_VIEW_DELIMITER = "_";
	public static final String REGEX_NETWORK_VIEW_DELIMITER = "_";
	public static final int VIEW_SIZE = 5;
	public static final String NULL_SERVER = "0.0.0.0";
	private ServerView serverView;

	private Logger LOGGER = Logger.getLogger(ServerViewManager.class.getName());
	
	public ServerViewManager() {
		this.serverView = new ServerView();
	}

	public Set<String> getServerViewSet(){
		return this.serverView.getServerSet();
	}

	public ArrayList<String> getServerViewList(){
		return new ArrayList<String>(this.serverView.getServerSet());
	}

	public Set<String> shrinkView(Set<String> s, int size){

		List<String> list = new ArrayList<String>(s);
		
		if ( list.size() > size){
			Collections.shuffle(list);
			list = list.subList(0, size);
		}
		return new HashSet<String>(list);    
	}

	public Set<String> removeFromView(Set<String> s, String str){
		
		//Set<String> retSet = new HashSet<String>();
		s.remove(str);
		return s;
	}

	public Set<String> addToView(Set<String> view, String server){
		Set<String> serverSet =  new HashSet<String>();
		serverSet.add(server);
		return unionView(view, serverSet);
	}

	public Set<String> unionView(Set<String> a, Set<String> b){
		Set<String> retset = new HashSet<String>();
		retset.addAll(a);
		retset.addAll(b);
		return retset;
	}

	public void addSelfToBootStrapServer(){

		LOGGER.info("Adding own IP to bootstrap server");
		String bootstrapcontentString  = WebServer.simpleDBManager.getValue();
		List<String> servers = Utils.splitAndTrim(bootstrapcontentString, REGEX_SIMPLE_DB_DELIMITER);		
		LOGGER.info("Received servers : " + Utils.printStringList(servers));
		Set<String> serverSet = new HashSet<String>(servers);
		serverSet = removeFromView(serverSet, NULL_SERVER);
		LOGGER.info("Null removed servers : " + Utils.printStringList(servers));
		serverSet = shrinkView(serverSet, VIEW_SIZE - 1);
		LOGGER.info("Shrunk servers : " + Utils.printStringList(servers));
		serverSet = addToView(serverSet, WebServer.hostInfo.getIPAddress());
		LOGGER.info("Own IP added servers : " + Utils.printStringList(servers));
		
		assert( serverSet.size() <= VIEW_SIZE);
		
		String write = Utils.generateDelimitedStringFromList(SIMPLE_DB_DELIMITER, new ArrayList<String>(serverSet));
		WebServer.simpleDBManager.putValue(write);
	}

	private Set<String> getHostView(String hostname){
		
		String viewstring = WebServer.rpcManager.gossipViewWithHost(hostname);
		
		if( viewstring!= null){
			
			LOGGER.info("View string received from host : " + viewstring);
			List<String> viewList = Utils.splitAndTrim(viewstring, REGEX_NETWORK_VIEW_DELIMITER);
			return new HashSet<String>(viewList);
			
		}else{
			LOGGER.info("Inside ServerViewManager:getHostView : Operation getting "
					+ "host view failed, returning empty set");
			return new HashSet<String>();
		}
	}
	
	private void gossipViewWithHost(String hostname){
		
		LOGGER.info("Gossiping with host : " + hostname);
		Set<String> viewSet = getHostView(hostname);
		if( viewSet.size() == 0 ){
			return;
		}
		
		Set<String> combinedViewSet = unionView(
				viewSet, this.serverView.getServerSet());
		
		combinedViewSet = removeFromView(
				combinedViewSet, WebServer.hostInfo.getIPAddress());
		
		Set<String> prunedCombinedViewSet = new HashSet<String>();
		for (String s : combinedViewSet) {
			if(HostInformation.isValidIP4Address(s)){
				prunedCombinedViewSet.add(s);
			}else{
				LOGGER.info("Incorrect IP found, ignoring : " + s);
			}
		}
		
		Set<String> shrunkSet = shrinkView(prunedCombinedViewSet, VIEW_SIZE);
		this.serverView.setServerSet(shrunkSet);
		LOGGER.info("Updating self view as :" + Utils.printStringSet(
				this.serverView.getServerSet()));
	}
	
	private void gossipWithBootStrapServer(){
		
		LOGGER.info("Gossiping with boot strap server");
		String bootstrapcontentString  = WebServer.simpleDBManager.getValue();
		List<String> servers = Utils.splitAndTrim(bootstrapcontentString, REGEX_SIMPLE_DB_DELIMITER);		
		Set<String> bootServerSet = new HashSet<String>(servers);
		LOGGER.info("Boot strap server set : " + Utils.printStringSet(bootServerSet));
		LOGGER.info("Own IP address is :" + WebServer.hostInfo.getIPAddress());
		bootServerSet = removeFromView(bootServerSet, WebServer.hostInfo.getIPAddress());
		LOGGER.info("Boot strap server set after removing own IP: " + Utils.printStringSet(bootServerSet));
		
		Set<String> combinedviewSet = unionView(bootServerSet, this.serverView.getServerSet());
		LOGGER.info("Combined server set : " + Utils.printStringSet(combinedviewSet));
		combinedviewSet = shrinkView(combinedviewSet, VIEW_SIZE);
		
		Set<String> prunedCombinedViewSet = new HashSet<String>();
		
		for (String s : combinedviewSet) {
			if( HostInformation.isValidIP4Address(s))
				prunedCombinedViewSet.add(s);
			else
				LOGGER.info("Incorrect IP encountered : " + s);
		}
		
		combinedviewSet = prunedCombinedViewSet;
		this.serverView.setServerSet(combinedviewSet);
		
		LOGGER.info("Updating self view as :" + Utils.printStringSet(
				this.serverView.getServerSet()));
		
		combinedviewSet = addToView(combinedviewSet, WebServer.hostInfo.getIPAddress());
		combinedviewSet = shrinkView(combinedviewSet, VIEW_SIZE);
		
		assert( combinedviewSet.size() <= VIEW_SIZE);
		
		String write = Utils.generateDelimitedStringFromList(
				SIMPLE_DB_DELIMITER, new ArrayList<String>(combinedviewSet));
		
		WebServer.simpleDBManager.putValue(write);
		
	}
	
	public void initiateViewGossip(){
		
		LOGGER.info("Initiating periodic view gossip");
		
		int size = this.serverView.getServerSet().size();
		int randomindex =  (int) (Math.random() * (size + 1) );
		
		if( size > 0 && randomindex < size){
			gossipViewWithHost(new ArrayList<String>(
					this.serverView.getServerSet()).get(randomindex));
		}else{
			gossipWithBootStrapServer();
		}
	}
}

