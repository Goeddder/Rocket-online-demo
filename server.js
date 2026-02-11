const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

let gameState = "WAIT"; 
let timer = 5; 
let multiplier = 1.0;
let crashAt = 0;
let bets = [];

function generateCrash() {
    let rnd = Math.random();
    if (rnd < 0.1) return 1.00;
    if (rnd < 0.7) return (Math.random() * 1.7 + 1.01);
    return (Math.random() * 5 + 2.71);
}

setInterval(() => {
    if (gameState === "WAIT") {
        timer -= 0.1;
        if (timer <= 0) {
            gameState = "FLY";
            multiplier = 1.0;
            crashAt = generateCrash();
        }
    } else if (gameState === "FLY") {
        multiplier += 0.005 * Math.sqrt(multiplier);
        if (multiplier >= crashAt) {
            gameState = "CRASH";
            setTimeout(() => {
                gameState = "WAIT";
                timer = 5;
                multiplier = 1.0;
                bets = [];
            }, 3000);
        }
    }
    io.emit('gameTick', { gameState, multiplier: multiplier.toFixed(2), timer: Math.ceil(timer), bets });
}, 100);

io.on('connection', (socket) => {
    socket.on('placeBet', (data) => {
        if (gameState === "WAIT") {
            bets.push({ user: data.user, amount: data.amount, status: "FLYING" });
            io.emit('updateBets', bets);
        }
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log('Server started on port ' + PORT));
