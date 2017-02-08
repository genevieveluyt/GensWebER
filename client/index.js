window.onload = function() {

    //var connectionInfo = {
        //user:'root',
        //name:'oscar15_bc',
        //password:'@scar2015', 
        //host:'127.0.0.1'
    //}

    var connectionInfo = {
        user:'root',
        name:'northwind',
        password:'1234', 
        host:'127.0.0.1'
    }

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            //console.log(xmlHttp.responseText);
            var rowanSchema = JSON.parse(xmlHttp.responseText);
            console.log(rowanSchema.tables);
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
}

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
