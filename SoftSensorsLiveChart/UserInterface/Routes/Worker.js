const express = require("express");
var router = express.Router();

router.get('/', function (req, res, next){
   res.send("Worker Device");
});







module.exports = router;