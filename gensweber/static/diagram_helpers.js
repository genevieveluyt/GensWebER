
schemaDiagram = null;

function initDiagram(divId, diagramData, editableHeader) {
	schemaDiagram = new SchemaDiagram(divId, diagramData, editableHeader);
}

function saveDiagram(url) {
	var dataString = schemaDiagram.getData();
	$.ajax({
		url: url,
		type: 'POST',
		contentType: 'application/json',
		data: dataString,
		success: function() {
			// This would be nice as a notification
			console.log("Diagram layout saved.");
		}
	});
}

function drillIn(baseUrl) {
	var entity_id = schemaDiagram.getSelectedNodeKey();
	if (entity_id === null) { // 0 is a valid value so don't use !entity_id
		// This would be nice as a notification
		console.log("Select an abstract entity or relationship to expand it.")
	} else {
		window.location.href = baseUrl + "/" + entity_id;
	}
}

function expandSelection() {
	schemaDiagram.showNeighboursOfSelectedNode();
}

function exportFullDiagram(fileName) {
	schemaDiagram.exportFullDiagram(fileName);
}

function exportVisibleDiagram(fileName) {
	schemaDiagram.exportDiagram(fileName);
}

function bindLayoutDropdown(dropdownElement) {
	dropdownElement.onchange = function() {
		var layout = dropdownElement.options[dropdownElement.selectedIndex].value
		console.log("Changed layout to " + layout);
		schemaDiagram.setLayout(layout);
	}
}

function setNodeVisibility(nodeKey, visible) {
	schemaDiagram.setNodeVisibility(nodeKey, visible);
}

function setRowVisibility(nodeKey, rowName, visible) {
	schemaDiagram.setRowVisibility(nodeKey, rowName, visible);
}
