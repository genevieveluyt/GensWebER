window.onload = function() {
	// keep track of projects
	projects = [];
	activeProject = null;

    /* var connectionInfo = {
        user:'root',
        name:'northwind',
        password:'1234', 
        host:'127.0.0.1'
    }*/

	document.getElementById('save-project-button').onclick = function() {
		addProject();
	}

	document.getElementById('expand-button').onclick = function() {
		activeProject.diagram.expandSelectedTable();
	}

	document.getElementById('download-button').onclick = function() {
		activeProject.diagram.export();
	}

	
	// TODO - the Layout dropdown needs to call activeDiagram.diagram.setLayout() 
	// for whatever layout is selected from the dropdown. 
	// See the function comments in schema_diagram.js for how to use the setLayout function
	// Hunter
	var l = document.getElementById('layout');
	l.onchange = function() {
		console.log("Changed layout to " + l.options[l.selectedIndex].value);
		activeProject.diagram.setLayout(l.options[l.selectedIndex].value);
	}
	// End Hunter

};


function addProject() {
	var form = document.getElementById('add-project-form');
	
	// TODO - don't let projects be added if the name exists already in the projects array
	// Hunter
	var uniqueName = true;
	for(i=0; i < projects.length; i++) {
		if(form.project_name.value == projects[i].name) {
			repeatedName = false;
		}
	}
	if(uniqueName) {
	// End Hunter

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
		cell.innerHTML = '<button class="btn btn-xl edit-button"><i class="glyphicon glyphicon-pencil"></i></button><button class="btn btn-xl delete-button"><i class="glyphicon glyphicon-trash"></i></button>';

		row.appendChild(cell);
		table.appendChild(row);

		setActiveProject(project.id);
	}
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

	// Load the list of tables
	if (activeProject.data) {
		activeProject.load_list(activeProject.data.tables);
	}
}

function toggleTable(id) {
	console.log(id);
}

/*function load_list(tables){
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

		var h2 = document.createElement('h2');
		h2.innerHTML = tables[i].name;
		a.appendChild(h2);
		
		var tog = document.createElement('button');
		tog.innerHTML = "Hide";
		tog.onclick = function(evt) {
					console.log(tables[i].name);
					activeProject.diagram.setTableVisibility(tables[i].name, false);
				};
		/*if (typeof window.addEventListener === 'function') {
			(function (_tog) {
				tog.addEventListener('click', function() {
					console.log(tables[i].name);
					activeProject.setTableVisibility(tables[i].name, false);
				});
			}) (tog);
		}*//*

		a.appendChild(tog);

		var div_table = document.createElement('div');
		item.appendChild(div_table);
		div_table.className = "detail";

		// Creates table
		var table = document.createElement('table');

		for(var n=0; n<tables[i].attributes.length; n++) {
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
	});*/
//}
