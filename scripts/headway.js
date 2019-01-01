(function() {
  var stops = [];

  var defaultVal = {
    "eb": [0, 13, 33, 56, 68],
    "wb": [0, 13, 32, 54, 66]
  }

  var margin = {top: 115, right: 50, bottom: 50, left: 30},
      outerWidth = 900,
      outerHeight = 500,
      width = outerWidth - margin.left - margin.right,
      height = outerHeight - margin.top - margin.bottom;

  var svg = d3.select("#svg").append("svg")
      .attr("viewBox", "0 0 " + outerWidth + " " + outerHeight)
      .attr("preserveAspectRatio", "xMidYMid meet")
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var gridWidth;
  var gridHeight = height / 24;
  var numberOfStops;

  var x = d3.scaleLinear()
      .range([0, width]);

  var y = d3.scaleLinear()
      .range([0, gridHeight * 24])
      .domain([0, 23.99]);

  var color = d3.scaleSequential(d3.interpolateYlGnBu);

  var legendY = d3.scaleLinear()
    .domain([0, height]);

  var inverseLegendY = d3.scaleLinear()
    .range([0, height]);

  var legend = svg.append("g")
    .attr("class", "legend")
    .attr("transform", "translate(" + (width) + ",0)");

  var legendAxisArea = legend.append("g")
      .attr("class", "axis axis--y")
      .attr("transform", "translate(30,0)");

  var legendAxis = d3.axisRight()
    .scale(inverseLegendY)
    .ticks(4)
    .tickSize(0);

  var yAxis = d3.axisLeft()
      .scale(y)
      .ticks(24)
      .tickSize(0)
      .tickFormat(hr => {
        var now = new Date();
        now.setHours(hr, 0, 0, 0);
        return d3.timeFormat("%-I%p")(now).toLowerCase();
      });

  var xAxis = svg.append("g");

  xAxis.attr("class", "axis axis--x");

  svg.append("g")
      .attr("class", "axis axis--y")
      .attr("transform", "translate(0," + gridHeight / 2 + ")")
      .call(yAxis);

  var bottomAxis = svg.append("g")
    .attr("class", "bottomAxis")
    .attr("transform", "translate(0," + height + ")");

  var quantizeX = d3.scaleQuantize()
      .domain([0, width / 2])
      .range([0, 1, 2, 3, 4]);

  var bandX = d3.scaleBand()
    .domain([0, 1, 2, 3, 4])
    .range([0, width / 2])
    .align(0.5);

  var offSet = ((width / 2) / quantizeX.range().length) / 2;

  var slider = d3.select("#slider").append("svg")
      .attr("width", width / 2)
      .attr("height", 50)
      .attr("id", "slider-svg")
    .append("g")
      .attr("transform", "translate(0,30)");

  slider.append("line")
      .attr("class", "track")
      .attr("x1", quantizeX.domain()[0] + offSet)
      .attr("x2", quantizeX.domain()[1] - offSet)
    .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
      .attr("class", "track-inset")
    .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
      .attr("class", "track-overlay")
      .call(d3.drag()
          .on("start.interrupt", function() { slider.interrupt(); })
          .on("start drag", function() { hue(d3.event.x); updateData(quantizeX(handleLeft.attr("cx")), quantizeX(handleRight.attr("cx"))); }));

  slider.insert("g", ".track-overlay")
      .attr("class", "ticks")
      .attr("transform", "translate(0," + 18 + ")")
    .selectAll("text")
    .data(quantizeX.range())
    .enter().append("text")
      .attr("x", d => bandX(d) + offSet)
      .attr("text-anchor", "middle")
      .text(d => d);

  slider.append("text")
      .attr("dx", width / 4)
      .attr("dy", "-2em")
      .attr("text-anchor", "middle")
      .style("font", "10px sans-serif")
      .text("Headway range (minutes)");


  var handleLeft = slider.insert("circle", ".track-overlay")
      .attr("class", "handle")
      .attr("r", 9)
      .attr("cx", offSet);

  var handleRight = slider.insert("circle", ".track-overlay")
      .attr("class", "handle")
      .attr("r", 9)
      .attr("cx", bandX(2) + offSet);

  function hue(h) {
    if ((Math.abs(handleLeft.attr("cx") - h) < 60) && 
      (h + offSet < handleRight.attr("cx"))) {
      handleLeft.attr("cx", bandX(quantizeX(h)) + offSet);
    } else if ((Math.abs(handleRight.attr("cx") - h) < 60) && 
      (handleLeft.attr("cx") < h + offSet)) {
      handleRight.attr("cx", bandX(quantizeX(h)) + offSet);
    } 
  }

  var bottomCaptionLeft = bottomAxis.append("text")
    .attr("id", "eb")
    .attr("x", 0)
    .attr("y", 20)
    .attr("text-anchor", "start")
    .style("font", "bold 16px sans-serif")
    .html("Eastbound") // &#8594
    .style("cursor", "pointer")
    .on("click", function(d) { updateEB(d3.select("#route-select").node().value) });

  var bottomCaptionRight = bottomAxis.append("text")
    .attr("id", "wb")
    .attr("x", width)
    .attr("y", 20)
    .attr("text-anchor", "end")
    .style("font", "bold 16px sans-serif")
    .html("Westbound") //&#8592 
    .style("cursor", "pointer")
    .on("click", function(d) { updateWB(d3.select("#route-select").node().value) });

  function updateEB(route) {
    if (!d3.select("#eb").classed("active")) {
      d3.select("#wb").classed("active", null);
      stops = [];
      bottomCaptionRight.attr("opacity", 0.5).html("Westbound");
      bottomCaptionLeft.attr("opacity", 1).html("Eastbound &#8594");
      updateDirection("eb", route);
      d3.select("#eb").classed("active", true);
    }
  }

  function updateWB(route) {
    if (!d3.select("#wb").classed("active")) {
      d3.select("#eb").classed("active", null);
      stops = [];
      bottomCaptionLeft.html("Eastbound");
      bottomCaptionRight.html("&#8592 Westbound");
      svg.attr("opacity", 0.5);
      updateDirection("wb", route);
      svg.attr("opacity", 1);
      d3.select("#wb").classed("active", true);
    }
  }

  function updateData(lower, upper) {
    d3.selectAll(".cell")
      .attr("fill", d => color(d.count.reduce((a, b, i) => {
        return (i >= lower && i < upper) ? a+b : a;
      }, 0)))
      .select("title")
        .text(d => d.count.reduce((a, b, i) => {
          return (i >= lower && i < upper) ? a+b : a;
        }, 0) + " bus bunching incidents at " + d.stopName);
  }

  function updateRoute(route) {
    d3.select("#eb").classed("active", null);
    updateEB(route);
  }

  var routeSelect = d3.select("#route-select")
      .on("change", function(d) {
        console.log(d3.select("#route-select").node().value);
        updateRoute(d3.select("#route-select").node().value);
      });

  routeSelect.selectAll("option")
      .data([{route: 55, name: "Garfield"}, {route: 66, name: "Chicago"}, {route: 73, name: "Armitage"}, {route: 77, name: "Belmont"}])
    .enter().append("option")
      .attr("value", d => d.route)
      .text(d => d.route + " " + d.name)
      

  function updateDirection(direction, route) {
    svg.classed("loading", true);
    d3.tsv("data/processed/headways/" + route + "_headways_" + direction + ".tsv", type, function(error, headway) {
      if (error) throw error;

      if (direction == "wb") {  
        stops.reverse();
        headway.forEach(e => e.counts.reverse());
      }

      d3.selectAll(".axistext").remove();
      d3.select("#chart").remove();
      //d3.selectAll("rect").remove();

      numberOfStops = headway[0].counts.length;
      gridWidth = Math.ceil(width / numberOfStops);

      x.domain([0, numberOfStops]);
      color.domain([0, d3.max(headway.reduce((a, b) => a.concat(b.counts), []), d => d.count.reduce((c,e) => { return c + e; }, 0))]);

      xAxis.selectAll("text")
          .data(stops)
        .enter().append("text")
          .attr("class", (_, i) => "axistext stop" + i)
          .attr("dx", "0.75em")
          .attr("dy", "0.75em")
          .attr("transform", (_, i) => "translate(" + x(i) + ",0) rotate(-65)")
          .style("visibility", (_, i) => defaultVal[direction].includes(i) ? "visible" : "hidden")
          .style("text-anchor", "start")
          .style("font", "9px sans-serif")
          .text(d => d);

      var rows = svg.append("g").attr("id", "chart").selectAll(".row")
          .data(headway)
        .enter().append("g")
          .attr("class", (_, i) => "row hour" + i)

      var cells = rows.selectAll("rect")
          .data(d => stops.map((stop, i) => {
            return { hour: d.hour, count: d.counts[i].count, stopName: stop}; 
          }))
        .enter().append("rect")
          .attr("x", (_, i) => x(i))
          .attr("y", d => y(d.hour))
          .attr("class", (_, i) => "cell stop" + i)
          .attr("fill", d => color(d.count[0] + d.count[1]))
          .attr("width", gridWidth)
          .attr("height", gridHeight)
          .on("mouseover", function(_, i) {
            d3.select("text.stop" + i).style("visibility", "visible");
            d3.select("#chart").insert("rect")
                .attr("id", "cell-selection")
                .attr("x", d3.select(this).attr("x"))
                .attr("y",  d3.select(this).attr("y"))
                .attr("width", gridWidth)
                .attr("height", gridHeight)
                .attr("fill", "none")
                .attr("stroke", "red")
                .attr("stroke-width", "1.5px");
          })
          .on("mouseout", function(_, i) {
            if (!defaultVal[direction].includes(i)) {
              d3.select("text.stop" + i).style("visibility", "hidden");
            }
            d3.select("#cell-selection").remove();
          })
        .append("title")
          .text(d => d.count[0] + d.count[1] + " bus bunching incidents at " + d.stopName);


      legendY.range(color.domain());
      inverseLegendY.domain(color.domain());

      legend.selectAll(".bands")
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

      d3.select("#chart").append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", width)
        .attr("height", height)
        .attr("stroke", "#aaa")
        .attr("fill", "none");

      legendAxisArea.call(legendAxis);
      svg.classed("loading", null);
    });
  }

  function type(d, i) {

    if (!i) for (var k in d) {
      if (k != "hour") {
        stops.push(k);
      }
    }

    return {
      hour: +d.hour,
      counts: stops.map(s => { return {stop: s, count: JSON.parse(d[s]) }; })
    };
  }

  //updateWB(d3.select("#route-select").node().value);
  updateWB("55");

})();