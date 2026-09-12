const room_id = sessionStorage.getItem("room_id") ;
const myName = sessionStorage.getItem("username") ;
let isOwner = false ; 
let ownerDone = false ;
const uid = sessionStorage.getItem("uid") ;
const playerSection = document.querySelector('.player-section') ;
const chatbox = document.querySelector('.chatbox') ;

const inputBox = document.querySelector('.chat-input') ;
const sendBtn = document.querySelector('.send') ;
const drawingSectionTop = document.querySelector('.drawing-section-top') ;
const drawingCanvas = document.querySelector('.drawing-canvas') ;
const canvas = document.querySelector('.canvas') ;
const ctx = canvas.getContext("2d") ;
const boundingRect = canvas.getBoundingClientRect() ;

let isDrawing = false ;
let isDrawing_socket = false ;
let brushColor = "black" ;
let brushWidth = 10 ;

function getCoords(e) {
    const scaleX = canvas.width / boundingRect.width ;
    const scaleY = canvas.height / boundingRect.height ;
    return {
        x: (e.clientX - boundingRect.left) * scaleX ,
        y: (e.clientY - boundingRect.top) * scaleY
    } ;
}

// websocket server is running on port 8000 ;
console.log(room_id) ;
console.log(myName) ;
console.log(uid) ;

function startDrawing(e) {
    isDrawing = true ;
    const pos = getCoords(e) ;
    ctx.beginPath() ;

    ctx.strokeStyle = brushColor ;
    ctx.lineWidth = brushWidth ;
    ctx.lineCap = "round" ;
    ctx.moveTo(pos.x, pos.y) ;
}


function contDrawing(e) {
    if(!isDrawing) return ;
    const pos = getCoords(e) ;
    ctx.lineTo(pos.x, pos.y) ;
    ctx.stroke() ;
}

function endDrawing(e) {
    isDrawing = false ;
}

canvas.addEventListener("mousedown", (e)=>{
    // startDrawing(e) ;
    isDrawing_socket = true ;
    const pos = getCoords(e) ;
    socketSend({
        type: "draw-begin", 
        clientX: e.clientX,
        clientY: e.clientY,
        uid: uid
    }) ;
}) ;

canvas.addEventListener("mousemove", (e)=>{
    // contDrawing(e) ;
    if(!isDrawing_socket) return ;
    const pos = getCoords(e) ;
    socketSend({
        type: "draw-cont",
        clientX: e.clientX,
        clientY: e.clientY,
        uid: uid
    }) ;
}) ;

window.addEventListener("mouseup", (e)=>{
    // endDrawing(e) ;
    isDrawing_socket = false ;
    socketSend({
        type: "draw-end",
        clientX: e.clientX,
        clientY: e.clientY,
        uid: uid
    }) ;
}) ;

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


function createBlocker(message) {
    const blocker = document.createElement('div') ;
    blocker.classList.add('game-blocker') ;

    const prompt = document.createElement('div') ;
    prompt.classList.add('blocking-prompt') ;
    prompt.textContent = `${message}` ;

    blocker.appendChild(prompt) ;
    // drawingCanvas.appendChild(blocker) ;

    return blocker ;
}

function pushBlocker(blocker) {
    drawingCanvas.appendChild(blocker)
}

function removeBlocker() {
    const blocker = document.querySelector('.game-blocker') ;
    if(blocker) blocker.remove() ;
}

function ownerPrivileges(is_owner) {
    if(is_owner) {

        // start button
        const startbtn = document.createElement('button') ;
        startbtn.classList.add('start') ;
        startbtn.textContent = 'START' ;
        drawingSectionTop.appendChild(startbtn) ;
        startbtn.addEventListener('click', (e)=>{
            socketSend({
                type: "start-game",
                id: uid
            }) ;
            startbtn.remove() ;
        }) ;

        ownerDone = true ;
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
            // if its self uid
            if(p.uid == uid) {
                isOwner = p.is_owner ;
                if(!ownerDone) ownerPrivileges(p.is_owner) ;
            }
            
            // add player in the player section 
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

            // send message in chats
        });
    }

    if(message.type == "guess") {   
        console.log(`${message.sender_name}: ${message.message}`) ;

        // a message element is being added to the chat section 
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

    if(message.type == "check") {
        console.log("heyyyyy") ;
    }

    if(message.type == "wait") {
        const blocker = createBlocker(`${message.drawer_name} is choosing a word...`) ;
        pushBlocker(blocker) ;
    }

    if(message.type == "select") {
        // console.log(message.words) ;

        const blocker = createBlocker("Choose a word...") ;
        const words = document.createElement('div') ;
        words.classList.add('words') ;
        message.words.forEach(w => {
            const word = document.createElement('div') ;
            word.classList.add('word') ;
            word.innerText = w ;

            word.addEventListener('click', (e)=>{
                const selectedWord = word.innerText ;
                socketSend({
                    type: "word-select",
                    word: selectedWord,
                    id: uid
                }) ;
                removeBlocker() ;
            }) ;

            words.appendChild(word) ;
        }) ;
        blocker.appendChild(words) ;
        pushBlocker(blocker) ;
    }

    if(message.type == "guess-start" || message.type == "start-draw") {
        removeBlocker() ;
    }

    if(message.type == "draw-begin") {
        startDrawing(message) ;
    }

    if(message.type == "draw-cont") {
        contDrawing(message) ;
    }

    if(message.type == "draw-end") {
        endDrawing(message) ;
    }

    if(message.type == "stop-draw") {
        const blocker = createBlocker(`The word was ${message.word}`) ;
        pushBlocker(blocker) 
    }
}



