package cs5300.proj1a.sessiontable;

import java.util.concurrent.ConcurrentHashMap;

import cs5300.proj1a.objects.SessionObject;

public class SessionTable {

public ConcurrentHashMap<String, SessionObject> concurrentHashMap;
	
	public SessionTable(){
		super();
		this.concurrentHashMap = new ConcurrentHashMap<String, SessionObject>();
	}

	public SessionObject putSession(String key, SessionObject value) {
		return this.concurrentHashMap.put(key, value);
	}

	public SessionObject getSession(String sessionid, int version_number) {
		
		SessionObject object =  this.concurrentHashMap.get(sessionid);
		if( object!= null){
			if( object.getVersion() < version_number){
				assert(false);
			}
		}
		return object;
	}

	public void deleteObject(String key) {
		this.concurrentHashMap.remove(key);		
	}

	public int getSize() {
		return this.concurrentHashMap.size();
	}
}
