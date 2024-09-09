const {Server, Socket} = require("socket.io");
const io = new Server();
let Config = require("./Config");
let SocketClient = require("./SocketClient")
io.resource_members = [];

io.socket_clients ={};

io.on("connection", (socket) => {
    console.log("User connected! Socket ID: "+socket.id);
    io.resource_members.push(socket)
    if(socket.handshake.query.URL || false){
        socket.worker_url = socket.handshake.query.URL;
        if (io.socket_clients[socket.worker_url]){
            io.socket_clients[socket.worker_url].AddMember(socket)
        }else{
            io.socket_clients[socket.worker_url] = new SocketClient(socket.worker_url, socket, io);
        }
    }
    socket.on("disconnect", (reason) => {

        console.log("User disconnected " + reason)
        if(socket.worker_url){
            io.socket_clients[socket.worker_url].RemoveMember(socket)
        }

        var resource_index = io.resource_members.indexOf(socket);
        if (resource_index !== -1) {
            io.resource_members.splice(resource_index, 1);
            console.log(socket.id + " element removed from resource_members")
        }
    });
});

io.SendResourceInfo = function (info) {
    io.resource_members.forEach(element => element.emit("resource_info", info));
}


io.listen(Config.Port);
console.log(Config.Port)
console.log("Open")

module.exports = io;
