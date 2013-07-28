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
    var dayNightContainer = document.getElementById("dayNight");
    var dayOn = document.getElementById("dayOn");;
    var nightOn = document.getElementById("nightOn");
    var dayOff = document.getElementById("dayOff");
    var nightOff = document.getElementById("nightOff");
    var nightTag = document.getElementsByTagName("link")[1];

    var night = function(e) {
        nightTag.disabled = false;
        show(nightOn);
        show(showDay);
        hide(dayOn);
        hide(showNight);
        localStorage.setItem('dayOrNight', 'night');
        if (e) { e.preventDefault() };
    };

    var day = function(e) {
        nightTag.disabled = true;
        show(dayOn);
        show(showNight);
        hide(showDay);
        hide(nightOn);
        localStorage.setItem('dayOrNight', 'day');
        if (e) { e.preventDefault() };
    };

    if (localStorageAvailable()) {
        show(dayNightContainer);
        var state = localStorage.getItem('dayOrNight');
        if (state === null || (state != 'day' && state != 'night')) {
            state = 'day';
        };
        if (state == 'day') {
            day();
        } else {
            night();
        };
        addEvent(showNight, 'click', night);
        addEvent(showDay, 'click', day);
    };
})();
