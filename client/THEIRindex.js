window.onload = function() {

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

	// Create a diagram for testTables and testRelationships in the div element with id "schema_diagram"
	// Optionally, pass in the diagram layout as a fourth parameter. One of "circular", "grid", "layered digraph" or "force directed"
	schemaDiagram = new SchemaDiagram("schema_diagram", testTables, testRelationships);

	// Hide Cat table
	schemaDiagram.setTableVisibility('Cat', false);

	// Hide the Poodle attribute of the Dog table
	schemaDiagram.setAttributeVisibility('Dog', 'Poodle', false);

	// Expand diagram (show tables connected to currently visible tables)
	schemaDiagram.expandVisibleTables()

	// Set the diagram layout to Circular
	schemaDiagram.setLayout("circular");

	// Export the diagram (commented out so it doesn't prompt for download when you load the page)
	// If no filename is provided, the default of "diagram.png" will be used
	// schemaDiagram.export("oscar.png");
};

function load_list(tables){
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
			var row = table.insertRow(-1);

			var cell1 = row.insertCell(0);

			cell1.innerHTML = tables[i].attributes[n].name;
			console.log(cell1.innerHTML);
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

	/*for(var i=0; i<tables.length; i++) {
		console.log("Name " + tables[i].name);
		if(_.has(tables[i], "foreign_keys")) {
			for(var m=0; m<tables[i].foreign_keys.length; m++) {
				console.log("Foreign Key " + tables[i].foreign_keys[m].name);
			}
		}
		else {
			console.log("No foreign keys in " + tables[i].name);
		}
		for(var n=0; n<tables[i].attributes.length; n++) {
			console.log(tables[i].attributes[n].name)
		}
	}*/
}
