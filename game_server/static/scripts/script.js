var currentGridPosition = '00';
var lettersArray = [[],[],[],[],[],[]];

var word = "HACKER";

var won = false;

// Effectively const, do not write to this
var playerId;
const roomId = JSON.parse(document.getElementById('room-id').value);

const roomSocket = new WebSocket(
		'ws://'
		+ window.location.host
		+ '/ws/session/'
		+ roomId
		+ '/'
);

//var sendGameData = {
//	'guess' = "",
//	'roomCode' = 0000
//};

//var recieveGameData = {
//	'playerColours' = [[],[],[],[],[],[]],
//	'opponentColours' = [[],[],[],[],[],[]],
//	'won' = false,
//	roomCode = 0000
//};

var colours = {
	"CORRECT_PLACEMENT" : 'green',
	"CORRECT_LETTER" : 'orange',
	"INCORRECT" : '#363636'
}

// Basically aliases to make their purpose more intuitive
function colourSquare(position, colour, safe = true) {colourCell(position, colour, safe)}
function colourKey(key, colour, safe = true) {colourCell(key, colour, safe)}
function colourCell(key, colour, safe = true) {
	if (safe) {
		// If the old colour is default, we want to overwrite anyway
		let oldColour = document.getElementById(key).style.backgroundColor;
		if (oldColour != '') {
			// Checks to make sure it isn't overwriting colour of higher value
			let newLevel = Object.values(colours).indexOf(colour);
			let oldLevel = Object.values(colours).indexOf(oldColour);
			if (newLevel >= oldLevel) return;
		}
	}
	document.getElementById(key).style.backgroundColor = colour;
}

function colourRow(response, isForMe) {
	var rightLetters = 0;
	var guess = lettersArray[parseInt(currentGridPosition[0])];
	const payload = response.payload;
	let prefix = (isForMe) ? '' : 'o';

	for (var i = 0; i < payload.values.length; i++) {
		colourSquare(prefix + response.payload.row + i, colours[payload.values[i]]);
		if (isForMe && payload.values[i] != 'CORRECT_PLACEMENT')
			colourKey(guess[i], colours[payload.values[i]]);
	}
}

function back() {
	console.log('back');
	let items = currentGridPosition.split(""); //'01' -> ['0','1']
	for (i=0; i<items.length; i++){
		items[i] = parseInt(items[i]); //['0','1'] -> [0,1]
	}

	if (items[1] == 6) {
		var tempGridPosition = currentGridPosition.split("");
		tempGridPosition[1] = parseInt(tempGridPosition[1]) - 1;
		tempGridPosition = tempGridPosition.join().replace(',','');

		lettersArray[items[0]].pop();
		document.getElementById(tempGridPosition).innerHTML = '';
		items[1] = items[1] - 1;
		currentGridPosition = items.join().replace(',','');
	}
	else if (items[1] != 0) {
		lettersArray[items[0]].pop();
		document.getElementById(currentGridPosition).innerHTML = '';
		items[1] = items[1] - 1;
		currentGridPosition = items.join().replace(',','');
	} else {
		document.getElementById(currentGridPosition).innerHTML = '';
	}
}

function activeRow(current) {
	for(i=0; i<6; i++) {
		item = document.getElementById(current + i.toString())
		item.style.boxShadow = "0px 5px rgba(0,0,0,0.5)";
		item.style.backgroundColor = "#D3D3D3";
	}
}

function enter() {
	let items = currentGridPosition.split(""); //'01' -> ['0','1']
	for (i=0; i<items.length; i++){
		items[i] = parseInt(items[i]); //['0','1'] -> [0,1]
	}
	if (items[1] == 6) {
		// Send a request to the server with this data
		let currentRow = currentGridPosition[0];
		roomSocket.send(JSON.stringify({
				'type': "SUBMIT_WORD",
				'id': playerId,
				'room': roomId,
				'payload': {
					'word': lettersArray[currentRow].join(""),
					'row': currentRow,
				}
		}));
		console.log(currentGridPosition);
		activeRow(items[0] + 1);
		// Check on the server
	}
}

function selectLetter(letter) {
	console.log(lettersArray);
	console.log(currentGridPosition);
	if (lettersArray[parseInt(currentGridPosition[0])].length < 6) {
		currentGrid = document.getElementById(currentGridPosition);
		currentGrid.innerHTML = letter;
		lettersArray[parseInt(currentGridPosition[0])].push(letter);
	}

	// nextItem
	let items = currentGridPosition.split(""); //'01' -> ['0','1']
	for (i=0; i<items.length; i++){
		items[i] = parseInt(items[i]); //['0','1'] -> [0,1]
	}
	if (items[1] != 6){
		items[1] += 1;
		currentGridPosition = items.join().replace(',','');
	}
}

// SOCKET STUFF

roomSocket.onmessage = function(e) {
		// Display the state of the row
		const data = JSON.parse(e.data);
		switch (data.payload.type) {
			case "CONNECTION_OPENED":
				document.getElementById('player-id').value = data.payload.id;
				playerId = data.payload.id;
				break;
			case "SUBMIT_WORD":
				colourRow(data, (data.payload.player == playerId));

				let items = currentGridPosition.split("");
				items[0] += 1;
				items[1] = 0;
				currentGridPosition = items.join().replace(',', '');
				break;
			case "PLAYER_WIN":
				if (playerId == data.payload.player) {
					alert("You won!");
				} else {
					alert("The opposing player won!");
				}
				break;
		}
		//document.querySelector('#chat-log').value += (data.message + '\n');
};

roomSocket.onclose = function(e) {
		//document.querySelector('#chat-log').value += "*** CONNECTION CLOSED ***";
		notifySocketClosed();
		alert("*** CONNECTION CLOSED ***");
		console.error('Game socket closed unexpectedly');
};

window.addEventListener('beforeunload', function (e) {
	notifySocketClosed();
});

function notifySocketClosed() {
	roomSocket.send(JSON.stringify({
			'type': "DISCONNECTED",
			'id': playerId,
			'room': roomId
	}));
}

roomSocket.onopen = function(e) {
		//document.querySelector('#chat-log').value += "*** Connected to Room " + roomId + " ***";
		//console.error('Game socket closed unexpectedly');
};
