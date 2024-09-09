DeviceLists = {}

CreateCharts = function (obj) {
    //Set Chart Name
    obj.VisualType = VisualType.Chart;
    if (obj.DeviceId == 3) {
        obj.VisualType = VisualType.HeatMap;
    }


    if (obj.StartRead || obj.Id) {
        var DeviceId = obj.ProjectId + "_" + obj.DeviceId;
        if (obj.Id) {
            DeviceId = obj.Id;
        }
        var device = DeviceLists[DeviceId];
        if (!device) {
            var visualTypeGroup = null;
            if (obj.VisualType = VisualType.Chart) {
                visualTypeGroup = new ChartGroup();
            } else if (obj.VisualType = VisualType.HeatMap) {
                visualTypeGroup = new HeatMapGroup();

            }


            visualTypeGroup.Initialize(obj, DeviceId);
            DeviceLists[DeviceId] = visualTypeGroup;
        }
    }
};


SensorFilter = function () {

};


SensorsData = function () {

};

AddSensorsData = function (obj) {
    var DeviceId = obj.ProjectId + "_" + obj.DeviceId;
    if (obj.Id) {
        DeviceId = obj.Id;
        if (ReplayObjects[DeviceId]) {
            ReplayObjects[DeviceId].ChangeTime(obj.Index);
        }
    }
    var visualTypeGroup = DeviceLists[DeviceId];
    if (visualTypeGroup) {
        visualTypeGroup.AddSensorsData(obj);
    }
};

VisualType = {
    Chart: 1,
    HeatMap: 2
};

// Prototype Object
VisualTypePrototype = function () {
    this.VisualType = VisualType.Chart;
    this.AddSensorsData = function (obj) {
    };
    this.Initialize = function (obj, deviceId) {

    }
};

// Chart Object
ChartGroup = function () {
    this.chartList = [];

    this.VisualType = VisualType.Chart;

    this.AddSensorsData = function (obj) {
        var min_size = Math.min(this.chartList.length, obj.Data.length);
        for (var i = 0; i < min_size; i++) {
            this.chartList[i].SensorAdd(obj.Data[i]);
        }
    };
    this.Initialize = function (obj, deviceId) {
        for (var i = 0; i < obj.SensorCount; i++) {
            var chart = new ChartObject(deviceId + "_" + i, "Sensor " + (i + 1));
            chart.initialize();
            this.chartList.push(chart);
        }
    }
};


function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

CheckAllMoveButtons = function () {
    $('#chart_row .move_icon[disabled]').attr('disabled', false).prop('disabled', false);

    $('#chart_row .move_icon.move_left:first').attr('disabled', true).prop('disabled', true);
    $('#chart_row .move_icon.move_right:last').attr('disabled', true).prop('disabled', true);
}

