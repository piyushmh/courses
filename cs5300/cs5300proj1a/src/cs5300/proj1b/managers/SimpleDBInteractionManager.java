package cs5300.proj1b.managers;


import java.util.logging.Logger;

import com.amazonaws.auth.ClasspathPropertiesFileCredentialsProvider;
import com.amazonaws.regions.Region;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.simpledb.AmazonSimpleDBClient;
import com.amazonaws.services.simpledb.model.Attribute;
import com.amazonaws.services.simpledb.model.Item;
import com.amazonaws.services.simpledb.model.PutAttributesRequest;
import com.amazonaws.services.simpledb.model.ReplaceableAttribute;
import com.amazonaws.services.simpledb.model.SelectRequest;

public class SimpleDBInteractionManager {

	private static final String simpleDBDomain = "Project1b";
	private static final String itemKey = "bootstrapItem";
	private static final String attributeKey = "bootstrapView";
	private AmazonSimpleDBClient sdb; 
	private Logger logger = Logger.getLogger(SimpleDBInteractionManager.class.getName());
	
	public SimpleDBInteractionManager(){

		try {
			sdb = new AmazonSimpleDBClient(
					new ClasspathPropertiesFileCredentialsProvider());
			Region usWest2 = Region.getRegion(Regions.US_WEST_2); //Oregon
			sdb.setRegion(usWest2);
			
		} catch (Exception e) {
			e.printStackTrace();
			sdb = null;
		}
	}

	public boolean putValue(String arg){

		logger.info("Writing to simple DB : " + arg);
		ReplaceableAttribute replaceableAttribute = new ReplaceableAttribute()
		.withName(attributeKey)
		.withValue(arg)
		.withReplace(true);

		sdb.putAttributes(new PutAttributesRequest().withDomainName(simpleDBDomain)
				.withItemName(itemKey)
				.withAttributes(replaceableAttribute));
		
		return true;
	}

	public String getValue(){
		
		String retval = "";
		String selectExpression = "select * from `" + simpleDBDomain + "`";
		SelectRequest selectRequest = new SelectRequest(selectExpression);
		for(Item item : sdb.select(selectRequest).getItems()){
			for (Attribute attribute : item.getAttributes()) {
				if(attribute.getName().equals(attributeKey)){
					retval = attribute.getValue();
					break;
				}
			}
		}
		logger.info("Read from simple DB : " + retval);
		return retval;
	}
}
