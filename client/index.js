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
		row.id = name;

		// Project Name
		var cell = document.createElement('td');
		var a = document.createElement('a');
		a.href = '#';
		a.id="cell_"+project.id;
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
		cell1 = document.createElement('td');
		cell1.innerHTML = '<button class="btn btn-xl edit-button"><i class="glyphicon glyphicon-pencil"></i></button>';		
		cell1.onclick = function() {
			editRow(project.id);		
		}
		cell1.width = '40px';
		cell2 = document.createElement('td');
		cell2.innerHTML = '<button class="btn btn-xl delete-button"><i class="glyphicon glyphicon-trash"></i></button>';	
		cell2.onclick = function() {
			deleteRow(row.id, div.id, project.id);		
		}
		cell2.width = '40px';
		row.appendChild(cell1);
		row.appendChild(cell2);
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

function deleteRow(rowId, divId, projectId) {
	var div = document.getElementById(divId);
	div.parentNode.removeChild(div);	
	var row = document.getElementById(rowId);
	row.parentNode.removeChild(row);	
	for(i=0; i < projects.length; i++) {
		if(projectId == projects[i].id) {
			projects.slice[i,1];
		}
	}
}
function editRow(cellId) {
	console.log(document.getElementById("cell_"+cellId).innerHTML);
}


function toggleTable(id) {
	console.log(id);
}
