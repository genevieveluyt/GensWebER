
schemaDiagram = null;

/*
 * Initialize the Go.js diagram.
 *
 * @param {string} divId - The id of the div element where the diagram will be placed into
 * @param {string or json} data - Either an object with 'nodes' and 'links' or a stringified JSON produced by saveDiagram()
 * @param {boolean} editableHeader - Whether or not the user can edit the headers of nodes in the diagram
 */
function initDiagram(divId, diagramData, editableHeader) {
	schemaDiagram = new SchemaDiagram(divId, diagramData, editableHeader);
}

/*
 * Save the diagram state to the logged in user's account.
 * Saves whether nodes are expanded or not, whether nodes are visible or not, whether rows in nodes are visible or not, and the location of nodes in the diagram.
 *
 * @param {string} url - url to post the diagram data to
 */
function saveDiagram(url) {
	var dataString = schemaDiagram.getData();
	$.ajax({
		url: url,
		type: 'POST',
		contentType: 'application/json',
		data: dataString,
		success: function() {
			$('.notification').text('Diagram layout saved').removeClass('hidden');
		},
		error: function(response) {
			$('.notification').text(response.responseText).removeClass('hidden');
		}
	});
}

/**
 * View the tables and relationships contained in an abstract entity or abstract relationship.
 *
 * baseUrl - the url to which to append the entity_id. Most likely the url of the current page.
 */
function drillIn(baseUrl) {
	var entity_id = schemaDiagram.getSelectedNodeKey();
	if (entity_id === null) { // 0 is a valid value so don't use !entity_id
		// This would be nice as a notification
		console.log("Select an abstract entity or relationship to expand it.")
	} else {
		window.location.href = baseUrl + "/" + entity_id;
	}
}

/**
 * Show neighbours of the selected node.
 */
function expandSelection(callback=None) {
	schemaDiagram.showNeighboursOfSelectedNode(callback);
}

/**
 * Export the full Go.js diagram.
 *
 * @param {string} fileName - name to use for the exported file.
 */
function exportFullDiagram(fileName) {
	schemaDiagram.exportFullDiagram(fileName);
}

/**
 * Export the visible Go.js diagram.
 *
 * @param {string} fileName - name to use for the exported file.
 */
function exportVisibleDiagram(fileName) {
	schemaDiagram.exportDiagram(fileName);
}

/**
 * Sets an onchange listener on the layout dropdown to change the diagram layout when a new layout is selected.
 *
 * dropdownElement - select DOM element with option values "directed", circular", "grid", and "digraph".
 */
function bindLayoutDropdown(dropdownElement) {
	dropdownElement.onchange = function() {
		var layout = dropdownElement.options[dropdownElement.selectedIndex].value
		console.log("Changed layout to " + layout);
		schemaDiagram.setLayout(layout);
	}
}

/**
 * Show or hide a node.
 *
 * @param {string} nodeKey - the key of the node to show or hide
 * @param {boolean} visible - true shows the node, false hides it and its associated links
 */
function setNodeVisibility(nodeKey, visible) {
	schemaDiagram.setNodeVisibility(nodeKey, visible);
}

/**
 * Show or hide a row in a node.
 *
 * @param {string} nodeKey - the key of the node containing the row to show or hide
 * @param {string} rowName - the name of the row to show or hide
 * @param {boolean} visible - true shows the row, false hides it
 */
function setRowVisibility(nodeKey, rowName, visible) {
	schemaDiagram.setRowVisibility(nodeKey, rowName, visible);
}

/**
 * Expand all nodes in the diagram (show all rows in all nodes).
 */
function expandAllNodes() {
	schemaDiagram.expandAllNodes();
}

/**
 *	Collapse all nodes in the diagram (hide all rows in all nodes)
 */
function collapseAllNodes() {
	schemaDiagram.collapseAllNodes();
}
