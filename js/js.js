// onload?
// preventdefault?
(function() {
    var addEvent = function(elem, name, func) {
        elem.addEventListener ? elem.addEventListener(name, func) : elem.attachEvent(name, func);
    }

    var localStorageAvailable = function() {
        try {
            localStorage.setItem('k', 'v');
            localStorage.removeItem('k');
            return true;
        } catch(e) {
            return false;
        }
    };

    var show = function(elem) { elem.style.display = 'inline'; }
    var hide = function(elem) { elem.style.display = 'none'; }

    var dayOn = document.getElementById("dayOn");;
    var nightOn = document.getElementById("nightOn");
    var dayOff = document.getElementById("dayOff");
    var nightOff = document.getElementById("nightOff");

    var night = function(e) {
        var ss = document.createElement("link");
        ss.type = "text/css";
        ss.rel = "stylesheet";
        ss.href = "dark.css";
        ss.id = "darkstyle";
        document.getElementsByTagName("head")[0].appendChild(ss);
        //document.write('<link rel="stylesheet" type="text/css" href="dark.css" id="darkstyle">');
        show(nightOn);
        show(showDay);
        hide(dayOn);
        hide(showNight);
        localStorage.setItem('dayOrNight', 'night');
        if (e) { e.preventDefault() };
    };

    var day = function(e) {
        var darkstyle = document.getElementById("darkstyle");
        if (darkstyle) { darkstyle.parentNode.removeChild(darkstyle); };
        show(dayOn);
        show(showNight);
        hide(showDay);
        hide(nightOn);
        localStorage.setItem('dayOrNight', 'day');
        if (e) { e.preventDefault() };
    };

    if (localStorageAvailable()) {
        show(document.getElementById("dayNight"));
        var state = localStorage.getItem('dayOrNight');
        if (state === null || (state != 'day' && state != 'night')) {
            state = 'day';
        };
        if (state == 'day') { day(); } else { night(); };
        addEvent(showNight, 'click', night);
        addEvent(showDay, 'click', day);
    };
})();
