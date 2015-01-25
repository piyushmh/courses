package simple;

import java.io.IOException;
import java.util.*;

import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;

public class LeReducer extends Reducer<Text, Text, Text, Text> {

	protected void reduce(Text key, Iterable<Text> values, Context context)
			throws IOException, InterruptedException {
		
		// format of each incoming value is either: <pageRankFactor>
		// this gives the pageRankFactor (pageRank/degrees) for each node pointing to the key node
		// or it could be: PR <prevPageRank> <outgoingEdgeList>
		Iterator<Text> itr = values.iterator();
		Text input = new Text();
		String[] inputTokens = null;
		
		Float pageRankIncomingSum = (float) 0.0;
		Float dampingFactor = (float) 0.85;
		Float randomJumpFactor = (1 - dampingFactor) / NodeDriver.totalNodes;
		
		Float pageRankNew = (float) 0.0;
		Float pageRankOld = (float) 0.0;
		Float residualError = (float) 0.0;
		
		String edgeList = "";
		String output = "";

		while (itr.hasNext()) {
			input = itr.next();
			inputTokens = input.toString().split("\\s+");			
			// if 3 elements, it is the previous pagerank and outgoing edgelist for this node
			if (inputTokens[0].equals("PR")) {
				pageRankOld = Float.parseFloat(inputTokens[1]);
				if (inputTokens.length == 3) {
					edgeList = inputTokens[2];
				} else {
					edgeList = "";
				}
			// otherwise it is the pageRankFactor for the incoming node
			} else {
				Float pageRankFactor = new Float(Float.parseFloat(inputTokens[0]));
				pageRankIncomingSum += pageRankFactor;
			}
			
		}
		
		// compute pageRankNew:
		// 	pageRankNew = dampingFactor * (sum(pageRank[v]/degrees[v])) + (1 - dampingFactor)/N
		pageRankNew = (dampingFactor * pageRankIncomingSum) + randomJumpFactor;
		
		// compute the residual error for this node
		residualError = Math.abs(pageRankOld - pageRankNew) / pageRankNew;
		
		// add the residual error to the counter that is tracking the overall sum (must be expressed as a long value)
		long residualAsLong = (long) Math.floor(residualError * NodeDriver.precision);
		context.getCounter(NodeDriver.ProjectCounters.RESIDUAL_ERROR).increment(residualAsLong);
		
		// output should be 
		//	key:nodeID (for this node)
		//	value:<pageRankNew> <degrees> <comma-separated outgoing edgeList>		
		Integer degrees = new Integer(edgeList.split(",").length);
		output = pageRankNew + " " + degrees.toString() + " " + edgeList;

		Text outputText = new Text(output);

		context.write(key, outputText);
	}

}
