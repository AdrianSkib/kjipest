const express = require("express");
const bodyParser = require("body-parser");
var MongoClient = require("mongodb");
var fs = require('fs')
var https = require('https')
var cors = require("cors");
const path = require('path');
// Setup express app
const app = express();


app.use(
  bodyParser.urlencoded({
    extended: false,
  })
);
app.use(bodyParser.json());
// Configure Mongo
// const dbURL = "mongodb://localhost:27017/";
const dbURL = "mongodb+srv://kjipestBackend:kpF1CpxQjDAVmFLn@kjipestcluster.tzoop.mongodb.net/kjipestDB";
// // Connect to Mongo
MongoClient.connect(dbURL, function (err, dbclient) {
  if (err) {
    throw err;
  }
  var db = dbclient.db("KjipestDB");
  console.log("Mongo connected!");
  var mysort = { kjipestScore: -1 };
  db.collection("Locations")
    .find({}, { projection: { _id: 0, location: 1, kjipestScore: 1 } })
    .sort(mysort)
    .toArray(function (err, result) {
      if (err) {
        console.log(err);
      }
      // console.log(result);
    });
});
// Make sure connections are accepted from frontend
app.use(cors());
// Set up GET sorted routine
app.get("/sorted/", (req, res) => {
  console.log("Got connection!");
  // // Connect to Mongo
  MongoClient.connect(dbURL, function (err, dbclient) {
    if (err) {
      throw err;
    }
    var db = dbclient.db("KjipestDB");
    // Sort by kjiphet and return sorted list of locations and their kjipestScore
    var mysort = { kjipestScore: -1 };
    db.collection("Locations")
      .find({}, { projection: { _id: 0, location: 1, kjipestScore: 1 } })
      .sort(mysort)
      .toArray(function (err, result) {
        if (err) {
          console.log(err);
          res.json(err);
        }
        res.json(result);
      });
  });
});

// Set up GET routine for getting current pos info based on lat lon
app.get("/lonlat/:lon&:lat", (req, res) => {
  var lon = parseFloat(req.params.lon);
  var lat = parseFloat(req.params.lat);
  console.log("Got lonlat connection! Lon: " + lon + ", lat: " + lat);
  // // Connect to Mongo
  MongoClient.connect(dbURL, function (err, dbclient) {
    if (err) {
      throw err;
    }
    var db = dbclient.db("KjipestDB");
    // Sort by kjiphet and return sorted list of locations and their kjipestScore
    db.collection("Locations")
      .find({ loc: { $near: {$geometry: {type: "Point", coordinates: [lon, lat]}}}})
      // .limit(1)
      .toArray(function (err, result) {
        if (err) {
          console.log(err);
          res.json(err);
        }
        res.json(result[0]);
      });
  });
});

var __dirname = "../app";
app.use(express.static(path.join(__dirname, 'build')));
/* GET React App */
app.get('/', function (req, res) {
  console.log("Got frontend request");
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

// Specify the Port where the backend server can be accessed and start listening on that port
const port = process.env.PORT || 80;
const hostname = "0.0.0.0";
// https.createServer({
//   key: fs.readFileSync('server.key'),
//   cert: fs.readFileSync('server.cert')
// }, app).
app.listen(port, hostname, () =>
  console.log(`Server up and running on port ${port}.`)
);
