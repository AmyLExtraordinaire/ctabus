var rtInfo = {
	"X49": {
		'rtno': "X49",
		'rtnm': "Western Express",
		'neg': "Southbound",
		'pos': "Northbound", 
		'pidNeg': 7871,
		'pidPos': 7873,
		'stpidTerminalNeg': 8307,
		'stpidTerminalPos': 14182,
		'rtinfo': "<a>Route X49 Western Express</a> operates during morning and evening rush hour every weekday. It travels along the same path as Route 49 Western but makes fewer stops, stopping approximately every 4 blocks or half-mile."
	},
	"52": {
		'rtno': "52",
		'rtnm': "Kedzie/California",
		'neg': "Southbound",
		'pos': "Northbound", 
		'pidNeg': 6650,
		'pidPos': 6647,
		'stpidTerminalNeg': 3099,
		'stpidTerminalPos': 17786,
		'rtinfo': "<a>Route 52 Kedzie/California</a> operates from early morning to late evening every day along California between Chicago and Addison and along Kedzie between Chicago and 63rd Place. The route serves neighborhoods on the Northwest and Southwest Sides, including Avondale, Logan Square, Humboldt Park, East Garfield Park, North Lawndale, Little Village, Brighton Park, Gage Park, and Chicago Lawn."
	},
	"55": {
		'rtno': "55",
		'rtnm': "Garfield",
		'neg': "Westbound",
		'pos': "Eastbound", 
		'pidNeg': 5425,
		'pidPos': 5424,
		'stpidTerminalNeg': 14122,
		'stpidTerminalPos': 10565,
		'rtinfo': "<a>Route 55 Garfield</a> operates at all hours every day of the week along 55th Street and Garfield Boulevard between the Museum of Science and Industry (MSI) and 55th/St. Louis Ave. Service is available between MSI and the Midway Orange Line Station every day between 4:00AM to 1:00AM. The route serves a number of neighborhoods, including Hyde Park, Back of the Yards, Englewood, Gage Park, and West Elsdon."
	},
	"73": {
		'rtno': "73",
		'rtnm': "Armitage",
		'neg': "Westbound",
		'pos': "Eastbound", 
		'pidNeg': 2169,
		'pidPos': 2170,
		'stpidTerminalNeg': 14179,
		'stpidTerminalPos': 15417,
		'rtinfo': "<a>Route 73 Armitage</a> operates from early morning to late evening on weekdays along Armitage Avenue between Clark & North and Grand & Laramie. Service ends in the early evening on weekends. The route serves neighborhoods on the North and West Sides, including Lincoln Park, Bucktown, Logan Square, Hermosa, and Belmont Craigin."
	}
}

var directionAbbrv = {
  "Northbound": "NB",
  "Eastbound": "EB",
  "Southbound": "SB",
  "Westbound": "WB"
}

var routeSelect = d3.select("#route-select");

routeSelect.selectAll("option")
		.data(Object.values(rtInfo))
	.enter().append("option")
		.attr("value", d => d.rtno)
		.attr("id", d => "rt-" + d.rtno)
		.text(d => d.rtno + " " + d.rtnm);

routeSelect.property("value", "55");

routeSelect.on("change.page", updatePageText);

function updatePageText() {
	var rt = document.getElementById("route-select").value;
	d3.selectAll(".text-rtno").text(rtInfo[rt].rtno);
	d3.selectAll(".text-rtnm").text(rtInfo[rt].rtnm);
	d3.select("#text-rtinfo").html(rtInfo[rt].rtinfo);
	d3.select("#text-rtinfo a").attr("href", "http://www.transitchicago.com/bus/" + rt);
}

updatePageText();

function mod(n, m) {
  return ((n % m) + m) % m;
}