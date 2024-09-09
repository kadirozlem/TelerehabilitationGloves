PNotify.defaults.styling = 'bootstrap4';
PNotify.defaults.modules = {
    Animate: {
        animate: true,
        inClass: 'zoomInLeft',
        outClass: 'zoomOutRight'
    }
};

function errorNotify(message, title='Error!') {
    new PNotify.error({
        title,
        text: message,
        delay: 3000
    });
}

function infoNotify(message,title='Info!') {
    new PNotify.info({
        title,
        text: message,
        delay: 3000
    });
}

function successNotify(message,title='Success!') {
    new PNotify.success({
        title,
        text: message,
        delay: 3000
    });
}


function warningNotify(message,title="Warning!") {
    new PNotify.notice({
        title,
        text: message,
        delay: 3000
    });
}

var intTo2DigitString = function (number) {
    if (number < 10) {
        return '0' + number;
    }
    return number;
};

function hideLoading() {
    $("#loadingDiv").hide();
}

function showLoading() {
    $("#loadingDiv").show();
}

Array.prototype.findElementById = function (Id) {
    var result = $.grep(this, function (e) {
        return e.Id === Id;
    });
    if (result.length === 0) {
        return null;
    } else {
        return result[0];
    }
};
Array.prototype.removeElementById = function (Id) {
    var element = this.findElementById(Id);
    if (element !== null) {
        var index = this.indexOf(element);
        this.splice(index, 1);
    }

};
$.fn.serializeObject = function () {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function () {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

$(document).ajaxError(function (response) {
    new PNotify.error({
        title: 'Connection Error!',
        text: 'An error occurred! Please, check your internet connection.',
    });
    hideLoading();
});


function disableEditable() {
    $('.EditableEnableBtn').html('Enable');
    $('.EditableEnableBtn').data('disabled', true);
    $('.editable').editable('option', 'disabled', true);
}

function enableEditable() {
    $('.EditableEnableBtn').html('Disable');
    $('.EditableEnableBtn').data('disabled', false);
    $('.editable').editable('option', 'disabled', false);
}



Object.defineProperty(String.prototype, "id", {
    get: function () {
        return '#' + this;
    }
});
Object.defineProperty(String.prototype, "class", {
    get: function () {
        return '.' + this;
    }
});

function AtLeast2Digit(value){
    if(value<10){
        return "0"+value;
    }
    return value;
}
function SecondToTime(value){
    value = parseInt(value);
    const second = value%60;
    const minute = parseInt(value%3600 /60);
    const hour = parseInt(value/3600);
    return AtLeast2Digit(hour)+":"+AtLeast2Digit(minute)+':'+AtLeast2Digit(second);
}

function ChangeProgressBar(search,value){
    const new_value = parseInt(value*100);
    $(search).css('width', new_value+'%');
}