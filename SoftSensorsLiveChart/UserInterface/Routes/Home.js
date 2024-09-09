const express = require("express");
const Config = require("../../Config");
const router = express.Router();
var pjson = require('../../package.json');
const path = require('path');

router.get('/', function (req, res, next) {
    const LiveChart= req.app.LiveChart;
    const FogChildren = {}
    /*for(const key in LiveChart.Socket.fog_children){
        const child = LiveChart.Socket.fog_children[key];
        FogChildren[key] = {DeviceInfo: child.DeviceInfo};

        if(child.Children){
            FogChildren[key].Children={};
            for(const key2 in child.Children){
                FogChildren[key].Children[key2]= {DeviceInfo:child.Children[key2].DeviceInfo}
            }
        }
    }*/

    res.render('index', {
        title: "FogETex",
        UserType: Config.DeviceTypes.UserInterface,
        DeviceInfo: LiveChart.DeviceInfo,
        DeviceTypes: Config.DeviceTypes,
        FogChildren: FogChildren,
        Directory: 'Home'
    })
});

router.get('/DeviceStatus', (req, res, next) => {
    res.json({Status: 'Running', DeviceType: req.app.FogETex.DeviceInfo.DeviceTypeString, Version: pjson.version});
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