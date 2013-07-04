var night = function() {  // make it dark
    document.write('<link rel="stylesheet" type="text/css" href="dark.css">');
};

var localStorageAvailable = function() {  // thanks modernizr
    try {
        localStorage.setItem('k', 'v');
        localStorage.removeItem('k');
        return true;
    } catch(e) {
        return false;
    }
};

if (localStorageAvailable()) {
    // figure out current state, defaulting to 'day'
    var state = localStorage.getItem('dayOrNight');
    if (state === null || (state != 'day' && state != 'night')) {
        state = 'day';
    }
    // show appropriate toggle
    // attach handlers
    night();
};

