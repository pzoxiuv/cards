function startCardDrag(e) {
	var style = window.getComputedStyle(e.target, null);
	var l = parseInt(style.getPropertyValue("left"), 10) - e.clientX;
	var t = parseInt(style.getPropertyValue("top"), 10) - e.clientY;
	var data = l + "," + t + "," + this.id;

	e.dataTransfer.setData("text/plain", data);
	console.log(data);
	console.log(e);
	console.log(this);
}

function dragoverCard(e) {
	var data = e.dataTransfer.getData("text/plain").split(",");
	var card = document.querySelector('#'+data[2]);
	card.style.visibility = "hidden";
	e.preventDefault();
	e.dataTransfer.dropEffect = 'copy';
	return false;
}

function dropCard(e) {
	var data = e.dataTransfer.getData("text/plain").split(",");
	var card = document.querySelector('#'+data[2]);

	console.log("dropCard");

	if (card.parentElement.id === "player-hand") {
		card.style.left = (e.clientX + parseInt(data[0], 10)) + 'px'
		//card.style.top = (e.clientY + parseInt(data[1], 10)) + 'px'
		card.style.top = card.parentElement.getBoundingClientRect().top;
		card.style.visibility = "visible";
	} else {
		console.log("Small")
		card.remove();
		e.target.appendChild(card);
		card.classList.remove("small");
	}

	var maxZIndex = undefined;
	var cards = document.querySelector('#player-hand').children;
	for (i=0; i<cards.length; i++) {
		console.log(i + ' ' + cards[i].style.zIndex + ' ' + maxZIndex);
		if (maxZIndex === undefined || maxZIndex < cards[i].style.zIndex) {
			maxZIndex = cards[i].style.zIndex;
		}
	}
	card.style.zIndex = parseInt(maxZIndex,10)+1;

	e.preventDefault();
	return false;
}

function addCardToTrick(e, isDown) {
	var data = e.dataTransfer.getData("text/plain").split(",");
	console.log(data);
	console.log(e);

	console.log("addCardToTrick");

	var card = document.querySelector('#'+data[2]);
	/*
	if (!e.target.classList.contains("player")) {
		console.log(e.target);
		console.log(card);
		card.style.visibility = "visible";
		e.preventDefault();
		return false;
	}*/

	var curTarget = e.target;
	while (curTarget.classList.contains("card")) {
		curTarget = curTarget.parentElement;
	}

	if (!curTarget.classList.contains("player") && !isDown) {
		e.preventDefault();
		return false;
	}

	console.log("remove");
	card.remove()
	console.log(curTarget);
	curTarget.appendChild(card);
	if (!card.classList.contains("small") && curTarget.id !== "player-hand") {
		card.classList.add("small");
	}
	card.style.top = card.parentElement.getBoundingClientRect().top;
	var parentX = card.parentElement.getBoundingClientRect().x;
	//card.style.left = (e.clientX + parseInt(data[0], 10)) + 'px'
	card.style.left = ((e.clientX-parentX)-(card.getBoundingClientRect().width/2)) +'px';//(e.clientX + parseInt(data[0], 10)) + 'px'
	card.style.marginLeft = '0';
	console.log(e);
	//card.style.top = (e.clientY + parseInt(data[1], 10)) + 'px'
	card.style.visibility = "visible";

	var maxZIndex = undefined;
	var cards = card.parentElement.children;
	for (i=0; i<cards.length; i++) {
		//console.log(i + ' ' + cards[i].style.zIndex + ' ' + maxZIndex);
		if (maxZIndex === undefined || maxZIndex < cards[i].style.zIndex) {
			maxZIndex = cards[i].style.zIndex;
		}
	}
	card.style.zIndex = parseInt(maxZIndex,10)+1;
	console.log(card);

	e.preventDefault();
	return false;
}
