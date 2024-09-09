let DeviceTypes = {
    Sensor: 1,
    UserInterface: 2,
    GetDeviceName: (deviceType) => {
        switch (deviceType) {
            case DeviceTypes.Sensor:
                return 'Sensor';
            case DeviceTypes.UserInterface:
                return 'User Interface';
        }
    }
}

module.exports = {
    Delimiter: ";",
    Port: 25368,
    DeviceTypes: DeviceTypes
};