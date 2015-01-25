package com.cs5300.proj2;

/**
 * Represents a single node in the graph
 */
public class Node {
	String nodeID;
	String edgeList;
	double pageRank = 0.0;
	int degree = 0;
	
	/**
	 * Set the nodeID
	 * @param id
	 */
	public void setNodeID(String id) {
		nodeID = id;
	}
	
	/**
	 * Get the nodeID
	 * @return
	 */
	public String getNodeID() {
		return nodeID;
	}
	
	/**
	 * Set the list of nodes to which there are outgoing edges from this node
	 * @param e
	 */
	public void setEdgeList(String e) {
		edgeList = e;
	}
	
	/**
	 * Get the list of nodes to which there are outgoing edges from this node
	 * @return
	 */
	public String getEdgeList() {
		return edgeList;
	}
	
	/**
	 * Set the degree(no of outgoing edges) of this node
	 * @param d
	 */
	public void setDegrees(Integer d) {
		degree = d;
	}
	
	/**
	 * Get the degree(no of outgoing edges) of this node
	 * @return
	 */
	public Integer getDegrees() {
		return degree;
	}
	
	/**
	 * Set the pageRank value for this node
	 * @param pr
	 */
	public void setPageRank(double pr) {
		pageRank = pr;
	}
	
	/**
	 * Get the pageRank for this node
	 * @return
	 */
	public double getPageRank() {
		return pageRank;
	}
}
