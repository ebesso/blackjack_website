$(document).ready(function(){

    var connection_string = document.getElementsByTagName('body')[0].getAttribute('id');
    console.log('Trying to connect to ' + connection_string);

    var socket = io.connect(connection_string);

    socket.on('connect', function(){
        console.log('Connected');
        socket.emit('client_connected', {'identifier': getCookie('identifier')});
    });

    socket.on('update_table', function(data){
        console.log('Updating table...');

        var table_data = JSON.parse(data);

        document.getElementById('player-hand').innerHTML = ''
        document.getElementById('cpu-hand').innerHTML = ''


        for(var i = 0; i < table_data.player_cards.length; i++){
            displayCard(table_data.player_cards[i].image, "player-hand");
        }
        for(var i = 0; i < table_data.cpu_cards.length; i++){
            displayCard(table_data.cpu_cards[i].image, "cpu-hand");
        }

        console.log('Updated table');
    });

    $('#hit-button').click(function(){
        socket.emit('client_hit', {'identifier': getCookie('identifier')});
    });

    function displayCard(image_src, hand){
        var img = document.createElement("img");

        img.src = "../static/images/cards/" + image_src + ".png";

        document.getElementById(hand).appendChild(img);
    }

    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
    }

});