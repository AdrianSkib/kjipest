const express = require("express");
const bodyParser = require("body-parser");
var MongoClient = require('mongodb');
var cors = require('cors');
// const localtunnel = require('localtunnel');

// Setup express app
const app = express();
app.use(
    bodyParser.urlencoded({
        extended: false
    })
);
app.use(bodyParser.json());

// Configure Mongo
const dbURL = "mongodb://localhost:27017/";

// // Connect to Mongo 
MongoClient.connect(dbURL, function(err, dbclient) {
    if (err) {throw err;}
    var db = dbclient.db('KjipestDB');
    console.log("Mongo connected!");
    var mysort = { kjipestScore: -1 };
    db.collection("Locations").find({}, { projection: { _id: 0, location: 1, kjipestScore: 1 } }).sort(mysort).toArray(function(err, result) {
        if (err) {console.log(err);};
        // console.log(result);
    });
  });

// Make sure connections are accepted from frontend
app.use(cors({origin: 'http://kjipest.surge.sh'}));

// Set up GET routine
app.get("/sorted/", (req, res) => {
    // // Connect to Mongo 
    MongoClient.connect(dbURL, function(err, dbclient) {
    if (err) {throw err;}
    var db = dbclient.db('KjipestDB');
    console.log("Mongo connected!");
    // Sort by kjiphet and return sorted list of locations and their kjipestScore
    var mysort = { kjipestScore: -1 };
    db.collection("Locations").find({}, { projection: { _id: 0, location: 1, kjipestScore: 1 } }).sort(mysort).toArray(function(err, result) {
        if (err) {
            console.log(err);
            res.json(err);
        };
        // console.log(result);
        res.json(result);
    });
  });
});



// Specify the Port where the backend server can be accessed and start listening on that port
const port = process.env.PORT || 5000;
// Set up tunnel from https://kjipest.localtunnel.me to https://localhost:5000
// const tunnel = localtunnel(port, { subdomain: 'kjipest'}, (err, tunnel) => {
//     if (err) console.log(err)
//     console.log("Tunnel open!")
//     tunnel.on('close', () => {
//         console.log("Tunnel closed!")
//       });
// });

// (async () => {
//     const tunnel = await localtunnel({ port: 5000 });
//     console.log("Tunnel open on ")
//     console.log(tunnel.url)
//     tunnel.on('close', () => {
//         console.log("Tunnel closed!")
//       });
//   })();
const hostname = '0.0.0.0';
app.listen(port, hostname, () => console.log(`Server up and running on port ${port}.`));


