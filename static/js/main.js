document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const counterDisplay = document.getElementById('counter-display');
    const incrementBtn = document.getElementById('increment-btn');
    const decrementBtn = document.getElementById('decrement-btn');

    incrementBtn.addEventListener('click', () => {
        socket.emit('increment', {name: counterName});
    });

    decrementBtn.addEventListener('click', () => {
        socket.emit('decrement', {name: counterName});
    });

    socket.on('update', data => {
        if (data.name === counterName) counterDisplay.textContent = data.value;
    });
});
