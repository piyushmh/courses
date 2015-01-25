package cs5300.proj1a.objects;

import java.util.HashSet;
import java.util.Set;

public class ServerView {
	
	private Set<String> serverSet;

	public ServerView() {
		this.serverSet = new HashSet<String>();
	}
	public Set<String> getServerSet() {
		return serverSet;
	}

	public void setServerSet(Set<String> serverSet) {
		this.serverSet = serverSet;
	}
	
	
}
