var socket;

$(document).ready(function(){

    $('#replay-button').hide()
    $('#doubledown-button').hide()

    var connection_string = 'http://' + document.getElementsByTagName('body')[0].getAttribute('data-website-domain');
    console.log('Trying to connect to ' + connection_string);

    socket = io.connect(connection_string);

    socket.on('connect', function(){
        console.log('Connected');
        socket.emit('single_client_connected', {'identifier': getCookie('identifier')});
        socket.emit('client_balance', {'identifier': getCookie('identifier')});

    });

    socket.on('update_table', function(data){
        socket.emit('client_balance', {'identifier': getCookie('identifier')});

        console.log('Updating table...');

        var table_data = JSON.parse(data);

        document.getElementById('player-hand').innerHTML = '';
        document.getElementById('cpu-hand').innerHTML = '';

        console.log(table_data.doubledown)

        if (table_data.doubledown == true){
            console.log('doubledown valid');
            $('#doubledown-button').show();
        }
        else{
            console.log('doubledown invalid');
            $('#doubledown-button').hide();
        }

        for(var i = 0; i < table_data.player_cards.length; i++){
            displayCard(table_data.player_cards[i].image, "player-hand");
        }
        for(var i = 0; i < table_data.cpu_cards.length; i++){
            displayCard(table_data.cpu_cards[i].image, "cpu-hand");
        }
        document.getElementById('current-bet').innerHTML = 'Current bet ' + table_data.bet + '$';
        
        console.log('Updated table');
    });

    socket.on('game_finished', function(data){
        socket.emit('client_balance', {'identifier': getCookie('identifier')});

        var game_data = JSON.parse(data);
        
        document.getElementById('player-hand').innerHTML = ''
        document.getElementById('cpu-hand').innerHTML = ''


        for(var i = 0; i < game_data.player_cards.length; i++){
            displayCard(game_data.player_cards[i].image, "player-hand");
        }
        for(var i = 0; i < game_data.cpu_cards.length; i++){
            displayCard(game_data.cpu_cards[i].image, "cpu-hand");
        }

        for (let el of document.querySelectorAll('.play-button')) el.style.visibility = 'hidden';
        $('#replay-button').show()
        

        document.getElementById('result-label').innerHTML = game_data.result;
    });

    $('#hit-button').click(function(){
        socket.emit('single_client_hit', {'identifier': getCookie('identifier')});
    });
    $('#stand-button').click(function(){
        socket.emit('single_client_stand', {'identifier': getCookie('identifier')});
    });
    $('#doubledown-button').click(function(){
        socket.emit('single_client_doubledown', {'identifier': getCookie('identifier')});
    });

    $('#replay-button').click(function(){
        window.location.reload();
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