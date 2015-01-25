package preprocess;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;


/**
 * @author Piyush
 *
 */
public class PreprocessInput {
	
	
	public static void init_constant( int netid){
		
		Constants.REJECT_MIN = (.99 * netid) /1000;	
		Constants.REJECT_LIMIT = Constants.REJECT_MIN + .01;
		
		System.out.println(Constants.REJECT_MIN);
		System.out.println(Constants.REJECT_LIMIT);
	}
	
	public static void main(String[] args) throws IOException {

		try{
			//System.out.println(java.lang.Runtime.getRuntime().maxMemory()); 
			//746
			init_constant(984);
			createFilteredEdgesFile("tmp/edges.txt", "tmp/randomedgesample.txt");
			createPreprocessedInputFile("tmp/randomedgesample.txt", "tmp/new_mapperinput.txt");
			
		}catch(Exception e){
			e.printStackTrace();
		}
			
	}

	//this is just used to create a randoms sample of the edges
	public static void createFilteredEdgesFile(
			String inPath,
			String outPath) throws NumberFormatException, IOException{
			 
		File inputFile = new File(inPath);
		File file = new File(outPath);  
		BufferedReader reader = new BufferedReader(new FileReader(inputFile));
		Writer writer = new OutputStreamWriter(new FileOutputStream(file));
		String line;
		String[] parts;
		double randVal;
		int edgeCount = 0;
		while ((line = reader.readLine()) != null) {          
			  parts = line.trim().split("\\s+");
		     randVal = Double.parseDouble(parts[2]);
		     if (selectInputLine(randVal)){
		          //System.out.println(line); 
		          edgeCount++;
		          writer.write(line + "\n");
		     }else {
				//System.out.println("Edge rejected");
			}
		}
		writer.close();
		reader.close();
		System.out.println("Edge count:"+edgeCount);
	}
	

	
	private static boolean selectInputLine(double x) {
		return ( ((x >= Constants.REJECT_MIN) && (x < Constants.REJECT_LIMIT)) ? false : true );
	}
	
	public static void createPreprocessedInputFile(String inPath,String outPath) throws IOException{
		
		File inFile = new File(inPath); 
		//File inFile = new File("test"); 
		File outFile = new File(outPath);      
		BufferedReader reader = new BufferedReader(new FileReader(inFile));
		FileWriter fw = new FileWriter(outFile);
		BufferedWriter bw = new BufferedWriter(fw);
		String line;
		String[] parts;
		int oldnode;
		int currentNode;
		line = reader.readLine();
		parts = line.trim().split("\\s+");
		oldnode = Integer.parseInt(parts[0]);
		List<Integer> outNodes = new ArrayList<Integer>();
		StringBuilder sb;
		HashMap<Integer, Boolean> usednodesHashMap = new HashMap<Integer, Boolean>();
		while ((line = reader.readLine()) != null) {      
			  parts = line.trim().split("\\s+");
			  currentNode = Integer.parseInt(parts[0]);
			  if(oldnode != currentNode){
				  usednodesHashMap.put(oldnode, true);
				  sb = new StringBuilder();
				  for(int i=0;i<outNodes.size()-1;i++){
					  sb.append(outNodes.get(i)).append(",");
				  }
				  sb.append(outNodes.get(outNodes.size()-1));
				  bw.write(oldnode+" "+Constants.INIT_PR+" "+outNodes.size()+" "+sb.toString()+"\n");
				  oldnode = currentNode;
				  outNodes = new ArrayList<Integer>();
				  outNodes.add(Integer.parseInt(parts[1]));
				  
			  }else{
				  outNodes.add(Integer.parseInt(parts[1]));
			  }
			
		}
		sb = new StringBuilder();
		for(int i=0;i<outNodes.size()-1;i++){
			sb.append(outNodes.get(i)).append(",");
		}
		sb.append(outNodes.get(outNodes.size()-1));
		bw.write(oldnode+" "+Constants.INIT_PR+" "+outNodes.size()+" "+sb.toString()+"\n");
		usednodesHashMap.put(oldnode, true);
		
		for( int i = 0 ; i < Constants.TOTAL_NODES ; i++){
			if( ! usednodesHashMap.containsKey(i)){
				bw.write(i +  " " + Constants.INIT_PR + "\n" );
			}
		}
		
		bw.close();
		reader.close();
	}
	
}