ChartObjectOld = function (divId, title) {
    this.divId = divId;
    this.title = title;
    this.max_total_point = 100;
    this.linedata = [];
    this.totalPoints = this.max_total_point;
    this.y_min = 0;
    this.y_max = 100;
    this.index_value = 1;
    this.y_val_height = 20;
    this.frequency = 1;
    this.counter = 0;
    this.mod_number = 2;
    this.div_count_in_row = 3;
    this.update_y=true;

    this.initialize = function () {
        this.AddDiv();
        this.plot = this.PlotTable();

        this.opts = this.plot.getOptions();
        this.UpdateYAxis();
        this.plot.setupGrid();

        this.plot.draw();
        this.AddMoveEvents();
        this.InitJqueryEvents();
    };


    this.AddDiv = function () {
        var col_lg = 12 / this.div_count_in_row;
        var col_md = col_lg > 6 ? col_lg : 6;
        var col_sm = 12;

        var divStr = `<div class="chart_div col-lg-${col_lg} col-md-${col_md} col-sm-${col_sm}" id="${this.divId}_div">
                        <div class="card alert movable">
                            <div class="card-title">
                                <h4><i class="fa fa-area-chart"></i> <b id="sensor_name">${this.title}</b></h4>
                            </div>
                            <div class="cpu-load-chart">
                                <div id="${this.divId}" class="cpu-load"></div>
                            </div>
                            <i class="fa fa-angle-left move_icon move_left "></i>
                            <i class="fa fa-angle-right move_icon move_right"></i>
                        </div>
                        <!-- /# card -->
                    </div>`;
        $('#chart_row').append(divStr);
    };

    this.PlotTable = function () {
        return $.plot("#" + this.divId, [], {
            series: {
                shadowSize: 0 // Drawing is faster without shadows
            },
            yaxis: {
                min: this.y_min,
                max: this.y_max
            },
            xaxis: {
                show: true,
                min: this.index_value / this.frequency,
                max: (this.index_value + this.totalPoints - 1) / this.frequency
            },
            colors: [getRandomColor()],
            grid: {
                color: "transparent",
                hoverable: true,
                borderWidth: 0,
                backgroundColor: 'transparent'
            },
            tooltip: true,
            tooltipOpts: {
                content: "Y: %y",
                defaultTheme: false
            }
        });
    };

    this.SensorAdd = function (data) {
        this.plot.setData([this.AddData(data)]);

        // Since the axes don't change, we don't need to call plot.setupGrid()
        if (this.index_value > this.totalPoints) {
            this.opts.xaxes[0].min = (this.index_value - this.totalPoints + 1) / this.frequency;
            this.opts.xaxes[0].max = this.index_value / this.frequency;
        }

        if (this.counter % this.mod_number == 0) {
            this.plot.setupGrid();

            this.plot.draw();
        }
        this.counter = this.counter + 1;
    };

    this.AddBulkData = function (arr){
        arr.forEach(x => this.AddData(x));
        // Since the axes don't change, we don't need to call plot.setupGrid()
        if (this.index_value > this.totalPoints) {
            this.opts.xaxes[0].min = (this.index_value - this.totalPoints + 1) / this.frequency;
            this.opts.xaxes[0].max = this.index_value / this.frequency;
        }

        if (this.counter % this.mod_number == 0) {
            this.plot.setupGrid();

            this.plot.draw();
        }

    }

    this.AddData = function (y) {

        if (this.linedata.length >= this.totalPoints - 1)
            this.linedata.shift();

        // var prev = this.linedata.length > 0 ? this.linedata[this.linedata.length - 1][1] : 50
        // if (!prev)
        //     prev = 50

        if(this.update_y) {
            if (y < this.y_min) {
                this.y_min = y - this.y_val_height;
                this.UpdateYAxis();
            } else if (y > this.y_max) {
                this.y_max = y + this.y_val_height;

                this.UpdateYAxis();
            } else if (this.index_value % 30 == 0) {
                var temp_values = this.linedata.map(function (elt) {
                    return elt[1];
                });
                this.y_max = Math.max.apply(null, temp_values) + this.y_val_height;
                this.y_min = Math.min.apply(null, temp_values) - this.y_val_height;

                this.UpdateYAxis();
            }
        }

        this.linedata.push([this.index_value / this.frequency, y]);
        this.index_value++;
        return this.linedata;
    };
    this.UpdateYAxis = function () {
        if (this.opts.yaxes[0].min != this.y_min)
            this.opts.yaxes[0].min = this.y_min;
        if (this.opts.yaxes[0].max = this.y_max)
            this.opts.yaxes[0].max = this.y_max;
    };
    this.AddMoveEvents = function () {
        $("#" + this.divId + "_div .move_icon").click(
            function (e) {
                e.preventDefault();
                a = $(this)

                if (!$(this).prop('disabled')) {
                    var parent = $(this).closest('.chart_div'),
                        grandparent = $(this).closest('#chart_row');
                    if ($(this).hasClass('move_left')) {
                        parent.insertBefore(parent.prev('div'));
                        CheckAllMoveButtons();
                    } else if ($(this).hasClass('move_right')) {
                        parent.insertAfter(parent.next('div'));
                        CheckAllMoveButtons();
                    }
                    console.log("Worked");
                }
            }
        );
        CheckAllMoveButtons();


    }

    this.InitJqueryEvents = function () {
        $('#' + this.divId + '_div #sensor_name').editable();
    }

    this.Remove = function () {
        $('#' + this.divId + "_div").remove();
    }
};

