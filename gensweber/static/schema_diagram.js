class SchemaDiagram {
	/**
	 * Create a Go.js diagram for a database schema.
	 *
	 * @param {string} divId - The id of the div element where the diagram will be placed into
	 * @param {string or json} data - Either an object with 'nodes' and 'links' or a stringified JSON produced by SchemaDiagram.getData()
	 * @param {boolean} editableHeader - Whether or not the user can edit the headers of nodes in the diagram
	 * @param {string} layout - The automatic layout of the tables in the diagram. One of "circular", "grid", "digraph" or "directed"
	 */
	constructor(divId, data, editableHeader=false, layout="directed") {
		if (typeof data == 'string') {
			var fromSavedData = true;
			console.log('Loading diagram from saved data');
		}

		this.diagram = this.initDiagram(divId, editableHeader);

		if (fromSavedData) {
			this.diagram.model = go.Model.fromJson(data);
		} else {
			this.diagram.model = new go.GraphLinksModel(data.nodes, data.links);
			this.setLayout(layout);
		}
	}

	/**
	 * Check if a node is visible.
	 *
	 * @return {boolean} - true if the node is visible, else false
	 */
	isNodeVisible(nodeKey) {
		var model = this.diagram.model;
		return model.findNodeDataForKey(nodeKey).visible;
	}

	/**
	 * Check if a row in a node is visible.
	 *
	 * @return {boolean} - true if the row is visible, else false
	 */
	isNodeRowVisible(nodeKey, rowName) {
		var model = this.diagram.model;
		var nodeData = model.findNodeDataForKey(nodeKey);
		var rowData = _.findWhere(_.union(nodeData.primary_keys, nodeData.foreign_keys, nodeData.attributes, nodeData.tables), {name: rowName});
		return rowData.visible;
	}

	/**
	 * Show or hide a node.
	 *
	 * @param {string} nodeKey - The key of the node to show or hide
	 * @param {boolean} visibility - True shows the node, false hides it and its associated links
	 */
	setNodeVisibility(nodeKey, visibility) {
		var model = this.diagram.model;
		model.setDataProperty(model.findNodeDataForKey(nodeKey), "visible", visibility);
	}

	/**
	 * Show or hide a row in a node.
	 *
	 * @param {string} nodeKey - The key of the node containing the row to show or hide
	 * @param {string} rowName - The name of the row to show or hide
	 * @param {boolean} visibility - True shows the row, false hides it
	 */
	setRowVisibility(nodeKey, rowName, visibility) {
		var model = this.diagram.model;
		var nodeData = model.findNodeDataForKey(nodeKey);
		var rowData = _.findWhere(_.union(nodeData.primary_keys, nodeData.foreign_keys, nodeData.attributes, nodeData.tables), {name: rowName});
		model.setDataProperty(rowData, "visible", visibility)
	}

	/**
	 * Get the key of the currently selected node in the diagram.
	 */
	getSelectedNodeKey() {
		var diagram = this.diagram;

		var selectedNode = diagram.selection.iterator;
		while(selectedNode.next()) {
			if (selectedNode.value) {
				return selectedNode.value.data.key;
			}
		}

		// no node selected
		return null;
		
	}

	/**
	 * Show all nodes that are linked to currently selected node.
	 */
	showNeighboursOfSelectedNode() {
		var diagram = this.diagram;
		var model = diagram.model;

		var selectedNodes = diagram.selection.iterator;
		while(selectedNodes.next()) {
			var connectedNodes = selectedNodes.value.findNodesConnected();
			while(connectedNodes.next()) {
				var connectedNode = connectedNodes.value.data;
				if (!connectedNode.visible) {
					model.setDataProperty(connectedNode, "visible", true);
				}
			}
		}
	}

	/**
	 * Set the automatic layout of nodes in the diagram
	 *
	 * @param {string} layout - One of "circular", "grid", "digraph" or "directed"
	 */
	setLayout(layout) {
		this.diagram.layout = (function (layout) {
			switch(layout) {
				case "circular":
					return new go.CircularLayout();
				case "grid":
					return new go.GridLayout();
				case "digraph":
					return new go.LayeredDigraphLayout();
				case "directed":
					return new go.ForceDirectedLayout();
				default:
					console.log("setLayout(): Unknown layout '" + layout + "'");
			}
		})(layout);
	}


	/**
	 * Export the full diagram to a file.
	 *
	 * @param {string} filename - The file name that will be used for the file.
	 */
	exportFullDiagram(filename="diagram.png") {
		this.exportDiagram(filename, { scale: 1 });
	}

	/**
	 * Export the diagram to a file. If no options are passed in, only the part of the diagram visible on the canvas will be exported.
	 *
	 * @param {string} filename - The file name that will be used for the file.
	 * @param {options} - See Go.js documentation for options that can be passed to Diagram.makeImageData()
	 */
	exportDiagram(filename="diagram.png", options={}) {
		// make a temporary element to force download
		var a = document.createElement('a');
		a.href = this.diagram.makeImageData(options);
		a.download = filename;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
	}

	/**
	 * Get the diagram data that can be used to load the diagram in the same state.
	 *
	 * @return {string} - stringified JSON that can be passed into the constructor of this class to reload the diagram in the same state.
	 */
	getData() {
		return this.diagram.model.toJson();
	}

	/**
	 * Build the actual diagram
	 */
	initDiagram(divId, editableHeader=false) {
		var $ = go.GraphObject.make;

		// Diagram Formatting
		var panelFormatting = {
				fill: $(go.Brush, "Linear", { 1: "#E6E6FA", 0: "#FFFAF0" }),
				stroke: "#756875",
				strokeWidth: 3 
			}
		var panelShadowColour = "#C5C1AA";
		var panelHeaderFont = "bold 16px sans-serif";
		var panelBodyFont = "bold 14px sans-serif";
		var panelBodyFontColour = "#333333";
		var linkColour = "#303B45";
		var foreignKeyCandidateLinkColour = "#ff4081";		// pink
		var linkTextFont = "bold 14px sans-serif";
		var linkTextColour = "#1967B3"


		// Helper function

		/**
		 * Create templates for the different kind of attributes: Primary Keys, Foreign Keys, Plain Attributes
		 *
		 * @param {string} type - one of "primary", "foreign", or "attributes" corresponding to the type of panel that will be made
		 * @return {go.Panel object}
		 */
		function generatePanel(type) {
			switch(type) {
				case "primary":
					var row = 0;
					var padding = new go.Margin(3, 3, 0, 3);
					var textBinding = "primary_keys";
					var figure = 'FivePointedStar';
					var figureColour = 'yellow';
					break;
				case "foreign":
					var row = 1;
					var padding = new go.Margin(0, 3, 0, 3);
					var textBinding = "foreign_keys";
					var figure = 'BpmnEventEscalation';
					var figureColour = 'blue';
					break;
				default:
					var row = 2;
					var padding = new go.Margin(0, 3, 3, 3);
					var textBinding = type;
					var figure = null;
			}

			var textBlock = $(
				go.TextBlock,
				{
					stroke: panelBodyFontColour,
					font: panelBodyFont
				},
				new go.Binding("text", "name")
			);

			if (figure) {
				var shape = $(
					go.Shape,
					{
						desiredSize: new go.Size(10, 10),
						stroke: 'grey',
						margin: new go.Margin(0, 4, 0, 0),
						figure: figure,
						fill: figureColour
					}
				);

				var itemTemplate = $(
					go.Panel,
					"Horizontal",
					shape,
					textBlock,
					new go.Binding("visible", "visible")
				);
			} else {
				textBlock.margin = new go.Margin(0, 0, 0, 14);

				var itemTemplate = $(
					go.Panel,
					"Horizontal",
					textBlock,
					new go.Binding("visible", "visible")
				);
			}

			var panel = $(
				go.Panel,
				"Vertical",
				{
					row: row,
					padding: padding,
					alignment: go.Spot.TopLeft,
					defaultAlignment: go.Spot.Left,
					stretch: go.GraphObject.Horizontal,
					itemTemplate: itemTemplate
				},
				new go.Binding("itemArray", textBinding)
			)

			return panel
		}


		// CODE

		var myDiagram = $(
			go.Diagram,
			divId,
			{
				initialContentAlignment: go.Spot.Center,
				allowDelete: false,
				allowCopy: false,
				"undoManager.isEnabled": true
			}
		);

		// define the Node template, representing an entity
		myDiagram.nodeTemplate =
			$(
				go.Node,
				"Auto",  // the whole node panel
				{
					selectionAdorned: true,
					resizable: true,
					layoutConditions: go.Part.LayoutStandard & ~go.Part.LayoutNodeSized,
					fromSpot: go.Spot.AllSides,
					toSpot: go.Spot.AllSides,
					isShadowed: true,
					shadowColor: panelShadowColour
				},
				new go.Binding("location", "location").makeTwoWay(),
				new go.Binding("visible", "visible"),
				// define the node's outer shape, which will surround the Table
				$(
					go.Shape,
					"RoundedRectangle",
					panelFormatting,
					new go.Binding("figure", "shape")
				),
				$(
					go.Panel,
					"Table",
					{
						margin: 8,
						stretch: go.GraphObject.Fill
					},
					$(
						go.RowColumnDefinition,
						{
							row: 0,
							sizing: go.RowColumnDefinition.None
						}
					),
					// the table header
					$(
						go.TextBlock,
						{
							row: 0,
							alignment: go.Spot.Left,
							margin: new go.Margin(0, 14, 0, 2),  // leave room for Button
							font: panelHeaderFont,
							editable: editableHeader
						},
						new go.Binding("text", "name").makeTwoWay()
					),
					// the collapse/expand button
					$(
						"PanelExpanderButton",
						"LIST",  // the name of the element whose visibility this button toggles
						{
							row: 0,
							alignment: go.Spot.TopRight
						}
					),
					// the table body
					$(
						go.Panel,
						"Table",
						{
							name: "LIST",
							row: 1
						},
						generatePanel('primary'),
						generatePanel('foreign'),
						generatePanel('attributes'),
						generatePanel('tables'),
						new go.Binding('visible', 'expanded').makeTwoWay()
					)
				)  // end Table Panel
			);  // end Node

		// define the Link template, representing a relationship
		myDiagram.linkTemplate =
			$(
				go.Link,  // the whole link panel
				{
					selectionAdorned: true,
					layerName: "Foreground",
					reshapable: true,
					routing: go.Link.AvoidsNodes,
					corner: 5,
					curve: go.Link.JumpOver
				},
				$(
					go.Shape,  // the link shape
					{
						stroke: linkColour,
						strokeWidth: 2.5
					},
					new go.Binding("stroke", "isForeignKeyCandidate", function(isForeignKeyCandidate) { 
						if (isForeignKeyCandidate) {
							return foreignKeyCandidateLinkColour;
						} else {
							return linkColour;
						}
					})
				),
				$(
					go.TextBlock,  // the "from" label
					{
						textAlign: "center",
						font: linkTextFont,
						stroke: linkTextColour,
						segmentIndex: 0,
						segmentOffset: new go.Point(NaN, NaN),
						segmentOrientation: go.Link.OrientUpright
					},
					new go.Binding("text", "text")
				),
				$(
					go.TextBlock,  // the "to" label
					{
						textAlign: "center",
						font: linkTextFont,
						stroke: linkTextColour,
						segmentIndex: -1,
						segmentOffset: new go.Point(NaN, NaN),
						segmentOrientation: go.Link.OrientUpright
					},
					new go.Binding("text", "toText")
				)
			);

		return myDiagram;
	}
}
