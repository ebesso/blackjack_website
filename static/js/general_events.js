$(document).ready(function(){
    socket.on('error', function(data){
        var error_data = JSON.parse(data);

        alert(error_data.message);
    });

    socket.on('balance_update', function(data){
        var balance_data = JSON.parse(data);
        console.log('Received balance update');
        document.getElementById('user-balance').innerHTML = 'Balance: ' + balance_data.balance + '$';
    });
});