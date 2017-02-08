window.onload = function() {
	// keep track of projects
	projects = [];
	activeProject = null;

      var connectionInfo = {
        user:'root',
        name:'oscar15_bc',
        password:'@scar2015', 
        host:'127.0.0.1	'
    }

    /* var connectionInfo = {
        user:'root',
        name:'northwind',
        password:'1234', 
        host:'127.0.0.1'
    }*/

    // Get Request
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            //console.log(xmlHttp.responseText);
            var rowanSchema = JSON.parse(xmlHttp.responseText);
            console.log(rowanSchema.tables);
	    load_list(rowanSchema.tables);
            var schemaDiagram = new SchemaDiagram("schema_diagram", rowanSchema.tables, rowanSchema.relationships);
	}
    }
    xmlHttp.open("POST","http://127.0.0.1:5000/dbSchema", true); // true for asynchronous 
    xmlHttp.setRequestHeader("Content-type", "application/json");
    xmlHttp.send(JSON.stringify(connectionInfo));
	// Hide Cat table
	//schemaDiagram.setTableVisibility('Cat', false);

	// Hide the Poodle attribute of the Dog table
	//schemaDiagram.setAttributeVisibility('Dog', 'Poodle', false);

	// Expand diagram (show tables connected to currently visible tables)
	//schemaDiagram.expandVisibleTables()

	// Set the diagram layout to Circular
	//schemaDiagram.setLayout("circular");

	// Export the diagram (commented out so it doesn't prompt for download when you load the page)
	// If no filename is provided, the default of "diagram.png" will be used
	// schemaDiagram.export("oscar.png");

	// Create a Go.js diagram with test data
	/*testTables = 
		[
			{
				name: "Cat",
				primary_keys: [
					"American Bobtail"
				],
				foreign_keys: [
					"Fuzzy Lop"
				],
				attributes: [
					"American Shorthair",
					"American Wirehair",
					"Balinese",
					"Bengal",
					"Birman",
					"Bombay",
				]
			},
			{
				name: "Rabbit",
				primary_keys: [
					"Fuzzy Lop",
					"Sable"
				],
				attributes: [
					"Angora",
					"Beveren",
					"Britannia Petite",
					"California",
					"Checkered Giant",
					"Cinnamon",
					"Dutch",
					"English Spot",
					"Flemish Giant"
				]
			},
			{
				name: "Dog",
				primary_keys: [
					"Doge"
				],
				foreign_keys: [
					"Sable",
					"American Bobtail"
				],
				attributes: [
					"Siberian Husky",
					"Shiba Inu",
					"Poodle",
					"Golden Retriever",
					"Labdradoodle"
				]
			},
			{
				name: "Lizard",
				foreign_keys: [
					"Doge"
				],
				attributes: [
					"Veiled Chameleon",
					"Water Monitor",
					"Satanic Leaf Tailed Gecko"
				]
			}
		]

	testRelationships =
		[
			{ from: "Cat", to: "Rabbit", text: "0..N", toText: "1" },
			{ from: "Cat", to: "Rabbit", text: "2..N", toText: "2" },
			{ from: "Dog", to: "Cat", text: "1", toText: "2"},
			{ from: "Rabbit", to: "Dog", text: "1", toText: "1"},
			{ from: "Lizard", to: "Dog", text: "2..3", toText: "1"}
		]*/

	

	document.getElementById('save-project-button').onclick = addProject;

	document.getElementById('expand-button').onclick = function() {
		activeProject.diagram.expandSelectedTable();
	}

	document.getElementById('download-button').onclick = function() {
		activeProject.diagram.export();
	}

	// TODO - the Layout dropdown needs to call activeDiagram.diagram.setLayout() for whatever layout is selected from the dropdown. See the function comments in schema_diagram.js for how to use the setLayout function
};

// TODO - don't let projects be added if the name exists already in the projects array
function addProject() {
	var form = document.getElementById('add-project-form');
	var project = new Project(
		name = form.project_name.value,
		db_name = form.db_name.value,
		user = form.username.value,
		password = form.password.value,
		host = form.host.value,
		port = form.port.value
	)
	projects.push(project)

	var div = document.createElement('div');
	div.id = project.divId;
	document.getElementById('schema_diagrams').appendChild(div);

	var table = document.getElementById('projects-table');

	var row = document.createElement('tr');
	row.setAttribute('projectdivid', project.divId);

	// Project Name
	var cell = document.createElement('td');
	var a = document.createElement('a');
	a.href = '#';
	var text = document.createTextNode(project.name);
	cell.onclick = function() {
		setActiveProject(project.id);
	}

	a.appendChild(text);
	cell.appendChild(a);
	row.appendChild(cell);

	// Edit and Delete buttons
	// TODO - Edit should let you change the name of the project
	// TODO - Delete should remove the project from the projects array, the row in the projects-table table and the div in the schema_diagrams div
	cell = document.createElement('td');
	cell.innerHTML = '<button class="btn btn-xl"><i class="glyphicon glyphicon-pencil"></i></button><button class="btn btn-xl"><i class="glyphicon glyphicon-trash"></i></button>';

	row.appendChild(cell);
	table.appendChild(row);

	setActiveProject(project.id);
}

function setActiveProject(projectId) {
	activeProject = _.find(projects, function(project) {
		return project.id == projectId;
	})

	// Highlight the table row with the active project
	_.each(document.getElementById('projects-table').childNodes, function(row) {
		if (row.getAttribute('projectdivid') == activeProject.divId) {
			row.setAttribute('class', 'bg-success');
		} else {
			row.setAttribute('class', '');
		}
	})

	// Only show the div with the active project diagram
	_.each(document.getElementById('schema_diagrams').childNodes, function(node) {
		node.style.display = 'none';
	})
	document.getElementById(activeProject.divId).style.display = 'block';
}

function load_list(tables){
	console.log(tables.length);	

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

		console.log("Name " + tables[i].name);
		var h2 = document.createElement('h2');
		h2.innerHTML = tables[i].name;

		a.appendChild(h2);

		var div_table = document.createElement('div');
		item.appendChild(div_table);
		div_table.className = "detail";

		// Creates table
		var table = document.createElement('table');

		for(var n=0; n<tables[i].attributes.length; n++) {
			console.log(tables[i].attributes);
			var row = table.insertRow(-1);

			var cell1 = row.insertCell(0);

			cell1.innerHTML = tables[i].attributes[n];
		}
		div_table.appendChild(table);
	}

	$(function() {
		$(".expand").on( "click", function() {
			$(this).next().slideToggle(200);
			$expand = $(this).find(">:first-child");

			if($expand.text() == "+") {
				$expand.text("-");
			} else {
				$expand.text("+");
			}
		});
	});
}
