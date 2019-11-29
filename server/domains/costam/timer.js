var deadline = new Date("2020-01-10T16:00:00").getTime();
var x = setInterval(function() {
    var now = new Date().getTime();
    var t = deadline - now;
    var days = Math.floor(t / (1000 * 60 * 60 * 24));
    /*var years = 0;
    if (days > 365) { // blad roku przestepnego
        years = Math.floor(days / 365);
        days = days % 365;
    }*/
    var hours = Math.floor((t%(1000 * 60 * 60 * 24))/(1000 * 60 * 60));
    var minutes = Math.floor((t % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((t % (1000 * 60)) / 1000);
    document.getElementById("timer").innerHTML = days + " dni " // years + " lat " + 
    + hours + " godzin " + minutes + " minut " + seconds + " sekund ";
    if (t < 0) {
        clearInterval(x);
        document.getElementById("timer").innerHTML = "Startujemy !!!";
    }
}, 1000);