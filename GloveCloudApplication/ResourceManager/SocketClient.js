const { Manager  } = require("socket.io-client");
const Config = require("./Config");
const ProjectConfig = require("../Config")
const microtime = require("microtime");

class SocketClient{
    constructor(url,member_socket, io) {
        this.worker_url = url;
        this.url = url+":"+Config.Port;
        this.member_sockets = [member_socket];
        this.io = io;
        this.connected = false;
        this.connectToSocket()
    }

    AddMember(member_socket){
        this.member_sockets.push(member_socket);
        if(this.connected){
            member_socket.emit("worker_connected","connected");
        }
    }

    RemoveMember(member_socket){
        const index = this.member_sockets.indexOf(member_socket);
        if (index > -1) {
            this.member_sockets.splice(index, 1);
        }
        if(this.member_sockets.length==0){
            this.close()
            if(this.io.socket_clients[this.worker_url]){
                delete this.io.socket_clients[this.worker_url];
            }
        }

    }

    connectToSocket(){
        const socketClient=this;
        const manager = new Manager(this.url, {
            autoConnect: true,
            query: {
                DeviceType: ProjectConfig.DeviceTypes.User
            }
        });

        this.socket = manager.socket("/");

        this.socket.on("connect",()=>{
            socketClient.emit("worker_connected","connected")
            console.log("Worker: "+socketClient.url + " connected!")
            socketClient.connected =true;
        })

        this.socket.on("disconnect", (reason) => {
            socketClient.emit("worker_disconnected","disconnected")
            console.log("Worker: "+socketClient.url + " disconnected!")
            socketClient.connected=false;
        });

        this.socket.on("connect_error", (err) => {
            socketClient.emit("worker_connect_error","connection_error")
            console.log("Worker: "+socketClient.url + " connection error -> "+err)
            socketClient.connected=false;
        });

        this.socket.on("resource_info", (info)=>{
           socketClient.emit("worker_info", info);
        });

    }
    close(){
        this.socket.close()
    }

    emit(eventName, info){
        this.member_sockets.forEach(element => element.emit(eventName, info));
    }

}

module.exports=SocketClient;