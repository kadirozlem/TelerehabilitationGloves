var DeviceTypes = {
    User: 0,
    Cloud: 1,
    UserInterface: 2,
    ProcessMaster: 3,
    Patient:4,
    GetDeviceName: (deviceType) => {
        switch (deviceType) {
            case DeviceTypes.User:
                return 'User';
            case DeviceTypes.Cloud:
                return 'Cloud';
            case DeviceTypes.UserInterface:
                return 'User Interface';
            case DeviceTypes.ProcessMaster:
                return 'Process Master';
            case DeviceTypes.Patient:
                return 'Patient';
        }
    }
}

module.exports = {
    Delimiter: ";",
    Port: 27592,
    UserPackageDirectory: "./UserPackage/",
    DeviceType: DeviceTypes.Cloud,
    DeviceTypes: DeviceTypes
};
