var main = document.getElementById('main')
main.style.height = (window.innerHeight - 160) +'px';


var listelement = document.getElementById("listelement");
var list = document.getElementById("list");

list.style.width = (window.innerWidth - 300) + 'px';

var head = document.getElementById('categories')

head.style.width = (window.innerWidth - 300) + 'px';


for(var i = 0; i < 300; i += 1){
document.getElementById("list").appendChild(listelement.cloneNode(true));
}


window.onresize = function(event) {
  var main = document.getElementById('main')
  main.style.height = (window.innerHeight - 160) +'px';


  var listelement = document.getElementById("listelement");
  var list = document.getElementById("list");

  list.style.width = (window.innerWidth - 300) + 'px';

  var head = document.getElementById('categories')

  head.style.width = (window.innerWidth - 300) + 'px';
};
