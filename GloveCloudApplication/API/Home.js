const express = require("express");
const Config = require("../Config");
const router = express.Router();
var pjson = require('../package.json');
const path = require('path');

router.get('/', (req, res, next) => {
    res.redirect('DeviceStatus')
})
router.get('/DeviceStatus', (req, res, next) => {
    res.json({Status: 'Running', DeviceType: "Cloud", Version: pjson.version});
});



router.get('/GetUserPackage',(req, res, next)=>{

        const file_path= path.join(__dirname,'../../'+Config.UserPackageDirectory+req.query.filename)

        res.sendFile(file_path,  function (err) {
            if (err) {
                next(err);
            } else {
                //next();
            }
        });
    }
)


module.exports = router;