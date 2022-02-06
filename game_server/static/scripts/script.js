var currentGridPosition = '00';
var lettersArray = [[],[],[],[],[],[]];

var word = "HACKER";

var won = false;

function getPlayerId() {
	return document.getElementById('player-id').value;
}
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

function colourSquare(position, colour) {
	document.getElementById(position).style.backgroundColor = colour;
}

function colourKey(key, colour) {
	document.getElementById(key).style.backgroundColor = colour;
}

function colourRow(response) {
	var rightLetters = 0;
	var guess = lettersArray[parseInt(currentGridPosition[0])];
	const payload = response.payload;

	for (var i = 0; i < payload.values.length; i++) {
		switch(payload.values[i]) {
			case 'CORRECT_PLACEMENT':
				colourSquare(currentGridPosition[0] + i, 'green');
				// rightLetters += 1;
				break;
			case 'CORRECT_LETTER':
				colourSquare(currentGridPosition[0] + i, 'orange');
				colourKey(guess[i],'orange');
				break;
			case 'INCORRECT':
				colourSquare(currentGridPosition[0] + i, '#363636');
				colourKey(guess[i],'#363636');
				break;
		}
	}

	// if (rightLetters == 6) {
	// 	won = true;
	// 	document.getElementById('win').innerHTML = "you won";
	// }
}


function _colourRow(response) {
	var rightLetters = 0;
	wordArray = word.split("");
	guess = lettersArray[parseInt(currentGridPosition[0])];
	if (currentGridPosition == '55') {
		//document.getElementById('win').innerHTML = "you lose";
		won = false;
	} else {
		for (i=0; i<wordArray.length; i++) {
			if (wordArray[i] == guess[i]) {
				colourSquare(currentGridPosition[0] + i, 'green');
				rightLetters += 1;
			} else if(wordArray.includes(guess[i])){
				colourSquare(currentGridPosition[0] + i, 'orange');
				colourKey(guess[i],'orange');
			} else {
				colourSquare(currentGridPosition[0] + i, '#363636');
				colourKey(guess[i],'#363636');
			}
		}
		if (rightLetters == 6) {
			won = true;
			document.getElementById('win').innerHTML = "you won";
		}
	}
}

function back() {
	console.log('back');
	items = currentGridPosition.split(""); //'01' -> ['0','1']
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
	items = currentGridPosition.split(""); //'01' -> ['0','1']
	for (i=0; i<items.length; i++){
		items[i] = parseInt(items[i]); //['0','1'] -> [0,1]
	}
	if (items[1] == 6) {
		// Send a request to the server with this data
		let currentRow = currentGridPosition[0];
		roomSocket.send(JSON.stringify({
				'type': "SUBMIT_WORD",
				'payload': {
					'word': lettersArray[currentRow].join(""),
					'row': currentRow
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
	currentGrid = document.getElementById(currentGridPosition);
	currentGrid.innerHTML = letter;
	if (lettersArray[parseInt(currentGridPosition[0])].length < 6) {
		lettersArray[parseInt(currentGridPosition[0])].push(letter);
	}

	// nextItem
	items = currentGridPosition.split(""); //'01' -> ['0','1']
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
				colourRow(JSON.parse(e.data));

				items[0] += 1;
				items[1] = 0;
				currentGridPosition = items.join().replace(',', '');
				break;
			case "PLAYER_WIN":
				if (getPlayerId() == data.payload.player) {
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
			'payload': {
				'id': getPlayerId(),
				'room': roomId
			}
	}));
}

roomSocket.onopen = function(e) {
		//document.querySelector('#chat-log').value += "*** Connected to Room " + roomId + " ***";
		//console.error('Game socket closed unexpectedly');
};
