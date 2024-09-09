const { Manager  } = require("socket.io-client");
const Config = require("../Config");

const manager = new Manager("ws://localhost:"+Config.Port, {
    autoConnect: true
});

const socket = manager.socket("/");

socket.on("resource_info",(info)=>{
    console.log(info);
})