CPUCoreObject = function (divId, index){
    this.divId=divId;
    this.index = index
    this.circleId ="cpu_core_"+this.index;
   this.initialize=function (){
       const divStr = `<div class="col-md-2">
                                <div class="card text-center">
                                    <div class="m-t-10">
                                        <h4 class="card-title"><i class="fa-solid fa-microchip"></i>  Core ${this.index}</h4>
                                    </div>
                                    <div class="widget-card-circle pr m-t-20 m-b-20" id="${this.circleId}">
                                        <i class="pa">0%</i>
                                    </div>
                                </div>
                            </div>`;

       $('#'+this.divId).append(divStr);
       this.CircleProgress();
    }

    this.CircleProgress=function (color="#a389d5",size=100){
        $('#'+this.circleId).circleProgress({
            value: 0.70,
            size: 100,
            fill: {
                gradient: ["#a389d5"]
            }
        });
    }
    this.Change=function (value){
        $('#'+this.circleId).circleProgress({value:value,animationStartValue:$('#'+this.circleId).circleProgress('value')})
        $('#'+this.circleId +' i').html(parseInt(100*value)+'%')
    }

}

SSLCustomColor = function (hex_color) {
    this.hex_color = hex_color;

    this.Initialize = function () {
        this.SetColor();
    };

    this.SetColor = function () {
        this.red = parseInt(this.hex_color.substr(1, 2), 16);
        this.green = parseInt(this.hex_color.substr(3, 2), 16);
        this.blue = parseInt(this.hex_color.substr(5, 2), 16);
    };

    this.Initialize();
};

SSLHeatMapColors = function (start_color, end_color) {
    this.start_color = new SSLCustomColor(start_color);
    this.end_color = new SSLCustomColor(end_color);

    this.GetColor = function (normalized_val) {
        if (normalized_val < 0 || normalized_val > 1) {
            return "#FFFFFF";
        }

        var red = this.GetScaledHexValue(normalized_val, this.start_color.red, this.end_color.red);
        var green = this.GetScaledHexValue(normalized_val, this.start_color.green, this.end_color.green);
        var blue = this.GetScaledHexValue(normalized_val, this.start_color.blue, this.end_color.blue);
        return "#" + red + green + blue;
    }

    this.GetScaledHexValue = function (normalized_val, start_val, end_val) {
        var hex_val = Math.floor((end_val - start_val) * normalized_val + start_val).toString(16).toUpperCase();
        if (hex_val.length == 1) {
            hex_val = "0" + hex_val;
        }
        return hex_val;
    }

}

HeatMap=function(container, row_count, column_count, colors){
    this.container=container;
    this.row_count=row_count;
    this.column_count=column_count;
    this.colors=colors;
    this.title="Heat Map";
    this.title_row=null;
    this.cells = [];

    this.AddSensorsData=function (data) {
        var arr_size = Math.min(data.length, this.cells.length);
        for (var i = 0; i < arr_size; i++) {
            this.cells[i].css("background-color", this.colors.GetColor(data[i]));
        }
    };

    this.Initialize = function (obj, deviceId) {
        this.divId = "hm_" + deviceId;
        this.title = "Pressure Mat";
        this.AddDiv();
    };

    this.AddDiv=function () {
        this.row=row= $(`<div class="col-xl-4 col-lg-6 col-md-12"></div>`);

        // var div_line = `<div id="${this.divId + "_line_legend"}" style="max-width: ${150 * this.column_count}px; width: 100%;text-align: center;margin-bottom: 10px;">

        var div_line = `<div id="${this.divId + "_line_legend"}" style="width: 100%;text-align: center;margin-bottom: 10px;">
                            <div style="display: inline-flex">
                                <div class="hm_legend">0%</div>
                                <div class="hm_legend">20%</div>
                                <div class="hm_legend">40%</div>
                                <div class="hm_legend">60%</div>
                                <div class="hm_legend">80%</div>
                               <div class="hm_legend">100%</div>
                           </div>
                       </div>`;
        row.append(div_line);
        var cell_width = Math.floor((100 / this.column_count) * 100) / 100;
        var count = 0;
        for (var i = 0; i < this.row_count; i++) {
            var div_line = $(`<div id="${this.divId + "_line_" + (i + 1)}" class="mat_line" ></div>`);
            row.append(div_line);
            //var div_line_cont = $("#" + this.divId + "_div #" + this.divId + "_line_" + (i + 1));
            for (var j = 0; j < this.column_count; j++) {
                count++;
                var div_square = $(`<div class="square" id="${this.divId + "_" + count}" style="width: ${cell_width}%"> </div>`);
                div_line.append(div_square);
                this.cells.push(div_square);
            }
        }
        this.title_row = $(`<div id="${this.divId + "_line_title"}" class="hm_title">${this.title}</div>`);
        row.append(this.title_row);
        this.container.append(row);
        this.UpdateLegendColor(row);

    };

    this.SetTitle=function (title) {
        this.title=title;
        this.title_row.html(title);
    };

    this.Remove=function () {
        this.row.remove();
    };

    this.UpdateLegendColor = function (row) {
       // var legend_divs = $("#" + this.divId + "_line_legend .hm_legend");
        var legend_divs = row.find('.hm_legend');
        var iteration_count = Math.min(legend_divs.length, 5);
        for (var i = 0; i <= iteration_count; i++) {
            $(legend_divs[i]).css("background-color", this.colors.GetColor(i * 0.2));
        }
    };

};


