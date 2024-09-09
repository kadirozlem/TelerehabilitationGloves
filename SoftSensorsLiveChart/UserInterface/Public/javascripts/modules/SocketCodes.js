(function (exports) {
    exports.SensorsData = function (projectId, deviceId, data = [], datetime=Date.now(),id=null) {
        this.Id=id;
        this.ProjectId = projectId;
        this.DeviceId = deviceId;
        this.DateTime=datetime;
        this.Data = data;
    };

    exports.DeviceInfo = function () {
        this.Id=null;
        this.ProjectId = 1;
        this.DeviceId=1;
        this.PortName="";
        this.SensorCount=1;
        this.RowCount=1;
        this.Frequency=50;
        this.StartRead=false;
        this.StartWrite=false;
        this.StartReplay=false;
        this.Configuration=null;
    };

    exports.Frequency= function(){
        this.Devices=[];
        this.AddDevice =function(projectId,deviceId,frequency){
            this.Devices.push({ProjectId:projectId,DeviceId:deviceId,Frequency:frequency});
        }
    };

    exports.Operations={
        DeviceStatus:1,
        ReadOperation:2,
        WriteOperation:3,
        InitialConfigurations:4,
        ReplayOperation:5
    };

    exports.DeviceStatus={
        NewDeviceFound:1,
        DeviceUnplugged:2,
        DeviceUnidentified:3,
        Error:4
    };

    exports.WROperation={
        Started:1,
        Stopped:2,
        Paused:3,
        ConfigurationChanged:4,
        Error:5
    };

    exports.OperationsInfo=function (operation,status,deviceInfo) {
        this.Operation=operation;
        this.Status=status;
        this.DeviceInfo=deviceInfo;
        this.Message="";
    };

    exports.ReadConfiguration=function(status,projectId,deviceId,readSendRatio,message){
        this.Operation=exports.Operations.ReadOperation;
        this.Status=status;
        this.ProjectId=projectId;
        this.DeviceId=deviceId;
        this.ReadSendRatio=readSendRatio;
        this.Message=message;
    };
    exports.WriteConfiguration=function(status,projectId,deviceId,message){
        this.Operation=exports.Operations.WriteOperation;
        this.Status=status;
        this.ProjectId=projectId;
        this.DeviceId=deviceId;
        this.Seperator=";";
        this.IsIdRequired=false;
        this.IsDateTimeRequired=true;
        this.FilePath="";
        this.FileName="";
        this.Message=message;
    };

    exports.InitialConfiguration=function(activeports,tempPorts,activeReplayData){
        this.Operation=exports.Operations.InitialConfigurations;
        this.ActivePorts=activeports;
        this.TempPorts=tempPorts;
        this.ActiveReplayData=activeReplayData;
    };

    exports.ReplayConfiguration=function(id, status){
        this.Operation=exports.Operations.ReplayOperation;
        this.Id=id;
        this.Status=status;
        this.StartTime=null;
        this.StopTime=null;
        this.IsCircular=true;
    };


    exports.test = function () {
        return 'This is a function from shared module';
    };

}(typeof exports === 'undefined' ? this.SocketCodes = {} : exports));