var os = require("os");
var config = require("./Config");
const microtime = require("microtime");
const childprocess = require("child_process")


class ResourceInfo {
    constructor(previous) {
        this.timestamp = microtime.nowDouble();
        this.cpu_times = this.cpuInfo();
        this.cpu_percentage = this.cpuPercentage(previous)
        this.freemem = os.freemem();
        this.totalmem = os.totalmem();
        this.system_uptime = os.uptime();
        this.process_uptime = process.uptime();
        this.network_stat = this.networkStats();
        this.network_bandwidth = this.bandwidth(previous)
    }

    cpuInfo() {
        var cpu = os.cpus();
        var cpuList = [];
        cpu.forEach(function (item) {
            cpuList.push(item.times);
        });
        return cpuList;
    }

    cpuPercentage(previous) {
        var total_idle = 0;
        var total_time = 0;
        var diffence = {
            total: null,
            cores: []
        };
        if (previous && previous.length != this.cpu_times.length) {
            for (var cpu in this.cpu_times) {
                var user = this.cpu_times[cpu].user - previous.cpu_times[cpu].user;
                var nice = this.cpu_times[cpu].nice - previous.cpu_times[cpu].nice;
                var sys = this.cpu_times[cpu].sys - previous.cpu_times[cpu].sys;
                var irq = this.cpu_times[cpu].irq - previous.cpu_times[cpu].irq;
                var idle = this.cpu_times[cpu].idle - previous.cpu_times[cpu].idle;
                var total = user + nice + sys + irq + idle;
                diffence.cores.push({idle: idle, total: total, usage: (1 - idle / total) * 100});
                total_idle += idle;
                total_time += total;
            }

        } else {
            for (var cpu in this.cpu_times) {
                var user = this.cpu_times[cpu].user;
                var nice = this.cpu_times[cpu].nice;
                var sys = this.cpu_times[cpu].sys;
                var irq = this.cpu_times[cpu].irq;
                var idle = this.cpu_times[cpu].idle;
                var total = user + nice + sys + irq + idle;
                diffence.cores.push({idle: idle, total: total, usage: (1 - idle / total) * 100});
                total_idle += idle;
                total_time += total;

            }
        }
        diffence.total = {idle: total_idle, total: total_time, usage: (1 - total_idle / total_time) * 100};
        //console.log("Idle: "+diffence.total.idle+ " - Total" +diffence.total.total+" - Usage:" +diffence.total.usage)

        return diffence;
    }


    networkStats() {
        if (config.IsWindows) {
            let response = childprocess.execSync('netstat -e').toString().match(/\d+/g)
            return {
                RX: {
                    Bytes: parseInt(response[0]),
                    Package: parseInt(response[2]) + parseInt(response[4])
                },
                TX: {
                    Bytes: parseInt(response[1]),
                    Package: parseInt(response[3]) + parseInt(response[5])
                }
            }
        } else {
            let response = childprocess.execSync('cat /sys/class/net/eth0/statistics/rx_bytes '
            +'&& cat /sys/class/net/eth0/statistics/rx_packets '
            +'&& cat /sys/class/net/eth0/statistics/tx_bytes '
            +'&& cat /sys/class/net/eth0/statistics/tx_packets').toString().match(/\d+/g);
            return {
                RX: {
                    Bytes: parseInt(response[0]),
                    Package: parseInt(response[1])
                },
                TX: {
                    Bytes: parseInt(response[2]),
                    Package: parseInt(response[3])
                }
            }
        }
    }

    bandwidth(previous) {
        let bw = {RX: {Bytes: 0, Package: 0}, TX: {Bytes: 0, Package: 0}}
        if (previous) {
            bw.RX.Bytes = this.network_stat.RX.Bytes - previous.network_stat.RX.Bytes;
            bw.RX.Package = this.network_stat.RX.Package - previous.network_stat.RX.Package;
            bw.TX.Bytes = this.network_stat.TX.Bytes - previous.network_stat.TX.Bytes;
            bw.TX.Package = this.network_stat.TX.Package - previous.network_stat.TX.Package;
        }
        return bw;
    }
}


class Resources {
    constructor(io) {
        this.io = io;
        this.resourcesInfos = [];
        this.previous = null;
        this.tick();
        var t = this;
        this.timer = setInterval(function () {
            t.tick()
        }, config.ResourceManagerSamplingPeriod);
    }

    tick() {
        var resourceInfo = new ResourceInfo(this.previous);
        this.previous = resourceInfo;
        this.io.SendResourceInfo(resourceInfo);
    }

}

module.exports = Resources;
