/**
 * Created by dario on 11.05.17.
 */

const Express = require('express');
const CollabServer = require('../../dist').Server;
const CollabCollection = require('../../dist').Collection;
const MongoClient = require('mongodb').MongoClient;

/* Create Express application */
const app = Express();
// Express only serves static assets in production
if (process.env.NODE_ENV === 'production') {
  app.use(Express.static('client/build'));
}



// Create a MongoDB server
const url = 'mongodb://localhost:27017/my-collaborative-app';
MongoClient.connect(url)
  .catch(function (err) {
    if (err) throw err;
  })
;

const options = {
  db: {
    type: 'mongo',
    url
  }
};

// Create a CollabServer instance with MongoDB
CollabServer.start(app, options);

// Create the collection that will hold the shared data.
const documents = new CollabCollection('documents');

// Create the shared form data
documents.create('editor1');
documents.create('editor2');




