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
	//schemaDiagram = new SchemaDiagram("schema_diagram", testTables, testRelationships);
    
    var connectionInfo = {
        user:'root',
        name:'northwind',
        password:'1234', 
        host:'127.0.0.1'
    }

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            //console.log(xmlHttp.responseText);
            var rowanSchema = JSON.parse(xmlHttp.responseText);
            console.log(rowanSchema.tables);
            schemaDiagram = new SchemaDiagram("big_ol_div", rowanSchema.tables, rowanSchema.relationships);
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
}
