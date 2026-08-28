const room_id = sessionStorage.getItem("room_id") ;
const myName = sessionStorage.getItem("username") ;
const uid = sessionStorage.getItem("uid") ;
const playerSection = document.querySelector('.player-section') ;
const chatbox = document.querySelector('.chatbox') ;

const inputBox = document.querySelector('.chat-input') ;
const sendBtn = document.querySelector('.send') ;


// websocket server is running on port 8000 ;
console.log(room_id) 
console.log(myName) ;
console.log(uid) ;

const socket = new WebSocket(`ws://127.0.0.1:8000/ws/${room_id}?username=${myName}&uid=${uid}`) ;

function socketSend(message) {
    socket.send(JSON.stringify(message)) ;
}

// Send chat message
function sendMessage(event) {
    const msg = inputBox.value
    console.log(msg) ;
    inputBox.value = "" ;

    if(msg != "") {
        socketSend({
            type: "guess",
            message: msg,
            sender_name: myName,
            sender_id: uid
        }) ;
    }
}


sendBtn.addEventListener('click', sendMessage) ;
socket.onopen = () => {
    console.log(`${myName} joined the room ${room_id}`) ;
} ;

socket.onmessage = (event) => {
    message = JSON.parse(event.data) 
    console.log(message)

    if(message.type == "join" || message.type == "leave") {
        playerSection.innerHTML = "" ;
        message.players.forEach(p => {
            const player = document.createElement('div') ;
            const player_name = document.createElement('div') ;
            const player_score = document.createElement('div') ;
        
            player.classList.add('player') ;
            player_name.classList.add('player-name') ;
            player_score.classList.add('player-score') ;
        
            player_name.textContent = `${p.username}` ;
            player_score.textContent = "0" ;
        
            player.appendChild(player_name) ;
            player.appendChild(player_score) ;
        
            playerSection.append(player) ;
        });
    }

    if(message.type == "guess") {   
        console.log(`${message.sender_name}: ${message.message}`) ;

        const msg = document.createElement('div') ;
        if(message.sender_id == uid) {
            msg.classList.add('message-self') ;
        }
        else {
            msg.classList.add('message-other') ;
        }

        const senderName = document.createElement('span') ;
        senderName.classList.add('message-username') ;

        const msgText = document.createElement('span') ;
        msgText.classList.add('message-text') ;

        if(message.sender_id != uid) {
            senderName.innerText = `${message.sender_name}:` ;
            msg.appendChild(senderName) ;
        } 
        msgText.innerText = `${message.message}` ;
        msg.appendChild(msgText) ;

        chatbox.appendChild(msg) ;
    }
}



