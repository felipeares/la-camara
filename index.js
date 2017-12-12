const express = require('express');
const app = express();
var path = require("path");
var fs = require('fs');

app.get('/', function (req, res) {
	res.sendFile(path.join(__dirname+'/www/index.html'));
});
app.get('/error', function (req, res) {
	res.sendFile(path.join(__dirname+'/www/error.html'));
});
app.get('/dist', function (req, res) {
	res.sendFile(path.join(__dirname+'/www/dist/index.html'));
});
app.get('/test', function (req, res) {
	res.sendFile(path.join(__dirname+'/www/tests/index.html'));
});

app.get('/visualizations/:visName', function (req, res) {
	if (fs.existsSync(__dirname+'/visualizations/'+req.params.visName+'.html')) {
	    res.sendFile(path.join(__dirname+'/visualizations/'+req.params.visName+'.html'));
	}
	else {
		res.sendFile(path.join(__dirname+'/visualizations/index.html'));
	}
	
});

app.use(express.static('./www/'));

app.listen(3000, function () {
	console.log('Example app listening on port 3000!');
});
