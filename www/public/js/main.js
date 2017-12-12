var numReps = 120,
cellSize = 5,
textLength = 75,
text_span = cellSize/4,
clusterRect = cellSize*2,
squareTipSize = 20,
toolTipSize = 340,
margin = { top: 1, right: 1, bottom: 1, left: 1 },
width = textLength + (numReps+1)*cellSize + squareTipSize,
height = width + squareTipSize,
clusterColors = ['#A0A4B8','#A3C4BC','#8DD17F','#7293A0','#AEDCC0','#D7B29D','#CB8589','#E8D2AE','#B5C2B7','#8C93A8'],
reps = [],
repsColors = [],
repsInfo = [],
zoomed = false,
growth = 4;

d3.select(".description-container").style("height",height + "px");

var svg = d3.select("#chart").append("svg")
.attr("width", width + margin.left + margin.right)
.attr("height", height + margin.top + margin.bottom)
.append("g")
.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.json("./public/data/graph.votaciones.json", function(error, graph) {
  if (error) throw error;

  $('#prev-loader').hide();

  var colorGroup = d3.scaleOrdinal(clusterColors);

  var colorScale = function(row,column,val) {
	  if (repsColors[row] === repsColors[column]) return d3.scaleLinear().domain([0, 1]).range(["#fff",repsColors[row]])(val);
	  return d3.scaleLinear().domain([0, 1]).range(["#fff","#ddd"])(val); 
	  //return d3.scalePow().domain([0, 1]).range(["#fff",d3.interpolateLab(repsColors[row], repsColors[column])(0.5)])(val);
  }

  var showToolTip = function(d, element) {  				  
	  var index_source = reps.indexOf(d.source),
	  source = repsInfo[index_source],
	  index_target = reps.indexOf(d.target),
	  target = repsInfo[index_target],
	  color_source = repsColors[index_source],
	  color_target = repsColors[index_target],
	  square_x = element.getAttribute("x")*1,
	  square_y = element.getAttribute("y")*1,
	  //tool_pos_x = ((d3.event.pageX > width - toolTipSize) ? (d3.event.pageX - toolTipSize - squareTipSize) : (d3.event.pageX + squareTipSize)),
	  //tool_pos_y = ((d3.event.pageY > height - toolTipSize) ? (d3.event.pageY - toolTipSize/2) : (d3.event.pageY - squareTipSize)),
	  
	  tool_pos_x = ((square_x > width - toolTipSize) ? (square_x - toolTipSize - squareTipSize*0.5) : (square_x + squareTipSize*1.5)),
	  tool_pos_y = ((square_y > height - toolTipSize) ? (square_y - toolTipSize/2) : (square_y + squareTipSize)),
	  
	  circle_pos_x = square_x + (zoomed ? growth : 1)*cellSize/2 + 0.5*squareTipSize/2;
	  circle_pos_y = square_y - 0.5*squareTipSize/2 + (zoomed ? growth : 1)*cellSize/2;
	  
	  match_color = d3.scaleLinear().domain([0, 1]).range(["red","green"])(d.value);
    
	  var selection = d3.select("#tooltip")
	  .style("left", tool_pos_x + "px")
	  .style("top", tool_pos_y + "px");
  
	  selection.select("#rep_1").style("border-color",color_source);
	  selection.select("#rep_1 p").html(source.nombre);  
	  selection.select("#rep_1 span.par").html(source.partido);  
	  selection.select("#rep_1 span.bloc").style("color",color_source).html("Bloque " + (source.group + 1));  
  
	  selection.select("#rep_2").style("border-color",color_target);
	  selection.select("#rep_2 p").html(target.nombre);  
	  selection.select("#rep_2 span.par").html(target.partido); 
	  selection.select("#rep_2 span.bloc").style("color",color_target).html("Bloque " + (target.group + 1));  
  
	  selection.select(".speed").style("color",match_color).style("border-color",match_color); 
	  selection.select("#match").html(Math.round(100*d.value) + "%"); 
  
	  selection.classed("hidden", false);
  
	  d3.select("#squareTip")
	  .style("left", circle_pos_x + "px")
	  .style("top", circle_pos_y + "px")
	  .style("background-color", colorScale(index_target, index_source, d.value))
	  .classed("hidden", false);				  
  }

  var getGroupClass = function(d) {
	  var index_source = reps.indexOf(d.source),
	  source = repsInfo[index_source],
	  index_target = reps.indexOf(d.target),
	  target = repsInfo[index_target];
	
	  if (index_source < index_target) return "group_" + (source.group + 1) + "_" + (target.group + 1);
	  return "group_" + (target.group + 1) + "_" + (source.group + 1);
  }

  var squareClicked = function(d) {
	  // Get the group
	  var group_target = repsInfo[reps.indexOf(d.target)].group;
	  var group_source = repsInfo[reps.indexOf(d.source)].group;
	  var group_str = getGroupClass(d);
	  zoomed = true;

	  // Delete all squares except group ones
	  d3.selectAll("rect.heatSquare:not(." + group_str + ")")
	  .transition()
	  .attr("width", function(d2) { return 0; })
	  .attr("height", function(d2) { return 0; });
	  d3.selectAll("text.mono:not(." + group_str + ")")
	  .transition()
	  .attr("fill-opacity", function(d2) { return 0; });
	  d3.selectAll("rect.clusterRect:not(." + group_str + ")")
	  .transition()
	  .attr("width", function(d2) { return 0; })
	  .attr("height", function(d2) { return 0; });

	  // Change sizes and positions
	  var counter = -1, counter_source = -1;
	  for (var i = 0; i < reps.length; i++) {
		  if (repsInfo[i].group === group_target && counter < 0) {
			  counter = i;
		  }
		  if (repsInfo[i].group === group_source && counter_source < 0) {
			  counter_source = i;
		  }
	  }

	  // SQUARES
	  d3.selectAll("rect.heatSquare.down." + group_str + "")
	  .transition()
	  .attr("width", function(d2) { return cellSize*growth; })
	  .attr("height", function(d2) { return cellSize*growth; })
	  .attr("x", function(d2) { return textLength + text_span + clusterRect + text_span + (reps.indexOf(d2.source)-counter_source)*cellSize*growth; })
	  .attr("y", function(d2) { return textLength + text_span + clusterRect + text_span + (reps.indexOf(d2.target)-counter)*cellSize*growth + cellSize; });

	  if (group_target === group_source) {
		  d3.selectAll("rect.heatSquare.diago." + group_str + "")
		  .transition()
		  .attr("width", function(d2) { return cellSize*growth; })
		  .attr("height", function(d2) { return cellSize*growth; })
		  .attr("x", function(d2, i2) { return textLength + text_span + clusterRect + text_span + i2*cellSize*growth; })
		  .attr("y", function(d2, i2) { return textLength + text_span + clusterRect + text_span + i2*cellSize*growth + cellSize; });

		  d3.selectAll("rect.heatSquare.up." + group_str + "")
		  .transition()
		  .attr("width", function(d2) { return cellSize*growth; })
		  .attr("height", function(d2) { return cellSize*growth; })
		  .attr("x", function(d2) { return textLength + text_span + clusterRect + text_span + (reps.indexOf(d2.target)-counter_source)*cellSize*growth; })
		  .attr("y", function(d2) { return textLength + text_span + clusterRect + text_span + (reps.indexOf(d2.source)-counter)*cellSize*growth + cellSize; });
	  } 
	  else if (group_target > group_source) {
		  d3.selectAll("rect.heatSquare.diago")
		  .transition()
		  .attr("width", function(d2) { return 0; })
		  .attr("height", function(d2) { return 0; });

		  d3.selectAll("rect.heatSquare.up")
		  .transition()
		  .attr("width", function(d2) { return 0; })
		  .attr("height", function(d2) { return 0; });
	  }

	  // CLUSTER RECTS
	  if (group_target === group_source) {
		  d3.selectAll("rect.clusterRect.row." + group_str + "")
		  .transition()
		  .attr("height", function(d2) { return cellSize*growth; })
		  .attr("y", function(d2, i2) { return text_span + clusterRect + cellSize + textLength + text_span  + (i2)*cellSize*growth; });
		  d3.selectAll("rect.clusterRect.column." + group_str + "")
		  .transition()
		  .attr("width", function(d2) { return cellSize*growth; })
		  .attr("x", function(d2, i2) { return textLength + text_span + clusterRect + text_span + (i2)*cellSize*growth; });
	  }	
	  else if (group_target > group_source) {
		  d3.selectAll("rect.clusterRect.row.group_" + (group_target+1) + "_" + (group_target+1))
		  .transition()
		  .attr("height", function(d2) { return cellSize*growth; })
		  .attr("y", function(d2, i2) { return text_span + clusterRect + cellSize + textLength + text_span  + (i2)*cellSize*growth; });
		  d3.selectAll("rect.clusterRect.column.group_" + (group_source+1) + "_" + (group_source+1))
		  .transition()
		  .attr("width", function(d2) { return cellSize*growth; })
		  .attr("x", function(d2, i2) { return textLength + text_span + clusterRect + text_span + (i2)*cellSize*growth; });
	  }

	  // TEXT LABELS
	  if (group_target === group_source) {
		  d3.selectAll("text.row." + group_str + "")
		  .transition()
		  .attr("y", function (d2, i2) { return text_span*2 + clusterRect + textLength + text_span + cellSize*1.5  + (i2) * cellSize*growth; });
		  d3.selectAll("text.column." + group_str + "")
		  .transition()
		  .attr("transform", function (d2, i2) { return "translate(" + i2*cellSize*growth + "," + (textLength + cellSize*2) + ") rotate(-90)"; });
	  }
	  else if (group_target > group_source) {
		  d3.selectAll("text.row.group_" + (group_target+1) + "_" + (group_target+1))
		  .transition()
		  .attr("fill-opacity", function(d) { return 1; })
		  .attr("y", function (d2, i2) { return text_span*2 + clusterRect + textLength + text_span + cellSize*1.5  + (i2) * cellSize*growth; });
	
		  d3.selectAll("text.column.group_" + (group_source+1) + "_" + (group_source+1))
		  .transition()
		  .attr("fill-opacity", function(d) { return 1; })
		  .attr("transform", function (d2, i2) { return "translate(" + i2*cellSize*growth + "," + (textLength + cellSize*2) + ") rotate(-90)"; });
	  }
  }

  var backToNormal = function() {
	  zoomed = false;
  
	  d3.selectAll(".rowLabel")
	  .attr("x", textLength)
	  .attr("fill-opacity", function(d) { return 1; })
	  .attr("y", function (d, i) { return text_span*2 + clusterRect + textLength + text_span + cellSize*1.5  + (i) * cellSize; });

	  d3.selectAll(".columnLabel")
	  .attr("x", cellSize)
	  .attr("y", text_span+ clusterRect + textLength + cellSize)
	  .attr("fill-opacity", function(d) { return 1; })
	  .attr("transform", function (d, i) { return "translate(" + i*cellSize + "," + (textLength + cellSize*2) + ") rotate(-90)"; });

	  d3.selectAll(".heatSquare.down")
	  .attr("x", function(d) { return text_span + clusterRect + textLength + text_span + reps.indexOf(d.source) * cellSize; })
	  .attr("y", function(d) { return text_span + clusterRect + textLength + cellSize + text_span + reps.indexOf(d.target) * cellSize; })
	  .attr("width", cellSize)
	  .attr("height", cellSize);

	  d3.selectAll(".heatSquare.up")
	  .attr("x", function(d) { return text_span + clusterRect + textLength + text_span + reps.indexOf(d.target) * cellSize; })
	  .attr("y", function(d) { return text_span + clusterRect + textLength + cellSize + text_span + reps.indexOf(d.source) * cellSize; })
	  .attr("width", cellSize)
	  .attr("height", cellSize);

	  d3.selectAll(".heatSquare.diago")
	  .attr("x", function(d) { return text_span + clusterRect + textLength + text_span + reps.indexOf(d.id) * cellSize; })
	  .attr("y", function(d) { return text_span + clusterRect + textLength + cellSize + text_span + reps.indexOf(d.id) * cellSize; })
	  .attr("width", cellSize)
	  .attr("height", cellSize);

	  d3.selectAll(".clusterRect.column")
	  .attr("x", function(d) { return text_span + clusterRect + textLength + text_span + reps.indexOf(d.id) * cellSize; })
	  .attr("y", function(d) { return textLength + cellSize + text_span })
	  .attr("width", cellSize)
	  .attr("height", clusterRect);

	  d3.selectAll(".clusterRect.row")
	  .attr("x", function(d) { return textLength + text_span; })
	  .attr("y", function(d) { return text_span + clusterRect + cellSize + textLength + text_span  + reps.indexOf(d.id) * cellSize; })
	  .attr("width", clusterRect)
	  .attr("height", cellSize);
  }

  for (var i = 0; i < graph.nodes.length; i++ ) {
	  reps.push(graph.nodes[i].id);
	  repsColors.push(colorGroup(graph.nodes[i].group));
	  repsInfo.push(graph.nodes[i])
  }

  var rowLabels = svg.append("g")
  .selectAll(".rowLabel")
  .data(graph.nodes)
  .enter()
  .append("text")
  .text(function (d) { return d.nombre; })
  .attr("x", textLength)
  .attr("y", function (d, i) { return text_span*2 + clusterRect + textLength + text_span + cellSize*1.5  + (i) * cellSize; })
  .style("text-anchor", "end")
  .attr("class", function (d,i) { return "rowLabel mono row r" + i + " rowId_" + d.id +  " group_" + (d.group+1) + "_" + (d.group+1); } );

  var columnLabels = svg.append("g")
  .selectAll(".columnLabel")
  .data(graph.nodes)
  .enter()
  .append("text")
  .text(function (d) { return d.nombre; })
  .attr("x", cellSize)
  .attr("y", text_span+ clusterRect + textLength + cellSize)
  .style("text-anchor", "left")
  .attr("transform", function (d, i) { return "translate(" + i*cellSize + "," + (textLength + cellSize*2) + ") rotate(-90)"; })
  .attr("class", function (d,i) { return "columnLabel mono column c" + i + " columnId_" + d.id +  " group_" + (d.group+1) + "_" + (d.group+1);} );

  var heatSquaresDown = svg.append("g")
  .selectAll(".heatSquare")
  .data(graph.links)
  .enter()
  .append("rect")
  .attr("x", function(d) { return text_span + clusterRect + textLength + text_span + reps.indexOf(d.source) * cellSize; })
  .attr("y", function(d) { return text_span + clusterRect + textLength + cellSize + text_span + reps.indexOf(d.target) * cellSize; })
  .attr("width", cellSize)
  .attr("height", cellSize)
  .style("fill", function(d) { return colorScale(reps.indexOf(d.target), reps.indexOf(d.source), d.value); })
  .attr("text", function(d) { return "From " + d.source + " to  " + d.target})
  .attr("class", function (d,i) {  return "heatSquare down " + getGroupClass(d); })
  .on("mouseover", function(d){
	  d3.select(".rowId_"+d.target).classed("selected", true);
	  d3.select(".columnId_"+d.source).classed("selected", true);					
	  showToolTip(d, this);
  })
  .on("mouseout", function(d){
	  d3.select(".rowId_" + d.target).classed("selected", false);
	  d3.select(".columnId_"+d.source).classed("selected", false);
	  d3.select("#squareTip").classed("hidden", true);
	  d3.select("#tooltip").classed("hidden", true);
  })
  .on("click", function(d){
	  // if (repsInfo[reps.indexOf(d.target)].group !== repsInfo[reps.indexOf(d.source)].group) return;
	  if (zoomed) { backToNormal(); return; }
	  squareClicked(d);
  });

  var heatSquaresUp = svg.append("g")
  .selectAll(".heatSquare")
  .data(graph.links)
  .enter()
  .append("rect")
  .attr("x", function(d) { return text_span + clusterRect + textLength + text_span + reps.indexOf(d.target) * cellSize; })
  .attr("y", function(d) { return text_span + clusterRect + textLength + cellSize + text_span + reps.indexOf(d.source) * cellSize; })
  .attr("width", cellSize)
  .attr("height", cellSize)
  .style("fill", function(d) { return colorScale(reps.indexOf(d.target), reps.indexOf(d.source), d.value); })
  .attr("text", function(d) { return "From " + d.target + " to  " + d.source})
  .attr("class", function (d,i) {  return "heatSquare up " + getGroupClass(d); })
  .on("mouseover", function(d){
	  d3.select(".rowId_"+d.source).classed("selected", true);
	  d3.select(".columnId_"+d.target).classed("selected", true);
	  showToolTip(d, this);
  })
  .on("mouseout", function(d){
	  d3.select(".rowId_"+d.source).classed("selected", false);
	  d3.select(".columnId_"+d.target).classed("selected", false);
	  d3.select("#squareTip").classed("hidden", true);
	  d3.select("#tooltip").classed("hidden", true);
  })
  .on("click", function(d){
	  // if (repsInfo[reps.indexOf(d.target)].group !== repsInfo[reps.indexOf(d.source)].group) return;
	  if (zoomed) { backToNormal(); return; }
	  squareClicked(d);
  });

  var heatSquaresDiagonal = svg.append("g")
  .selectAll(".heatSquare")
  .data(graph.nodes)
  .enter()
  .append("rect")
  .attr("x", function(d) { return text_span + clusterRect + textLength + text_span + reps.indexOf(d.id) * cellSize; })
  .attr("y", function(d) { return text_span + clusterRect + textLength + cellSize + text_span + reps.indexOf(d.id) * cellSize; })
  .attr("width", cellSize)
  .attr("height", cellSize)
  .attr("class", function (d,i) {  return "heatSquare diago " + "group_" + (d.group+1) + "_" + (d.group+1); })
  .style("fill", function(d) { return colorScale(reps.indexOf(d.id), reps.indexOf(d.id), 1); });

  var clusterRectColumns = svg.append("g")
  .selectAll(".clusterRect")
  .data(graph.nodes)
  .enter()
  .append("rect")
  .attr("x", function(d) { return text_span + clusterRect + textLength + text_span + reps.indexOf(d.id) * cellSize; })
  .attr("y", function(d) { return textLength + cellSize + text_span })
  .attr("width", cellSize)
  .attr("height", clusterRect)
  .style("fill", function(d) { return colorGroup(d.group); })
  .style("stroke-width", 0)
  .attr("class", function (d,i) {  return "clusterRect column " + "group_" + (d.group+1) + "_" + (d.group+1); });

  var clusterRectRows = svg.append("g")
  .selectAll(".clusterRect")
  .data(graph.nodes)
  .enter()
  .append("rect")
  .attr("x", function(d) { return textLength + text_span; })
  .attr("y", function(d) { return text_span + clusterRect + cellSize + textLength + text_span  + reps.indexOf(d.id) * cellSize; })
  .attr("width", clusterRect)
  .attr("height", cellSize)
  .style("fill", function(d) { return colorGroup(d.group); })
  .style("stroke-width", 0)
  .attr("class", function (d,i) {  return "clusterRect row " + "group_" + (d.group+1) + "_" + (d.group+1); });

});


// Cluster Loading
var loadedClusters = false;
function loadClusters() {
  if (loadedClusters) return;
  loadedClusters = true;
  $('#cluster-graph-container').html('<iframe style="width:100%;" src="http://bloques.votoenbloque.cl/"></iframe>');
}

// Mobile alert
if (window.innerWidth < 500) {
	$('#mobileModal').modal('show');
}