const os = require('os');
module.exports={
    Delimiter:";",
    ResourceManagerSamplingPeriod:1000,
    ResourceManagerBufferCount:60,
    Port: 17796,
    IsWindows:os.platform() === 'win32' || os.platform() === 'win64'
};