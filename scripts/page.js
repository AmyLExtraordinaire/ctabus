var rtInfo = {
	"55": {
		'rtno': "55",
		'rtnm': "Garfield",
		'neg': "Westbound",
		'pos': "Eastbound", 
		'pidNeg': 5425,
		'pidPos': 5424,
		'stpidTerminalNeg': 14122,
		'stpidTerminalPos': 10565,
		'fromPos1': "55th/St. Louis Ave",
		'toPos1': "the Museum of Science and Industry (MSI)",
		'fromNeg1': "the Museum of Science and Industry (MSI)",
		'toNeg1': "55th/St. Louis Ave",
		'fromPos2': "the Midway Orange Line Station",
		'toPos2': "MSI",
		'fromNeg2': "MSI",
		'toNeg2': "the Midway Orange Line Station",
		'serviceDays': "every day",
		'servicePeriod': "at all hours",
		'serviceRt': "55th Street and Garfield Boulevard",
		'secondaryServiceDays': "every day",
		'secondaryServicePeriod': "between 4:00AM and 1:00AM",
		'secondaryServiceRt': "55th Street and Garfield Boulevard",
		'rtinfo': "The route serves a number of neighborhoods, including Hyde Park, Back of the Yards, Englewood, Gage Park, and West Elsdon."
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
		'fromPos1': "Grand & Laramie",
		'toPos1': "Clark & North",
		'fromNeg1': "Clark & North",
		'toNeg1': "Grand & Laramie",
		'fromPos2': null,
		'toPos2': null,
		'fromNeg2': null,
		'toNeg2': null,
		'serviceDays': "every day",
		'servicePeriod': "early morning to early evening",
		'serviceRt': "Armitage Avenue",
		'secondaryServiceDays': "every day",
		'secondaryServicePeriod': "early morning to early evening",
		'secondaryServiceRt': "Armitage Avenue",
		'rtinfo': "The route serves a number of neighborhoods, including Lincoln Park, Bucktown, Logan Square, Hermosa, and Belmont Craigin."
	}
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
}

updatePageText();

/*
Definitons
Dynamically updated on project page
	Route Number
	Route Name
	Default chart values -- same for most routes
	Terminals
	Directions

Python Scripts
	Used stopids
	Used pids*/

