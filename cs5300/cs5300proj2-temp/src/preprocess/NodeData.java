package preprocess;

// data structure used to represent a node
public class NodeData {
	String nodeID = "";
	String edgeList = "";
	Double pageRank = 0.0;
	Integer degrees = 0;
	
	public void setNodeID(String id) {
		nodeID = id;
	}
	public String getNodeID() {
		return nodeID;
	}
	
	public void setEdgeList(String e) {
		edgeList = e;
	}
	public String getEdgeList() {
		return edgeList;
	}
	
	public void setDegrees(Integer d) {
		degrees = d;
	}
	public Integer getDegrees() {
		return degrees;
	}
	
	public void setPageRank(Double pr) {
		pageRank = pr;
	}
	public Double getPageRank() {
		return pageRank;
	}
}
