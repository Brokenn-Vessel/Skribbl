const room_id = sessionStorage.getItem("room_id") ;
const myName = sessionStorage.getItem("username") ;

// websocket server is running on port 8000 ;
const socket = new WebSocket(`ws://127.0.0.1:8000/ws/${room_id}`) ;

socket.onopen = () => {
    console.log("connected!") ;
    socket.send(JSON.stringify({
        type: "join",
        name: myName,
        room_id: room_id
    })) ;
} ;