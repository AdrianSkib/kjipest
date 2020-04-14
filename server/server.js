const express = require("express");
const bodyParser = require("body-parser");
var MongoClient = require("mongodb");
var cors = require("cors");
// Setup express app
const app = express();
app.use(
  bodyParser.urlencoded({
    extended: false,
  })
);
app.use(bodyParser.json());
// Configure Mongo
const dbURL = "mongodb://localhost:27017/";
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
// Set up GET routine
app.get("/", (req, res) => {
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
// Specify the Port where the backend server can be accessed and start listening on that port
const port = process.env.PORT || 8888;
const hostname = "0.0.0.0";
app.listen(port, hostname, () =>
  console.log(`Server up and running on port ${port}.`)
);
