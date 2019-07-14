(function() {
  
  var margin = {top: 30, right: 0, bottom: 0, left: 0},
      outerWidth = 150 + margin.left + margin.right,
      width = outerWidth - margin.left - margin.right,
      gridSize = 10,
      outerHeight = (gridSize * 24) + margin.top + margin.bottom,
      height = outerHeight - margin.top - margin.bottom;
/*
  var svg = d3.select("#svg-departures").append("svg")
      .attr("viewBox", "0 0 " + outerWidth + " " + outerHeight)
      .attr("preserveAspectRatio", "xMidYMid meet")
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");*/

  var directionAbbrv = {
    "Northbound": "NB",
    "Eastbound": "EB",
    "Southbound": "SB",
    "Westbound": "WB"
  }

/*
  var svg = d3.select("#svg-departures").append("svg")
      .attr("width", outerWidth)
      .attr("height", outerHeight)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var svg2 = d3.select("#svg-departures").append("svg")
      .attr("width", outerWidth)
      .attr("height", outerHeight)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");*/
  var parseTime = d3.timeFormat("%-I%p");

  var x = d3.scaleLinear()
      .range([0, width])
      .domain([0, 59]);

  var x2 = d3.scaleLinear()
      .range([0, 30])
      .domain([0, 10]);

  var y = d3.scaleLinear()
      .range([0, gridSize])
      .domain([0, 0.5])
      //.domain([0, 6.99]);
  /*
  var color = d3.scaleSequential(d3.interpolateGreys)
      .domain([0, 100]);

  var grids = svg.selectAll(".grid")
      .data(Array(22-6 + 1));

  grids.enter().append("rect")
      .attr("class", "grid")
      .attr("x", d => gridSize)
      .attr("y", (_, i) => i * gridSize)
      .attr("width", 60)
      .attr("height", gridSize)
      .attr("fill", "none")
      .attr("stroke", "none")
      .on("mouseover", function(d) {
        d3.select(this).style("stroke", "red")
          .style("stroke-width", "2px");
      })
      .on("mouseout", function(d) {
        d3.select(this).style("stroke", "black").style("stroke-width", "1px");
      })*/
  function updateRouteDepartures() {
    var rt = document.getElementById("route-select").value;

    d3.select("#departures-table").selectAll("tr").remove()

    d3.queue()
        .defer(d3.json, "data/project_page/departures/" + rt + "_daily_departures.json?")
        .defer(d3.json, "data/project_page/departures/" + rt + "_hourly_departures.json?")
        .await(process);
  }

  routeSelect.on("change.departures", updateRouteDepartures);

  function process(error, days, hrs) {
    var rt = document.getElementById("route-select").value;

    buildHistograms(hrs[rtInfo[rt]["pidNeg"]]);

    var tbody = d3.select("#departures-tbody")

    var total;
    var subtotal;

    addTableRows(days[0]);
    total = calculateDirectionTotals(days[0]);
    addTableRows(days[1]);
    subtotal = calculateDirectionTotals(days[1]);
    d3.select("#row" + rtInfo[rt]["pidNeg"]).classed("active", true);
 
    total.w += subtotal.w;
    total.s += subtotal.s;
    total.u += subtotal.u;

    function addTableRows(days) {
      tbody.append("tr")
          .html(d => "<th>" + days.direction + "</th><th class='c'>Weekdays</th><th class='c'>Saturday</th><th class='c'>Sunday</th>")

      tbody.selectAll("." + days.direction + "row")
          .data(days.data)
        .enter().append("tr")
          .attr("class", days.direction + "row")
          .attr("id", d => "row" + d.pid)
          .html(d => "<td>" + d.origin + "<br>to " + d.destination + "</td><td class='c'>" + format(d.counts.w) + "</td><td class='c'>" + format(d.counts.s) + "</td><td class='c'>" + format(d.counts.u) + "</td>")
          .on("mouseover", function(d) {
            d3.select("tr.active").classed("active", false);
            d3.select(this).classed("active", true);
            buildHistograms(hrs[d.pid]);
            d3.select("#svg-departures-caption").html(d.origin + " -> " + d.destination);
          })
          .on("mouseout", function(_, i) {
          })
          .each(d => d.pid == rtInfo[rt]["pidNeg"] ? d3.select("#svg-departures-caption").html(d.origin + " -> " + d.destination) : null)
    }

    function format(n) {
      return n ? Math.round(n) : "--";
    }

    function calculateDirectionTotals(days) {
      var dayTotal = {"w": 0, "s": 0, "u": 0};

      days.data.forEach(d => {
        dayTotal.w += d.counts.w;
        dayTotal.s += d.counts.s;
        dayTotal.u += d.counts.u;
      });

      if (d3.selectAll("." + days.direction + "row").size() > 1) {
        tbody.append("tr")
            .html(d => "<th>" + directionAbbrv[days.direction] + " Total</th><th class='c'>" + format(dayTotal.w) + "</th><th class='c'>" + format(dayTotal.s) + "</th><th class='c'>" + format(dayTotal.u) + "</td>");
      }

      return dayTotal;
    }

    var tfoot = d3.select("#departures-tfoot")
    tfoot.append("tr")
        .style("border-top", "1px solid #aaa")
        .html(d => "<th>All Trips</th><th class='c'>" + format(total.w) + "</th><th class='c'>" + format(total.s) + "</th><th class='c'>" + format(total.u) + "</th>");
  
  /*
    svg2.append("g")
        .attr("class", "axis axis--y")
      .selectAll(".ytick")
      .data(hrs)
      .enter()
      .append("text")
          .attr("id", d => "hr" + d.hr)
          .attr("dx", "-0.25em")
          .attr("y", (_, i) => i * gridSize + gridSize / 2)
          .style("text-anchor", "middle")
          .style("alignment-baseline", "middle")
          .style("font", "8px sans-serif")
          .text(d => d.hr);

    svg2.selectAll(".row")
        .data(hrs)
      .enter().append("g")
        .attr("transform", (_, i) => "translate(" + gridSize + "," + (gridSize * i) + ")")
        .attr("width", 120)
        .attr("height", gridSize)
      .selectAll(".hist")
        .data(d => {console.log(d); return d.data})
      .enter().append("rect")
        .attr("x", (d, i) => gridSize + (i * 2))
        .attr("y", 0)
        .attr("width", 2) 
        .attr("height", gridSize)
        .attr("stroke", "none")
        .attr("fill", d => color(d))



    svg.selectAll(".hist")
        .data(hrs)
      .enter().append("line")
          .attr("x1", (_, i) => gridSize + i)
          .attr("x2", (_, i) => gridSize + i)
          .attr("y1", (_, i) => gridSize)
          .attr("y2", (d, i) => gridSize - y(d))
          .attr("stroke", "black")
  */
  };

  function buildHistograms(data) {
    var rt = document.getElementById("route-select").value;

    d3.select("#svg-departures").selectAll("svg").remove()

    var svg = d3.select("#svg-departures").selectAll("svg")
        .data(data)
      .enter().append("svg")
        .attr("width", outerWidth)
        .attr("height", outerHeight)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("text")
        .attr("x", (outerWidth + gridSize) / 2)
        .attr("y", 0 - (margin.top / 4))
        .attr("text-anchor", "middle")
        .style("font-size", "10px")
        .style("font-weight", "bold")
        .text(d => dowToString(d.dow))

    var hours = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1, 2];
    svg.append("g")
        .attr("class", "axis axis--y")
      .selectAll(".ytick")
        .data(hours)
      .enter().append("text")
        .attr("id", d => "hr" + d)
        //.attr("dx", "-0.25em")
        .attr("x", gridSize * 1.5)
        .attr("y", (_, i) => i * gridSize + gridSize / 2)
        .style("text-anchor", "end")
        .style("alignment-baseline", "middle")
        .style("font", "8px sans-serif")
        .text(d => {
          return d
          //var now = new Date();
          //now.setHours(d.hr, 0, 0, 0);
          //return parseTime(now).toLowerCase();
          
        });

    svg.selectAll("rect")
        .data([0, 10, 20, 30, 40, 50])
      .enter().append("rect")
        .attr("width", 120 / 6)
        .attr("height", gridSize * hours.length)
        .attr("x", d => (gridSize + d) * 2)
        .attr("y", 0)
        .attr("fill", (_, i) => i % 2 == 0 ? "#dfdfdf" : "#f8f8f8")
        .attr("opacity", 0.5);

    svg.selectAll(".row")
        .data(d => d.data)
      .enter().append("g")
        .attr("transform", d => "translate(" + gridSize + "," + (gridSize * mod(d.hr - 3, 24)) + ")")
        .attr("width", 120)
        .attr("height", gridSize)
      .selectAll(".hist")
        .data(d => d.departures)
      .enter().append("rect")
        .attr("x", (_, i) => gridSize + (i * 2))
        .attr("y", d => gridSize - y(d))
        .attr("width", 2) 
        .attr("height", (d, i) => y(d))
        .attr("stroke", "none")
        .attr("fill", "black");
    /*
    svg.append("g")
        .attr("class", "axis axis--y")
      .selectAll(".ytick")
      .data(d => d.data)
      .enter()
      .append("text")
          .attr("id", d => "hr" + d.hr)
          .attr("dx", "-0.25em")
          .attr("x", d => width + gridSize * 2 + x2(d.avg))
          .attr("y", (_, i) => i * gridSize + gridSize / 2)
          .style("text-anchor", "start")
          .style("alignment-baseline", "middle")
          .style("font", "8px sans-serif")
          .text(d => d.avg);*/
  }

  function dowToString(text) {
    if (text == "W") {
      return "Weekdays"
    } else if (text == "S") {
      return "Saturdays"
    } else {
      return "Sundays"
    }
  }

  updateRouteDepartures();

})();