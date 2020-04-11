const express = require("express");
// var http = require('http');
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
// app.use(cors({origin: 'http://kjipest.surge.sh'}));
app.use(cors());
// app.use(function(req, res, next) {
//     res.header("Access-Control-Allow-Origin", "*");
//     res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
//     next();
//   });

// app.get('/', (req, res) => {
//     res.send('Hello World!')
// })
// Set up GET routine
app.get("/", (req, res) => {
    // res.send(JSON.stringify('success'));
    // res.send('')
    console.log("Got connection!");
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
const port = process.env.PORT || 8888;
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
// var httpServer = http.createServer(app);
const hostname = '0.0.0.0';
app.listen(port,hostname,() => console.log(`Server up and running on port ${port}.`));
// app.listen(port, hostname, () => console.log(`Server up and running on port ${port}.`));


