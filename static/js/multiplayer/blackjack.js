var socket;

$(document).ready(function(){

    $('#replay-button').hide()
    $('#doubledown-button').hide()

    var connection_string = 'http://' + document.getElementsByTagName('body')[0].getAttribute('data-website-domain');
    console.log('Trying to connect to ' + connection_string);

    socket = io.connect(connection_string);

    socket.on('connect', function(){
        console.log('Connected');
        socket.emit('multi_client_connect', {'identifier': getCookie('identifier')});
        socket.emit('client_balance', {'identifier': getCookie('identifier')});

        hideControlls();

    });

    socket.on('client_message', function(data){
        var message_data = JSON.parse(data);   
        alert(message_data.message);
    });
    socket.on('client_action_required', function(data){
        hideControlls()

        console.log('Received action required');
        
        var action_data = JSON.parse(data);        
        alert(action_data.message);

        if(action_data.action_required == 'bet'){
            $('#bet-controlls').show();
        }
    });

    socket.on('update_table', function(data){
        console.log(data);
    });
    
    socket.on('action_confirmed', function(){
        hideControlls();
    });

    $('#bet-submit').click(function(){
        bet_amount = $('#bet-amount').val();
        console.log(bet_amount);
        socket.emit('multi_client_action', {'action': 'bet', 'identifier': getCookie('identifier'), 'amount': bet_amount});
    });

    function hideControlls(){
        $('#bet-controlls').hide();
    }

    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
    }
});