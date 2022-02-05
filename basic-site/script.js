var currentGridPosition = '00';
var lettersArray = [[],[],[],[],[],[]];

var word = "HACKER";

var won = false;

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

function nextItem(current) {
	items = current.split(""); //'01' -> ['0','1']
	for (i=0; i<items.length; i++){
		items[i] = parseInt(items[i]); //['0','1'] -> [0,1]
	}
	if (items[1] == 5){
		checkWord(lettersArray[items[0]]);
		items[0] += 1;
		items[1] = 0;
	} else {
		items[1] += 1;
	}

	return items.join().replace(',', '');
}

function selectLetter(letter) {
	currentGrid = document.getElementById(currentGridPosition);
	currentGrid.innerHTML = letter;
	lettersArray[parseInt(currentGridPosition[0])].push(letter);
	currentGridPosition = nextItem(currentGridPosition);
}