const http = require('http');
const { Server } = require("socket.io");
const Config = require("./Config");
const app = require('./API')

const server = http.createServer(app);
const io = new Server(server);
//Create a object to access application variables to share info and methods.
let GloveCloud = {Express:app, HttpServer:server, Socket:io}
app.GloveCloud = GloveCloud;

const Socket = require('./Socket')(GloveCloud);
// io.on('connection', (socket) => {
//     console.log('a user connected');
// });

server.listen(Config.Port, '0.0.0.0',() => {
    console.log('listening on *:'+Config.Port);
});