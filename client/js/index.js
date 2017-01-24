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
			}
		]

	testRelationships =
		[
			{ from: "Cat", to: "Rabbit", text: "0..N", toText: "1" },
			{ from: "Cat", to: "Rabbit", text: "2..N", toText: "2" },
			{ from: "Dog", to: "Cat", text: "1", toText: "2"},
			{ from: "Rabbit", to: "Dog", text: "1", toText: "1"}
		]

	schemaDiagram = new SchemaDiagram("schema_diagram", testTables, testRelationships);
}