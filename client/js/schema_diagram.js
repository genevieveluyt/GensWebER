class SchemaDiagram {
	/**
	 * @param {string} divId - The id of the div element where the diagram will be placed into
	 * @param {array} tables - Array of table objects representing the schema of that table
	 * @param {array} relationships - Array of link objects representing how tables are related by foreign keys
	 */
	constructor(divId, tables, relationships) {
		this.initDiagram(divId, tables, relationships);
	}

	initDiagram(divId, tables, relationships) {
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
				case "attribute":
				default:
					var row = 2;
					var padding = new go.Margin(0, 3, 3, 3);
					var textBinding = "attributes";
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
					textBlock
				);
			} else {
				textBlock.margin = new go.Margin(0, 0, 0, 14);

				var itemTemplate = $(
					go.Panel,
					"Horizontal",
					textBlock
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

		tables = SchemaDiagram.formatTables(tables);

		var myDiagram = $(
			go.Diagram,
			divId,
			{
				initialContentAlignment: go.Spot.Center,
				allowDelete: false,
				allowCopy: false,
				layout: $(go.ForceDirectedLayout),
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
				// define the node's outer shape, which will surround the Table
				$(
					go.Shape,
					"Rectangle",
					panelFormatting
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
							alignment: go.Spot.Center,
							margin: new go.Margin(0, 14, 0, 2),  // leave room for Button
							font: panelHeaderFont
						},
						new go.Binding("text", "name")	// table name
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
						generatePanel('attributes')
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
					}
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

		myDiagram.model = new go.GraphLinksModel(tables, relationships);
		this.diagram = myDiagram;
	}

	// Transform the schema into the structure required for the diagram
	static formatTables(tables) {
		_.each(tables, function(table) {
			// Each node must have a key
			table.key = table.name;

			// Convert each attribute (string) into an object with a 'name' property
			_.each(table, function(value, key) {
				if (_.isArray(value)) {
					table[key] = _.map(value, function(attribute) {
						return { name: attribute };
					});
				};
			});
		})

		return tables;
	}
	
}