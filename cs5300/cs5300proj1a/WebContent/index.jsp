<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>Project1b</title>
<style type="text/css">
p {color:blue}
</style>
</head>
<body>

<div>

<br/><br/>
<b> Server Id :</b><p id="serverid"></p>
<b> Server Message :</b><p id="servermessage"></p><br/>
<b> Data found on host :</b><p id="datafoundhost"></p><br/>
<b> Primary Host :</b><p id="primaryhost"></p><br/>
<b> Secondary Host : </b><p id="secondaryhost"></p><br/>
<b> Server view :</b><p id="serverview"></p><br/>
<b>Cookie Expiration Time : </b><p id="cookieexptime"></p><br/>
<b>Cookie Discard Time : </b><p id="cookiediscardtime"></p><br/>
<b>Cookie VersionNumber : </b><p id="cookieversionnumber"></p><br/>

<br/><br/>
<button type="button" id ="replace">Replace</button><input type="text" name="message" id="servermessageinput"/>(Message will be truncated after 30 characters)
<br/>
<button type="button" id="refresh">Refresh</button>
<br/>
<button type="button" id="logout">Logout</button>
<br/>
</div>

<script src="js/jquery-2.1.0.min.js"></script>
<script src="js/jquery-ui-1.10.4.custom.min.js"></script>
<script type="text/javascript">

function populate(data){
	
	var response = data.split("|");
	
	var srvmessage = response[8];
	srvmessage = srvmessage.trim(); //this will become empty there was no explicit server message
	
	console.log("Server message : " + srvmessage);
	if( srvmessage.length > 0){
		if( srvmessage == "SESSIONTIMEDOUT"){
			alert("Session timed out, creating a new session");
		}
	}
	
	$("#servermessage").text(response[0].trim());
	$("#cookiediscardtime").text(response[2]);
	$("#cookieexptime").text(response[1]);
	$("#serverid").text(response[4]);
	var repservers = response[5].split(",");
	$("#primaryhost").text(repservers[0]);
	$("#secondaryhost").text(repservers[1]);
	$("#serverview").text(response[6]);
	if( response[7] == -1 || response[7] == 0)
		$("#datafoundhost").text("Primary");
	else
		$("#datafoundhost").text("Secondary");
	$("#cookieversionnumber").text(response[3]);

}

$(function(){
	$.ajax({
		url : "SessionManager",
		type : "GET",
		datatype : "text",
		data : {
			param : "pageload"
		},
		success : function( data, textstatus, jqXHR){
			
			populate(data);
			
		},
		error : function( jqXHR, textstatus, errorThrown){
			alert(errorThrown);
		}
	});
});

$('#refresh').click(function(){
	$.ajax({
		url : "SessionManager",
		type : "GET",
		datatype : "text",
		data : {
			param : "refresh"
		},
		success : function( data, textstatus, jqXHR){
			
			populate(data);
		},
		error : function( jqXHR, textstatus, errorThrown){
			alert(errorThrown);
		}
	});
});

$('#replace').click(function(){
	console.log("Here");
	var newmessage = $('#servermessageinput').val().trim();
	if( newmessage.length == 0 ){
		alert("Message text is empty");
	}else{
		if( newmessage.length > 30){
			newmessage = newmessage.substring(0,29);
		}
		$.ajax({
			url : "SessionManager",
			type : "GET",
			datatype : "text",
			data : {
				param : "replace",
				message : newmessage
			},
			success : function( data, textstatus, jqXHR){
				
				populate(data);
				
			},
			error : function( jqXHR, textstatus, errorThrown){
				alert(errorThrown);
			}
		});	
	}
	
});

$('#logout').click(function(){
	$.ajax({
		url : "SessionManager",
		type : "GET",
		datatype : "text",
		data : {
			param : "logout"
		},
		success : function( data, textstatus, jqXHR){
			
			alert("You have been logged out!");	
			$("#servermessage").text("");
			$("#cookieexptime").text("");
			$("#cookieversionnumber").text("");
			$("#serverid").text("");
			$("#primaryhost").text("");
			$("#secondaryhost").text("");
			$("#serverview").text("");
			$("#datafoundhost").text("");
			$("#cookieversionnumber").text("");
		},
		error : function( jqXHR, textstatus, errorThrown){
			alert(errorThrown);
		}
	});
});



</script>
</body>
</html>