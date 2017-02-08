var projectIdCounter = 1;

class Project {
	constructor(name, db_name, user, password, host, port) {
		this.id = projectIdCounter++;
		this.name = name;
		this.connectionInfo = {
			name: db_name,
		 	user: user,
			password: password,
			host: host,
			port: port
		}
		this.divId = this.generateDivId();
		this.getSchema(this.divId);
	}

	generateDivId() {
		return "schema_" + this.id;
	}

	getSchema() {
		var xmlHttp = new XMLHttpRequest();
	    xmlHttp.onreadystatechange = function() { 
	        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
	            var data = JSON.parse(xmlHttp.responseText);
	            this.diagram = new SchemaDiagram(this.divId, data.tables, data.relationships);
	        }
	    }
	    xmlHttp.open("POST","http://127.0.0.1:5000/dbSchema", true); // true for asynchronous 
	    xmlHttp.setRequestHeader("Content-type", "application/json");
	    xmlHttp.send(JSON.stringify(this.connectionInfo));
	}
}