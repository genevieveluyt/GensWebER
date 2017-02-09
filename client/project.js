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
		this.getSchema();
	}

	generateDivId() {
		return "schema_" + this.id;
	}

	getSchema() {
		var project = this;
		var xmlHttp = new XMLHttpRequest();
	    xmlHttp.onreadystatechange = function() { 
	        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
	            project.data = JSON.parse(xmlHttp.responseText);
	            project.diagram = new SchemaDiagram(project.divId, project.data.tables, project.data.relationships);
		    project.load_list();
	        }
	    }
	    xmlHttp.open("POST","http://127.0.0.1:5000/dbSchema", true); // true for asynchronous 
	    xmlHttp.setRequestHeader("Content-type", "application/json");
	    xmlHttp.send(JSON.stringify(this.connectionInfo));
	}

	load_list(){
		var tables = this.data.tables;

		// Creates list
		var list = document.getElementById('accordion');

		for(var i = 0; i < tables.length; i++) {
			var item = document.createElement('li');
			list.appendChild(item);

			var a = document.createElement('a');
			item.appendChild(a);
			a.className = "expand";

			var div = document.createElement('div');
			a.appendChild(div);
			div.className = "right-arrow";
			div.innerHTML = "+";

			var h2 = document.createElement('h2');
			h2.innerHTML = tables[i].name;
			a.appendChild(h2);
		
			var tog = document.createElement('button');
			tog.setAttribute('table', tables[i].name);
			tog.innerHTML = "Hide/Show";
			tog.onclick = function(evt) {
				var tableName = evt.target.getAttribute('table');
				if(activeProject.diagram.isTableVisible(tableName)) {
					activeProject.diagram.setTableVisibility(tableName, false);
				} else {
					activeProject.diagram.setTableVisibility(tableName, true);
					
				}
			};
			a.appendChild(tog);

			var div_table = document.createElement('div');
			item.appendChild(div_table);
			div_table.className = "detail";

			// Creates table
			var table = document.createElement('table');

			for(var n=0; n<tables[i].attributes.length; n++) {
				var row = table.insertRow(-1);

				var cell1 = row.insertCell(0);
				cell1.setAttribute('tableName', tables[i].name);
				cell1.setAttribute('attributeName', tables[i].attributes[n].name);
				cell1.innerHTML = tables[i].attributes[n].name + " (Hide/Show)";
				cell1.onclick = function(evt) {
					var tableName = evt.target.getAttribute('tableName');
					var attributeName = evt.target.getAttribute('attributeName');
					// visible --> hidden
					if(activeProject.diagram.isAttributeVisible(tableName, attributeName)) {
						activeProject.diagram.setAttributeVisibility(tableName, attributeName, false);
					}
					// hidden --> vissible
					else {
						activeProject.diagram.setAttributeVisibility(tableName, attributeName, true);
					}
				};
			};
			div_table.appendChild(table);
		}

		$(function() {
			$(".expand").on( "click", function(evt) {
				if(evt.target.tagName === "BUTTON") {
					return;
				} else {
					$(this).next().slideToggle(200);
					var $expand = $(this).find(">:first-child");

					if($expand.text() == "+") {
						$expand.text("-");
					} else {
						$expand.text("+");
					}
				}
			});
		});
	}
}
