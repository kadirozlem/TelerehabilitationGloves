const express = require('express');
const http = require('http');
const { Server } = require("socket.io");
const Config = require("./Config");
const  Home_Route = require('./UserInterface/Routes/Home')
const app = require('./UserInterface')

const server = http.createServer(app);
const io = new Server(server);

let LiveChart = {Express:app, HttpServer:server, Socket:io}
app.LiveChart = LiveChart;

const Socket = require('./Socket')(LiveChart);

server.listen(Config.Port, '0.0.0.0',() => {
    console.log('listening on *:'+Config.Port);
});