(function() {

  var pi = Math.PI,
      tau = 2 * pi;

  var width = 200,
      height = 100;

  var color = d3.scaleSequential(d3.interpolateMagma);

  var maxBunching;

  // Unit projection
  var smallProjection = d3.geoMercator()
      .scale(1 / tau)
      .translate([0, 0]);

  var bigProjection = d3.geoMercator()
      .scale(1 / tau)
      .translate([0, 0]);

  var path = d3.geoPath();
      //.projection();

  var fullViz = d3.select("#bunching-svg");

  var legendWidth = 100;

  var legendY = d3.scaleLinear()
      .domain([0, legendWidth]);

  var inverseLegendY = d3.scaleLinear()
      .range([0, legendWidth]);

  var tooltip = d3.select("body")
      .append("div")
      .attr("id", "tooltip")
      .style("visibility", "hidden");

  d3.queue()
      .defer(d3.json, "data/project_page/geometry/55_5425.topojson")
      .defer(d3.json, "data/project_page/bunching/55_Westbound_bunching.json")
      .defer(d3.json, "data/project_page/geometry/55_5424.topojson")
      .defer(d3.json, "data/project_page/bunching/55_Eastbound_bunching.json")
      .await(ready);

  function ready(error, rtWB, bunchingWB, rtEB, bunchingEB) {
    if (error) throw error;

    var bbox = path.projection(smallProjection).bounds(topojson.feature(rtEB, rtEB.objects.stops));

    var deltaX = bbox[1][0] - bbox[0][0];
    var deltaY = bbox[1][1] - bbox[0][1];
    var vertical = Math.abs(deltaX * 2) < deltaY;

    console.log(vertical);

    if (vertical) {
      width = 100;
      height = 200;
    }

    // pre-filter data
    bunchingWB = bunchingWB.filter(b => b.terminal == "wait|14122");
    bunchingEB = bunchingEB.filter(b => b.terminal == "wait|10565");

    bunchingEB.forEach((data, i) => {
      var wrapper = fullViz
          .append("div")
          .attr("width", width)
          .attr("height", height + 20);

      var figure = wrapper.append("svg")
          .attr("class", i ? " inactive" : " active")
          .attr("id", "small-map-wrapper" + i)
          .attr("width", width)
          .attr("height", height + 20);

      var map = figure.append("svg")
          .attr("class", "small-map")
          .attr("width", width)
          .attr("height", height);

      drawMap(bbox, width, height, smallProjection, map);
    });

    var fullWidth = width * bunchingEB.length
    var fullHeight = height * 4
    var bigWrapper = fullViz
        .append("div")
        .attr("width", fullWidth)
        .attr("height", fullHeight);

    var bigMap = bigWrapper.append("svg")
          .attr("id", "fullmap")
          .attr("width", fullWidth)
          .attr("height", fullHeight);

    drawMap(bbox, fullWidth, fullHeight, bigProjection, bigMap);

    var buttonWB = drawTextButton(bigMap, 30, fullHeight - 10, "&#8592 WB", "bold 16px sans-serif");

    buttonWB
        .attr("class", "update-inactive")
        .on("click", function (d) {
          update(bunchingWB, rtWB);
          if(!d3.select(this).classed("update-active")) {
            toggleClasses("update-active", "update-inactive", d3.select(this));
          }
        });

    var buttonEB = drawTextButton(bigMap, fullWidth - 30, fullHeight - 10, "EB &#8594", "bold 16px sans-serif");

    buttonEB
        .attr("class", "update-active")
        .on("click", function (d) {
          update(bunchingEB, rtEB);
          if(!d3.select(this).classed("update-active")) {
            toggleClasses("update-active", "update-inactive", d3.select(this));
          }
        });

    update(bunchingEB, rtEB)
  }

  function drawMap(b, width, height, projection, svg) {
    var s = 0.95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height),
        t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];

    var tiles = d3.tile()
        .size([width, height])
        .scale(s)
        .translate([t[0], t[1]])
        ();

    projection
        .scale(s / tau)
        .translate([t[0], t[1]]);

    var map = svg.append("g")
      .selectAll("image").data(tiles).enter().append("image")
        .attr("xlink:href", d => "http://" + "abc"[d[1] % 3] + ".basemaps.cartocdn.com/light_all/" + d[2] + "/" + d[0] + "/" + d[1] + ".png")
        .attr("x", d => (d[0] + tiles.translate[0]) * tiles.scale)
        .attr("y", d => (d[1] + tiles.translate[1]) * tiles.scale)
        .attr("width", tiles.scale)
        .attr("height", tiles.scale);

    return map;
  }

  function drawRoute(svg, data, geometry, projection) {
    var route = svg.selectAll(".stops")
        .data(topojson.feature(geometry, geometry.objects.stops).features)
      .enter().append("path")
        .attr("d", path.projection(projection))
        .attr("fill", "none")
        .attr("stroke", d => color(data.values[d.properties.stpid].proportion))
        .attr("pointer-events", "visibleStroke");

    return route;
  }

  function updateColorScale(data) {
    maxBunching = d3.max(data, b => d3.max(Object.values(b.values).map(v => v.proportion)));
    color.domain([0, maxBunching]);
  }

  function updateColor(data) {
    d3.selectAll(".big-map-path")
        .attr("stroke", d => color(data.values[d.properties.stpid].proportion));
  }

  function drawSmallMultiples(data, geometry, projection) {
    data.forEach((d, i) => {
      var smallMap = d3.select("#small-map-wrapper" + i);
      drawSmallFigure(smallMap, d, geometry, projection);
    });
  }

  function drawSmallFigure(svg, data, geometry, projection) {
    svg = svg.append("g").attr("class", "small-figure-info");

    var route = drawRoute(svg, data, geometry, projection);

    route.attr("stroke-width", 2)

    var button = drawTextButton(svg, width / 2, height + 15, data.time_of_day, "bold 12px sans-serif");
  }

  function drawTextButton(svg, x, y, text, font) {
    var button = svg.append("g");
    var rectLayer = button.append("g");
    var textLayer = button.append("g");

    var text = textLayer.append("text")
        .attr("text-anchor", "middle")
        .attr("x", x)
        .attr("y", y)
        .style("font", font)
        .html(text)
        .style("cursor", "pointer");

    var textBBox = text.node().getBBox();

    var rect = rectLayer.append("rect")
        .attr("class", "textbox")
        .attr("rx", 3)
        .attr("ry", 3)
        .attr("x", textBBox.x - 2)
        .attr("y", textBBox.y - 1)
        .attr("width", textBBox.width + 4)
        .attr("height", textBBox.height + 2)
        .attr("fill", "#bbb");

    return button;
  }

  function drawFigure(data, geometry, projection) {
    var svg = d3.select("#fullmap")
    svg = svg.append("g").attr("class", "big-figure");

    var route = drawRoute(svg, data, geometry, projection);

    route.attr("class", "big-map-path")
        .attr("stroke-width", 5)
        .on("mouseover", function (d) {
          showToolTip(this, d, data);
        })
        .on("mouseout", function (d) {
          d3.select(this).attr("stroke-width", 5);
          tooltip.style("visibility", "hidden");
        })

    var legend = svg.append("g")
        .attr("class", "legend")
        .attr("transform", "translate(20," + (height - 50) + ")");

    inverseLegendY.domain(color.domain());
    legendY.range(color.domain());

    var legendAxisArea = legend.append("g")
        .attr("class", "axis axis--y")
        .attr("transform", "translate(0,15)")

    var legendAxis = d3.axisBottom()
      .scale(inverseLegendY)
      .tickValues([0, maxBunching / 2, maxBunching])
      .tickSize(3)
      .tickFormat(d3.format(".0%"))

    legendAxisArea.call(legendAxis);

    legend.selectAll(".bands")
        .data(d3.range(legendWidth), d => d)
      .enter().append("rect")
        .attr("x", d => d)
        .attr("y", 10)
        .attr("width", 1)
        .attr("height", 5)
        .attr("fill", d => color(legendY(d)));
  }

  function toggleClasses(a, b, e) {
    d3.selectAll("." + a).classed(a, false).classed(b, true);
    e.classed(a, true).classed(b, false);
  }

  function showToolTip(self, d, data) {
    d3.select(self).attr("stroke-width", 7);
    tooltip.style("visibility", "visible")
        .html(d.properties.stpnm + "<br />" + data.values[d.properties.stpid].count + " incidents, " + d3.format(".0%")(data.values[d.properties.stpid].proportion) + " of trips");

    var tip = document.getElementById("tooltip")
    var tipw = tip.offsetWidth
    var tiph = tip.offsetHeight

    var bbox = self.getBBox();
    var matrix = self.getScreenCTM();
    var svg = document.getElementById("fullmap");
    var pt = svg.createSVGPoint();
    pt.x = bbox.x  + window.scrollX + (bbox.width / 2) - (tipw / 2);
    pt.y = bbox.y - tiph + window.scrollY;
    var trans = pt.matrixTransform(matrix);

    tooltip
        .style("left", (trans.x) + "px")   
        .style("top", (trans.y - 10) +  "px");
  }

  function update(data, geometry) {
    d3.selectAll(".big-figure").remove();
    d3.selectAll(".small-figure-info").remove();
    updateColorScale(data);
    drawSmallMultiples(data, geometry, smallProjection);
    drawFigure(data[0], geometry, bigProjection);

    toggleClasses("active", "inactive", d3.select("#small-map-wrapper0"));
    //d3.select("#small-map-wrapper0").classed("active", true)

    data.forEach((row, i) => {
      d3.select("#small-map-wrapper" + i)
        .on("click", function(d) {
          if(!d3.select(this).classed("active")) {
            toggleClasses("active", "inactive", d3.select(this));
            var newData = data.filter(b => b.time_of_day == row.time_of_day)[0];
            updateColor(newData);
            d3.selectAll(".big-map-path")
              .on("mouseover", function(e) {
                showToolTip(this, e, newData);
              })
          }
        });
    });
  }

})();