//Heat Map Group
HeatMapGroup = function (row_count, column_count) {
    this.VisualType = VisualType.HeatMap;
    this.colors = new SSLHeatMapColors("#fe0000", "#0a0000");
    this.row_count = row_count;
    this.column_count = column_count;
    this.cell_count=row_count*column_count;
    this.heatmaps = [];
    this.cells_min_val = [];
    this.cells_max_val = [];
    this.calibration_count = 20;
    this.CalibrationActive = true;
    this.CalibrationMax = false;
    this.MinMaxDifferenceValue = 5;
    this.AddSensorsData = function (obj) {
        var data = obj.Data;
        var arr_size = Math.min(data.length, this.heatmaps.length);
        for (var i = 0; i < arr_size; i++) {
            this.heatmaps[i].AddSensorsData(data[i]);
        }
    };

    this.AddSensorsDataWithCalib = function (obj) {
        var data = obj.Data;
        if (this.CalibrationActive) {
            this.Calibration(data);
        }
        var normalized_data = this.calculateNormalizedValues(data);
        var arr_size = Math.min(normalized_data.length, this.cells.length);
        for (var i = 0; i < arr_size; i++) {
            this.cells[i].css("background-color", this.colors.GetColor(normalized_data[i]));
        }
        console.log("Updated." + arr_size);
    };

    this.Initialize = function (obj, deviceId) {
        this.divId = "hm_" + deviceId;
        this.title = "Pressure Mat";
        this.AddDiv();
    };

    this.AddDiv = function () {
        var divStr = `<div class="heatmap_div col-lg-12 col-md-12 col-sm-12" id="${this.divId}_div">
                        <div class="card alert movable">
                            <div class="card-title">
                                <h4><i class="fa fa-table"></i> <b id="sensor_name">${this.title}</b></h4>
                            </div>
                            <div class="cpu-load-chart row" id="${this.divId}">
                                
                            </div>
                            <i class="fa fa-angle-left move_icon move_left "></i>
                            <i class="fa fa-angle-right move_icon move_right"></i>
                        </div>
                        <!-- /# card -->
                    </div>`;
        $('#chart_row').append(divStr);
        this.container = $("#" + this.divId + "_div #" + this.divId);
        //Legend
        this.heatmaps.push(new HeatMap(this.container,this.row_count,this.column_count,this.colors));
        this.heatmaps[this.heatmaps.length-1].Initialize();
    };

    this.SetTitles=function(titles){
        for(var i=0; i<titles.length;i++){
            if(i>this.heatmaps.length-1) {
                this.heatmaps.push(new HeatMap(this.container, this.row_count, this.column_count, this.colors));
                this.heatmaps[i].Initialize();
            }
            this.heatmaps[i].SetTitle(titles[i]);
        }
    };

    this.SetMapCount=function (count) {
        if(count<this.heatmaps.length){
            while(this.heatmaps.length>count){
                var mat=this.heatmaps.pop();
                mat.Remove();
            }
        }else {
            for (var i = this.heatmaps.length; i < count; i++) {
                this.heatmaps.push(new HeatMap(this.container, this.row_count, this.column_count, this.colors));
                this.heatmaps[i].Initialize();
            }
        }
    };

    this.calculateNormalizedValues = function (arr) {
        var arr_size = Math.min(arr.length, this.cells_max_val.length, this.cells_min_val.length);
        var nvList = [];
        for (var i = 0; i < arr_size; i++) {
            var value = (arr[i] - this.cells_min_val[i]) / (this.cells_max_val[i] - this.cells_min_val[i]);
            value = value > 1 ? 1 : (value < 0 ? 0 : value);
            nvList.push(value);
        }
        return nvList;
    };


    this.InitMinMaxArray = function (data) {
        for (var i = 0; i < data.length; i++) {
            this.cells_min_val.push(data[i]);
            this.cells_max_val.push(data[i] + this.MinMaxDifferenceValue);
        }
    }
    this.Calibration = function (data) {
        this.calibration_count--;
        this.CalibrationActive = this.calibration_count > 0;
        if (this.cells_min_val.length == 0) {
            this.InitMinMaxArray(data);
        }
        var arr_size = Math.min(data.length, this.cells_max_val, this.cells_min_val);

        for (var i = 0; i < arr_size; i++) {
            if (this.cells_min_val[i] > data[i]) {
                this.cells_min_val[i] = data[i];
                if (!this.CalibrationMax) {
                    this.cells_max_val = data[i] + this.MinMaxDifferenceValue;
                }

                if (this.CalibrationMax && this.cells_max_val[i] < data[i]) {
                    this.cells_max_val[i] = data[i];
                }
            }
        }

    };

    this.Remove = function () {
        $('#' + this.divId + "_div").remove();
    };
};

