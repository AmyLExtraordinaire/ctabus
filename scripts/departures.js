(function() {
  
  var margin = {top: 30, right: 50, bottom: 50, left: 30},
      outerWidth = 900,
      width = outerWidth - margin.left - margin.right,
      gridSize = width / 24,
      outerHeight = (gridSize * 7) + margin.top + margin.bottom,
      height = outerHeight - margin.top - margin.bottom;

  var svg = d3.select("#svg-departures").append("svg")
      .attr("viewBox", "0 0 " + outerWidth + " " + outerHeight)
      .attr("preserveAspectRatio", "xMidYMid meet")
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var x = d3.scaleLinear()
      .range([0, width])
      .domain([0, 23.99]);

  var y = d3.scaleLinear()
      .range([0, gridSize * 7])
      .domain([0, 6.99]);

  var color = d3.scaleSequential(d3.interpolateGreys);

  var legendY = d3.scaleLinear()
    .domain([0, height]);

  var inverseLegendY = d3.scaleLinear()
    .range([0, height]);

  var legend = svg.append("g")
    .attr("class", "legend-departure")
    .attr("transform", "translate(" + (width) + ",0)");

  var legendAxisArea = legend.append("g")
      .attr("class", "axis axis--y")
      .attr("transform", "translate(30,0)");

  var legendAxis = d3.axisRight()
    .scale(inverseLegendY)
    .ticks(4)
    .tickSize(0);

  svg.append("g")
    .attr("class", "axis axis--x")
  .selectAll(".xtick")
  .data(Array(24))
  .enter()
  .append("text")
    .attr("id", (_, i) => "hour" + i)
    .attr("dy", "-0.25em")
    .attr("x", (_, i) => i * gridSize + gridSize / 2)
    .style("text-anchor", "middle")
    .style("font", "10px sans-serif")
    .text((_, i) => {
        var now = new Date();
        now.setHours(i, 0, 0, 0);
        return d3.timeFormat("%-I%p")(now).toLowerCase();
      });

  svg.append("g")
      .attr("class", "axis axis--y")
    .selectAll(".ytick")
    .data(Array(7))
    .enter()
    .append("text")
        .attr("id", (_, i) => "day" + i)
        .attr("dx", "-0.25em")
        .attr("y", (_, i) => i * gridSize + gridSize / 2)
        .style("text-anchor", "end")
        .style("font", "10px sans-serif")
        .text((_, i) => {
          var date = new Date(2017, 4, 1);
          return d3.timeFormat("%a")(date.setDate(date.getDate() + i));
        });

  var bottomAxis = svg.append("g")
    .attr("class", "departures-bottom-axis")
    .attr("transform", "translate(0," + (height + 10) + ")");

  var bottomButtons = bottomAxis.append("g")
    .attr("transform", "translate(0,10)");

  var bottomCaptionLeft = bottomButtons.append("text")
    .attr("id", "wb-departure")
    .attr("text-anchor", "start")
    .style("font", "bold 16px sans-serif")
    .html("Westbound")
    .style("cursor", "pointer")
    .on("click", function(d) { updateWB(); });

  bottomAxis.append("g")
    .attr("transform", "translate(" + bottomCaptionLeft.node().getBBox().width + ",10)")
    .append("text")
    .attr("id", "eb-departure")
    .attr("dx", "1em")
    .attr("text-anchor", "start")
    .style("font", "bold 16px sans-serif")
    .html("Eastbound")
    .style("cursor", "pointer")
    .on("click", function(d) { updateEB(); });

  var bottomTitle = bottomAxis.append("text")
    .attr("x", width)
    .attr("y", 10)
    .attr("text-anchor", "end")
    .style("font", "bold 16px sans-serif");

  function updateEB() {
    if (!d3.select("#eb-departure").classed("active")) {
      d3.select("#wb-departure")
          .classed("active", null)
          .attr("opacity", 0.5);
      //bottomCaption.html("Eastbound &#8594");
      updateDirectionDeparture("eb");
      d3.select("#eb-departure")
          .classed("active", true)
          .attr("opacity", 1);
    }
  }

  function updateWB() {
    if (!d3.select("#wb-departure").classed("active")) {
      d3.select("#eb-departure")
          .classed("active", null)
          .attr("opacity", 0.5);
      //bottomCaption.html("&#8592 Westbound");
      updateDirectionDeparture("wb");
      d3.select("#wb-departure")
          .classed("active", true)
          .attr("opacity", 1);
    }
  }

  function updateDirectionDeparture(direction) {
    d3.csv("data/processed/departures/55_departures_" + direction + ".csv", type, function(error, departures) {
      if (error) throw error;

      color.domain([0, Math.ceil(d3.max(departures.map(d => d.departures)))]);

      var grids = svg.selectAll(".grid")
          .data(departures);

      grids.exit().remove();

      grids.enter().append("rect")
          .attr("x", d => x(d.hour))
          .attr("y", d => y(d.day))
          //.attr("rx", 5)
          //.attr("ry", 5)
          //.attr("id", d => "hour" + d.hour + " day" + d.day)
          .attr("class", "grid")
          .attr("width", gridSize)
          .attr("height", gridSize)
          .style("fill", d => color(d.departures))
          .on("mouseover", function(d) {
            d3.select(this).style("stroke", "red")
              .style("stroke-width", "2px");
            d3.select("#day" + d.day).style("fill", "red");
            d3.select("#hour" + d.hour).style("fill", "red");
          })
          .on("mouseout", function(d) {
            d3.select(this).style("stroke", "none");
            d3.select("#day" + d.day).style("fill", "black");
            d3.select("#hour" + d.hour).style("fill", "black");
          })

      d3.selectAll(".departures-grid-caption").remove();
      d3.selectAll(".grid").append("title")
          .attr("class", "departures-grid-caption")
          .text((d) => d.departures + " buses dispatched on average");

      grids.transition().duration(1000).style("fill", d => color(d.departures));

      legendY.range(color.domain());
      inverseLegendY.domain(color.domain());

      legend.selectAll(".bands-departure")
        .data(d3.range(height), d => d)
      .enter().append("rect")
        .attr("x", 10)
        .attr("y", d => d)
        .attr("width", 20)
        .attr("height", 1)
        .attr("fill", d => color(legendY(d)));

      legend.append("rect")
        .attr("x", 10)
        .attr("y", 0)
        .attr("width", 20)
        .attr("height", height)
        .attr("stroke", "#aaa")
        .attr("fill", "none");

      legendAxisArea.call(legendAxis);

      bottomTitle.text("# of " + direction.toUpperCase() + " 55 Buses Dispatched");

      weekdays = Math.round(departures.filter(d => d.day < 5).reduce((a, b) => a + b.departures, 0));
      saturdays = Math.round(departures.filter(d => d.day == 5).reduce((a, b) => a + b.departures, 0));
      sundays = Math.round(departures.filter(d => d.day == 6).reduce((a, b) => a + b.departures, 0));
      total = weekdays + saturdays + sundays;

      var fullDirection;

      if (direction == "eb") {
        fullDirection = "eastbound";
      } else if (direction == "wb") {
        fullDirection = "westbound";
      }

      d3.select("#dispatched-summary")
        .html("During an average weekday, there are " + total + " total " + fullDirection + " trips. " + weekdays + " of these trips are scheduled during weekdays, " + saturdays + " trips are scheduled on Saturdays, and " + sundays + " trips are scheduled on Sundays.");

    });
  }

  function type(d) {
    return {
      day: +d.day,
      hour: +d.hour,
      departures: +d.departures
    }
  }

  updateWB();

})();