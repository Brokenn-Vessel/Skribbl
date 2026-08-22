const room_id = sessionStorage.getItem("room_id") ;
const myName = sessionStorage.getItem("username") ;
const uid = sessionStorage.getItem("uid") ;


// websocket server is running on port 8000 ;
console.log(room_id) 
console.log(myName) ;
console.log(uid) ;

const socket = new WebSocket(`ws://127.0.0.1:8000/ws/${room_id}?username=${myName}&uid=${uid}`) ;

socket.onopen = () => {
    console.log(`${myName} joined the room ${room_id}`) ;
    socket.send(JSON.stringify({
        type: "join",
        name: myName,
        room_id: room_id
    })) ;
} ;