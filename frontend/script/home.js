const usernameInput = document.querySelector('.username-input');
const roomIdInput = document.querySelector('.room-id-input') ;
const joinBtn = document.querySelector('.join-room') ;
const createBtn = document.querySelector('.create-room') ;

createBtn.addEventListener('click', async () => {
    const name = usernameInput.value ;
    usernameInput.value = "" ;
    roomIdInput.value = "" ;

    const response = await fetch(`http://127.0.0.1:8000/app/get_room?username=${name}`) ;
    const msg = await response.json() ;

    sessionStorage.setItem("room_id", msg.room_id) ;
    sessionStorage.setItem("username", msg.owner) ;

    // get a unique identification id for the game
    const uid_response = await fetch(`http://127.0.0.1:8000/app/get_uid?username=${name}`) ;
    const uid_msg= await uid_response.json() ;
    sessionStorage.setItem("uid", uid_msg.uid) ;

    // redirect the user to this page 
    window.location.href = "./game.html" ; 
}) ;

joinBtn.addEventListener('click', async () => {
    const name = usernameInput.value ;
    const room_id = roomIdInput.value ;

    usernameInput.value = "" ;
    roomIdInput.value = "" ;

    sessionStorage.setItem("room_id", room_id) ;
    sessionStorage.setItem("username", name) ;

    // get a unique identification id for the game
    const uid_response = await fetch(`http://127.0.0.1:8000/app/get_uid?username=${name}`) ;
    const uid_msg= await uid_response.json() ;
    sessionStorage.setItem("uid", uid_msg.uid) ;

    window.location.href = "./game.html" ;
}) ;