package cs5300.proj1b.managers;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import cs5300.proj1a.objects.SessionObject;
import cs5300.proj1a.servelets.WebServer;
import cs5300.proj1a.utils.Utils;
import cs5300.proj1b.rpc.RPCClient;

import java.util.logging.*;

public class RPCCommunicationManager {

	private final static Logger LOGGER = Logger.getLogger(RPCCommunicationManager.class.getName());

	private static String NETWORK_DELIMITER = "|";

	private static String REGEX_NETWORK_DELIMITER = "\\|";

	private static int RPC_SERVER_PORT = 5300;

	private static int SESSION_READ_OPCODE = 1;

	private static int SESSION_WRITE_OPCODE = 2;

	private static int VIEW_GOSSIP_OPCODE = 3;

	private static int CONFIRMATION_CODE = 400;


	public String gossipViewWithHost(String server){

		LOGGER.info("Inside RPC Communication Manager: Gossiping with host : " + server);

		String callId = UUID.randomUUID().toString(); 
		String serverString = 
				callId + NETWORK_DELIMITER + VIEW_GOSSIP_OPCODE + NETWORK_DELIMITER ;

		String reply = null;
		try {

			String networkreply = new RPCClient().callServer(server, RPC_SERVER_PORT, serverString, callId);	
			LOGGER.info("String received from server : " + networkreply);
			if( networkreply != null){
				List<String> networkReplyList = Utils.splitAndTrim(networkreply, REGEX_NETWORK_DELIMITER);
				reply = networkReplyList.get(1);
			}

		} catch (IOException e) {
			e.printStackTrace();
		}

		return reply;
	}

	public boolean replicateSession(
			SessionObject object, 
			String replicaserver){

		LOGGER.info("Replicating session id : " + object.getSessionId() + 
				" on server : " + replicaserver);

		boolean retval = false;
		String callId = UUID.randomUUID().toString(); //callID
		String serverstring = 
				callId + 				NETWORK_DELIMITER +
				SESSION_WRITE_OPCODE +  NETWORK_DELIMITER + 
				object.getSessionId() + NETWORK_DELIMITER +
				object.getMessage() + 	NETWORK_DELIMITER + 
				object.getVersion() + 	NETWORK_DELIMITER + 
				object.getExpirationTimeMilliSecond()  + NETWORK_DELIMITER ;

		try {

			String reply = new RPCClient().callServer(replicaserver, RPC_SERVER_PORT, serverstring, callId);	
			LOGGER.info("String received from server : " + reply);
			if( reply!= null){
				String[] list = reply.split(REGEX_NETWORK_DELIMITER);

				LOGGER.info(Utils.printStringList(Arrays.asList(list)));

				if( 400 == Integer.parseInt(list[1].trim())){
					retval = true;
				}

			}else{
				LOGGER.info("Replication failed on server : " + replicaserver);
			}

		} catch (IOException e) {
			e.printStackTrace();
		}

		return retval;
	}

	/* Returns NULL if can't connect
	 * Returns NULL if exception if thrown
	 */
	public SessionObject sessionRead( String hostname, String sessionid, int version){

		SessionObject object = null;
		try{
			String callID = UUID.randomUUID().toString();
			String send= callID + NETWORK_DELIMITER + SESSION_READ_OPCODE + NETWORK_DELIMITER + 
					sessionid +  NETWORK_DELIMITER + version;
			String outputString = new RPCClient().callServer(hostname, RPC_SERVER_PORT, send, callID);

			if( outputString != null){

				//EXPECTING FORMAT - CALLID|VERSION|MESSAGE|EXPIRATIONDATE

				String[] list = outputString.split(REGEX_NETWORK_DELIMITER);

				LOGGER.info("Inside session read : " + Utils.printStringList(Arrays.asList(list)));

				if( Integer.parseInt(list[1].trim()) != -1){

					object = new SessionObject();
					assert( version == Integer.parseInt(list[1]));
					object.setVersion(version);
					object.setSessionId(sessionid);
					object.setMessage(list[2]);
					object.setExpirationTime(Long.parseLong(list[3].trim()));
				}else {
					LOGGER.info("Inside session read : Invalid version number received from server");
				}
			}
		}catch(IOException e){
			e.printStackTrace();
		}
		return object;
	}

	public String replyToClient( String s){

		LOGGER.info("String received from client : " + s);
		List<String> list = Utils.splitAndTrim(s, REGEX_NETWORK_DELIMITER);

		LOGGER.info(Utils.printStringList(list));

		String retvalString = list.get(0); //return the same call id

		int opcode = Integer.parseInt(list.get(1).trim());

		if( opcode == SESSION_READ_OPCODE){

			//EXPECTED FORMAT - CALLID|OPCODE|SESSIONID|VERSION|

			SessionObject object = WebServer.sessionTable.concurrentHashMap.get(list.get(2));
			if(object != null && (object.getVersion() == Integer.parseInt(list.get(3).trim()))){
				retvalString += NETWORK_DELIMITER + object.getVersion() + NETWORK_DELIMITER + object.getMessage()
						+ NETWORK_DELIMITER + object.getExpirationTimeMilliSecond() + NETWORK_DELIMITER;

			}else{

				retvalString += NETWORK_DELIMITER + -1 + NETWORK_DELIMITER + "Dummy" + 
						NETWORK_DELIMITER + -1 + NETWORK_DELIMITER;
			}

		}else if ( opcode == SESSION_WRITE_OPCODE){

			//EXPECTED FORMAT - CALLID|OPCODE|SESSIONID|MESSAGE|VERSION|EXPIRATIONDATE

			SessionObject sessionObject = new SessionObject();
			sessionObject.setSessionId(list.get(2).trim());
			sessionObject.setMessage(list.get(3).trim());
			sessionObject.setVersion(Integer.parseInt(list.get(4).trim()));
			sessionObject.setExpirationTime(Long.parseLong(list.get(5).trim()));

			WebServer.sessionManager.addSessionLocally(sessionObject, WebServer.sessionTable);
			retvalString += NETWORK_DELIMITER + CONFIRMATION_CODE + NETWORK_DELIMITER;

		} else if( opcode == VIEW_GOSSIP_OPCODE){

			//EXPECTEDFORMAT = CALLID|OPCODE

			Set<String> selfviewSet = WebServer.viewManager.getServerViewSet();
			retvalString += NETWORK_DELIMITER + Utils.generateDelimitedStringFromList(
					ServerViewManager.NETWORK_VIEW_DELIMITER , new ArrayList<String>(selfviewSet)) 
					+ NETWORK_DELIMITER;
		}

		LOGGER.info("String returning to client : " + retvalString);
		return retvalString;
	}
}
