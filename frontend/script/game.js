const room_id = sessionStorage.getItem("room_id") ;
const myName = sessionStorage.getItem("username") ;
const uid = sessionStorage.getItem("uid") ;
const playerSection = document.querySelector('.player-section')


// websocket server is running on port 8000 ;
console.log(room_id) 
console.log(myName) ;
console.log(uid) ;

const socket = new WebSocket(`ws://127.0.0.1:8000/ws/${room_id}?username=${myName}&uid=${uid}`) ;

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
}