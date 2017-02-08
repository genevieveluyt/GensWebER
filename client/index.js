window.onload = function() {

	// keep track of projects
	projects = [];
	activeProject = null;

	// Create a Go.js diagram with test data
	testTables = 
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
		]

	

	document.getElementById('save-project-button').onclick = addProject;

	document.getElementById('expand-button').onclick = function() {
		activeProject.diagram.expandSelectedTable();
	}

	document.getElementById('download-button').onclick = function() {
		activeProject.diagram.export();
	}
}

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