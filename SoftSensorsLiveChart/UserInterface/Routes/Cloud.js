const express = require("express");
const Helper = require("../../Helper");
const {response} = require("express");
var router = express.Router();

router.get('/',  (req, res, next)=>{

   res.send("Cloud Device");

});

router.get('/AssignFogNode',(req, res, next)=>{
   if(!req.query.lat || !req.query.lon){
      res.json({err: 'Missing Parameter'})
   }

   const user_lat = parseFloat(req.query.lat);
   const user_lon = parseFloat(req.query.lon);
   const user_ip  = req.ip;

   const brokers = req.app.FogETex.Socket.fog_children;
   for (const key in brokers){
      const broker = brokers[key];
      if(broker.DeviceInfo.PublicIP == user_ip && !broker.NodeBusy){
         res.json({IP: brokers[key].DeviceInfo.LocalIP,type:'LAN',distance:0, err: null });
         return;
      }
   }

   let closest_node = null
   for (const key in brokers){
      const broker= brokers[key];
      const distance = Helper.CalculateDistance(user_lat,user_lon,...broker.DeviceInfo.Location);

      if((!closest_node || closest_node.distance > distance)&& !broker.NodeBusy){
         closest_node = {IP:broker.DeviceInfo.PublicIP, type: 'WAN', distance:distance, err: null };
      }
   }

   if(closest_node){
      res.json(closest_node);
   }else{
      res.json({err: 'No connected device found!'})
   }

   //https://www.movable-type.co.uk/scripts/latlong.html
});

router.get('/GetBrokerIp',(req,res, next)=>{
   const user_ip  = req.ip;

   const brokers = req.app.FogETex.Socket.fog_children;
   for (const key in brokers){
      if(brokers[key].DeviceInfo.PublicIP == user_ip){
         res.json({LocalIP: brokers[key].DeviceInfo.LocalIP, err: null });
         return;
      }
   }
   res.json({LocalIP:null, err: "Broker device not yet connected!" })

});

module.exports = router;