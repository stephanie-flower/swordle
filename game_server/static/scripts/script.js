var currentGridPosition = '00';
var lettersArray = [[],[],[],[],[],[]];

var word = "HACKER";

var won = false;

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

function checkWord() {
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
	if (items[1] != 0) {
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
	if (items[1] == 5) {
		console.log(currentGridPosition);
		activeRow(items[0] + 1);
		checkWord(lettersArray[items[0]]);
		items[0] += 1;
		items[1] = 0;
		currentGridPosition = items.join().replace(',', '')
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
	if (items[1] != 5){
		items[1] += 1;
		currentGridPosition = items.join().replace(',','');
	}
}
