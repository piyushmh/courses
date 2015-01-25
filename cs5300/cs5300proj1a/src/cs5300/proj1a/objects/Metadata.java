package cs5300.proj1a.objects;

import java.util.ArrayList;

public class Metadata {

	private SessionObject sessionObject;
	private int servernum;
	private ArrayList<String> replicatedServers;


	public Metadata(SessionObject sessionObject, int servernum, ArrayList<String> replicatedServers) {
		super();
		this.setSessionObject(sessionObject);
		this.servernum = servernum;
		this.replicatedServers = replicatedServers;
	}

	
	
	public int getServernum() {
		return servernum;
	}

	public void setServernum(int servernum) {
		this.servernum = servernum;
	}

	public SessionObject getSessionObject() {
		return sessionObject;
	}

	public void setSessionObject(SessionObject sessionObject) {
		this.sessionObject = sessionObject;
	}

	public ArrayList<String> getReplicatedServers() {
		return replicatedServers;
	}

	public void setReplicatedServers(ArrayList<String> replicatedServers) {
		this.replicatedServers = replicatedServers;
	}
}
