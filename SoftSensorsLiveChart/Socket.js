var microtime = require('microtime')
const Config = require("./Config");
let users = {};

module.exports=function (FogEtex) {
    const io = FogEtex.Socket;
    io.users = {}
    io.ui_clients = {'Home':[]}

    io.GetCandidateUserId= function (){
        let i = 1;

        while (io.users[i.toString()]) {
            i++;
        }
        io.users[i.toString()] = true;
        return i.toString();
    }

    io.on("connection", (socket) => {
        socket.DeviceType= parseInt(socket.handshake.query.DeviceType || Config.DeviceTypes.Sensor);
        console.log(Config.DeviceTypes.GetDeviceName(socket.DeviceType)+" connected");


        if(socket.DeviceType==Config.DeviceTypes.UserInterface){
            socket.Directory = socket.handshake.query.Directory;
            socket.join('ui');
            if(!io.ui_clients[socket.Directory]){
                io.ui_clients[socket.Directory]=[]
            }
            io.ui_clients[socket.Directory].push(socket);

            /*if(socket.Directory=='Home'){
                socket.emit('bulk_data', FogEtex.ResourceManager.GetBulkData());
            }*/

            socket.on("disconnect", (reason) => {
                var ui_index = io.ui_clients[socket.Directory].indexOf(socket);
                if (ui_index !== -1) {
                    io.ui_clients[socket.Directory].splice(ui_index, 1);
                    console.log(socket.Directory + " element removed from ui clients.")
                    //Delete array if all clients is disconnected.
                    if(socket.Directory!='Home' && io.ui_clients[socket.Directory].length==0){
                        delete io.ui_clients[socket.Directory];
                    }
                }
                console.log("User Interface disconnected " + reason);
            });
        }else{
            socket.Directory = socket.handshake.query.Directory;
            socket.on("sensor", (data)=>{
                var ui_clients = io.ui_clients[socket.Directory];
                ui_clients.forEach(x=>x.emit("sensor", data))
            });
            socket.on("finger_status", (data)=>{
                var ui_clients = io.ui_clients[socket.Directory];
                ui_clients.forEach(x=>x.emit("finger_status", data))
            })
        }
    });

    io.SendAllUserInterface=function (eventName, message){
        for(const directory in io.ui_clients){
            io.ui_clients[directory].forEach(element => element.emit(eventName,message))
        }
    }
}