var test_arr = [
    [0.1, 0.0, 0.1, 0.1, 0.1, 0.2, 0.0, 0.0, 0.0],
    [0.2, 0.0, 0.1, 0.2, 0.1, 0.2, 0.0, 0.0, 0.0],
    [0.3, 0.0, 0.1, 0.1, 0.1, 0.2, 0.0, 0.0, 0.0],
    [0.4, 0.0, 0.1, 0.2, 0.1, 0.2, 0.0, 0.0, 0.0],
    [0.5, 0.0, 0.1, 0.1, 0.1, 0.2, 0.0, 0.0, 0.0],
    [0.6, 0.0, 0.1, 0.2, 0.1, 0.2, 0.0, 0.0, 0.0],
    [0.7, 0.0, 0.1, 0.1, 0.1, 0.2, 0.0, 0.0, 0.0],
    [0.8, 0.0, 0.1, 0.2, 0.1, 0.2, 0.0, 0.0, 0.0],
    [0.9, 0.0, 0.1, 0.1, 0.1, 0.2, 0.0, 0.0, 0.0],
    [0.8, 0.0, 0.1, 0.1, 0.1, 0.2, 0.0, 0.0, 0.0],
    [0.7, 0.0, 0.1, 0.1, 0.1, 0.2, 0.0, 0.0, 0.0],
    [0.6, 0.0, 0.1, 0.2, 0.1, 0.2, 0.0, 0.0, 0.0],
    [0.5, 0.0, 0.1, 0.1, 0.1, 0.2, 0.0, 0.0, 0.0],


]
var IntervalObj = null;
var index = 0;
var exampleHeatMat = null;

var IntervalObj2 = null;
var index2 = 0;
var exampleHeatMat2 = null;
var max_count=1000;
TestInterval = function () {
    index++;
    if (index < test_arr.length) {
        exampleHeatMat.AddSensorsData({Data: [test_arr[index]]});
    } else {
        console.log("Bitti");
        clearInterval(IntervalObj);
    }
}

HeatMapTest = function () {
    exampleHeatMat = new HeatMapGroup(5, 5);
    exampleHeatMat.Initialize(null,"kadir");
    exampleHeatMat.AddSensorsData({Data: test_arr[index]});
    IntervalObj = setInterval(TestInterval, 1000);
};

GenerateNumbers=function(arr_count){
    var l=[];
    for(var i=0;i<arr_count;i++){
        l.push(Math.random());
    }
    return l;
};

TestInterval2 = function () {
    if (index2 < max_count) {
        var l=[];
        for(var i=0; i<exampleHeatMat2.heatmaps.length;i++){
            l.push(GenerateNumbers(exampleHeatMat2.cell_count));
        }
        exampleHeatMat2.AddSensorsData({Data: l});
    } else {
        console.log("Bitti");
        clearInterval(IntervalObj2);
    }
    index2++;
};

HeatMapTest2 = function (row, column,mat_count,interval=1000,l_max_count=1000) {
    max_count=l_max_count;
    exampleHeatMat2 = new HeatMapGroup(row, column);
    exampleHeatMat2.Initialize(null,"kadir");
    exampleHeatMat2.SetMapCount(mat_count);
    exampleHeatMat2.AddSensorsData({Data: test_arr[index]});
    IntervalObj2 = setInterval(TestInterval2, interval);
};


InsertRandomData=function(index, count){

}


$.fn.editable.defaults.mode = 'inline';
$.fn.editable.defaults.disabled = true;

// SocketControlMessage=function(data){
//
// };



