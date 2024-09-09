const express = require("express");
var router = express.Router();

router.get('/', function (req, res, next){

   res.send("Broker Device");
});

router.get('/AssignWorkerDevice', function (req, res, next){
   const workers = req.app.FogETex.Socket.fog_children;
   let candidate_worker=null;
   for (const key in workers){
      const worker = workers[key];
      if(!worker.Busy && (!candidate_worker || candidate_worker.CPU_Usage > worker.CPU_Usage)){
         candidate_worker = {IP:worker.DeviceInfo.LocalIP, CPU_Usage:worker.CPU_Usage, err: null };
      }
   }

   if(candidate_worker){
      res.json(candidate_worker)
   }else{
      res.json({IP:null, err: "Worker device cannot assigned!"})
   }
});






module.exports = router;