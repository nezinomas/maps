 

var map;
$(document).ready(function () {
    
    prettyPrint();

    map = new GMaps({
        div: '#map',
        zoom: 8,
        lat: 54.687157,
        lng: 25.279652,
    });
    
});
