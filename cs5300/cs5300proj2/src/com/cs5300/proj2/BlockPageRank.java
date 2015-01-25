package com.cs5300.proj2;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class BlockPageRank {

	/*This is the counter that we are using for calculating residual values*/
	public static enum ProjectCounters {
		RESIDUAL_ERROR
	};
	
	public static final int totalNodes = 685230;	// total # of nodes in the input set
	public static final int totalBlocks = 68;	// total # of blocks
	public static final int precision = 10000;	// this allows us to store the residual error value in the counter as a long
	private static final Double thresholdError = 0.001;	// the threshold to determine whether or not we have converged

	public static void main(String[] args) throws Exception {

		String inputFile = "tmp/mapperinput.txt"; //this is the pruned edge set
		String outputPath = "tmp/final_output"; //final output folder, this called by passed using command line as well
		
		int i = 0;
		
		double residualErrorAvg = 0.0;

		// iterate to convergence 
		do {
			Job job = new Job();
		
			// Set a unique job name
			job.setJobName("prBlock_"+ (i+1));
			job.setJarByClass(com.cs5300.proj2.BlockPageRank.class);

			// Set Mapper and Reducer class
			job.setMapperClass(BlockPageRankMapper.class);
			job.setReducerClass(BlockPageRankReducer.class);

			// set the classes for output key and value
			job.setOutputKeyClass(Text.class);
			job.setOutputValueClass(Text.class);

			// on the initial pass, use the pre-processed input file
			if (i == 0) {
				FileInputFormat.addInputPath(job, new Path(inputFile)); 	
				// otherwise use the output of the last pass as our input
			} else {
				FileInputFormat.addInputPath(job, new Path(outputPath + "/temp"+i)); 
			}
			// set the output file path
			FileOutputFormat.setOutputPath(job, new Path(outputPath + "/temp"+(i+1)));

			// execute the job and wait for completion before starting the next pass
			job.waitForCompletion(true);

			// before starting the next pass, compute the avg residual error for this pass and print it out
			residualErrorAvg = (double) job.getCounters().findCounter(ProjectCounters.RESIDUAL_ERROR).getValue(); 
			residualErrorAvg = residualErrorAvg / Constants.RESIDUAL_OFFSET;
			
			residualErrorAvg = residualErrorAvg/ totalBlocks; //take average across all blocks
			String residualErrorString = String.format("%.4f", residualErrorAvg);
			System.out.println("Residual error for iteration " + i + ": " + residualErrorString);

			// reset the counter for the next round
			job.getCounters().findCounter(ProjectCounters.RESIDUAL_ERROR).setValue(0L);
			i++;
		} while (residualErrorAvg > thresholdError);

	}
}

