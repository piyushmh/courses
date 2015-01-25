package simple;
import java.io.IOException;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;

public class LeMapper extends Mapper<LongWritable, Text, Text, Text> {

	protected void map(LongWritable key, Text value, Context context)
			throws IOException, InterruptedException {
		
		//value is in the format['node','PageRank Estimate','degrees(node)','outgoing edgelist'] delimiter = " "
		
		String line = value.toString();
		line = line.trim();
		String[] temp = line.split("\\s+");
		
		Text node = new Text(temp[0]);
		Float pageRank = new Float(temp[1]);
		Integer degree = new Integer(temp[2]);
		// there may not be any outgoing edges
		String edgeList = "";
		if (temp.length == 4) {
			edgeList = temp[3];
		}
		
		// to pass along previous pageRank and outgoing edgelist
		// map key:node value:PR pageRank <outgoing edgelist>
		Text mapperKey = new Text(node);
		Text mapperValue = new Text("PR " + String.valueOf(pageRank) + " " + edgeList);
		context.write(mapperKey, mapperValue);

		// the pageRankFactor is used by the reducer to calculate the new pageRank for the outgoing edges
		// map key:nodeOut value:pageRankFactor for each outgoing edge
		if (edgeList != "") {	
			Float pageRankFactor = new Float(pageRank/degree);
			mapperValue = new Text(String.valueOf(pageRankFactor));
			String[] edgeListArray = edgeList.split(",");

			for (int i = 0; i < edgeListArray.length; i++) {
				mapperKey = new Text(edgeListArray[i]);
				context.write(mapperKey, mapperValue);
			}
		}
	}
}
