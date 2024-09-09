const express = require("express");
var createError = require('http-errors');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
const winston = require('winston');
const Config = require("../Config");
const app = express();

app.use(express.static(path.join(__dirname, 'Public')));
const env = process.env.NODE_ENV || 'development';

//Logger
let log = 'dev';
if (env !== 'development') {
    log = {
        stream: {
            write: message => winston.info(message)
        }
    }
}

app.use(logger(log));
// view engine setup
app.set('views', path.join(__dirname, 'Views'));
app.set('view engine', 'ejs');
app.set('trust proxy', true)
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());

app.use("/", require("./Routes/Home"));


//App Events
// catch 404 and forward to error handler
app.use(function(req, res, next) {
    next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
    // set locals, only providing error in development
    res.locals.message = err.message;
    res.locals.error = req.app.get('env') === 'development' ? err : {};

    // render the error page
    res.status(err.status || 500);
    //res.send(err.status)
    res.render('error');
});

app.onCloseEvent=function(){
    winston.log('Closed express server');

    /*db.pool.end(() => {
      winston.log('Shut down connection pool');
    });*/
};

module.exports = app;