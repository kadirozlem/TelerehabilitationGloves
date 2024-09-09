var microtime = require('microtime')
const Config = require("./Config");
const Helper = require("./Helper");

module.exports=function (FogEtex) {
    const io = FogEtex.Socket;
    io.users = {}
    io.user_token={}
    io.process_master = null;
    io.users_package = {}
    io.users_package_buffer={}

    io.GetCandidateUserId= function (){
        let i = 1;

        while (io.users[i.toString()]) {
            i++;
        }
        io.users[i.toString()] = true;
        return i.toString();
    }

    io.UserDisconnected=function (userId, token){
        if(userId != null){
            let obj = io.users[userId];
            if(obj){
                obj.User = null;
                if(obj.User == null){
                    delete io.users[userId];
                }
            }
        }

        if(token != null){
            let obj = io.users[userId];
            if(obj){
                if(userId == null){
                    obj.Patient=null;
                }
                if(obj.User == null && obj.Patient==null){
                    delete io.user_token[token];
                }
            }
        }
    }

    io.CreateTherapyObj=function (userId, token){
        let obj =null;
        if(io.user_token[token]){
            obj=io.user_token[token]

        }else {
            io.user_token[token] =obj = {User: null, Patient: null, token: token}
        }
        if(userId!=null){
            io.users[userId]=obj;
        }
        return obj;
    }

    io.on("connection", (socket) => {
        socket.DeviceType= parseInt(socket.handshake.query.DeviceType || Config.DeviceTypes.User);
        console.log(Config.DeviceTypes.GetDeviceName(socket.DeviceType)+" connected");


        if(socket.DeviceType === Config.DeviceTypes.ProcessMaster){
            io.process_master = socket;

            socket.on("disconnect", (reason) => {
                console.log("Process master disconnected " + reason);
                for(var key in io.users ){
                    io.users[key].emit("application_disconnected", true);
                }
                io.process_master = null;
            });

            //msg -> userid;status -> 12|1  or 12|1;AppNotCreate
            socket.on("process_ready", (msg) => {
                const [userId, status_msg] =msg.split("|");
                if (!io.users[userId]) {
                    console.log('User not found: ' + userId)
                    return
                }

                io.users[userId].User.emit("process_ready", status_msg)
            });
            //req: msg -> 'userId|socket_received|data_index;result;added_queue;process_started;process_finished'
            //response -> 'data_index;result;added_queue;process_started;process_finished;response_time'
            socket.on("result", (msg) => {
                const result_received_socket = microtime.nowDouble();
                const [userId, socket_received, result]=msg.split("|");
                if (!io.users[userId]) {
                    //console.log(obj.username+'User not found!')
                    return
                }

                const response_time = result_received_socket - parseFloat(socket_received);
                const response = result+";"+response_time;


                io.users[userId].Patient.emit("result", response);

                if (!io.users_package[userId]) {
                    io.users_package[userId] = {request: 0, response: 1}
                } else {
                    io.users_package[userId].response++;
                }
            });

        }

        if(socket.DeviceType===Config.DeviceTypes.User){
            //If client is User, get small id to decrease communication message
            socket.userId = io.GetCandidateUserId();
            socket.Token=null;
            socket.on("disconnect", (reason) => {
                console.log("User disconnected " + reason)

                if (io.users[socket.userId]) {
                    if (io.process_master) {
                        io.process_master.emit("user_disconnected", socket.userId)
                    }
                    io.UserDisconnected(socket.userId, socket.Token);
                }
            });
            //msg -> dataIndex|data -> 1|123;1
            socket.on("sensor_data", (msg) => {
                const socket_received = microtime.nowDouble();
                const message = `${socket.userId}|${msg}|${socket_received}`;
                io.process_master.emit("sensor_data", message);
                if (!io.users_package[socket.userId]) {
                    io.users_package[socket.userId] = {request: 1, response: 0}
                } else {
                    io.users_package[socket.userId].request++;
                }
            });

            socket.on("request_info", (msg)=>{
                if(socket.Therapy){
                    if(socket.Therapy.Patient){
                        socket.Therapy.Patient.emit("request_info", msg)
                    }
                }
            });

            //user_index -> 1  #Created by user
            //response -> false|msg   or true
            socket.on("app_info", (user_index, model_name, token) => {
                socket.Therapy= io.CreateTherapyObj(socket.userId, token);
                socket.Therapy.User = socket
                socket.user_index = user_index;
                if (io.process_master) {
                    io.process_master.emit("new_user", socket.userId+"|"+socket.id+"|"+model_name);
                } else {
                    socket.emit("process_ready", "0;Master is not ready");
                }

                socket.FileName =  socket.user_index+'_'+Helper.DateTimeAsFilename()+'_'+socket.id+".json";
                socket.emit('filename', socket.FileName);
            });
        }

        if(socket.DeviceType===Config.DeviceTypes.Patient){
            //If client is User, get small id to decrease communication message

            socket.on("disconnect", (reason) => {
                console.log("User disconnected " + reason)

                if (io.users[socket.userId]) {
                    if (io.process_master) {
                        io.process_master.emit("user_disconnected", socket.id)
                    }
                    delete io.users[socket.userId]
                }
            });

            //user_index -> 1  #Created by user
            //response -> false|msg   or true
            socket.on("app_info", (token) => {
                socket.Therapy= io.CreateTherapyObj(null, token);
                socket.Therapy.Patient=socket;
                if (!io.process_master) {
                    socket.emit("process_ready", "0;Master is not ready");
                }
            });
        }
    });


}
