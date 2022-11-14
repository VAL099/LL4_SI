export function onlyOneCheckBox() {
    console.log('Hello world!!!')
	var checkboxgroup = document.getElementById('diff_selector').getElementsByTagName("input");
	
    //Note #2 Change max limit here as necessary
    var limit = 1;
  
	for (var i = 0; i < checkboxgroup.length; i++) {
		checkboxgroup[i].onclick = function() {
			var checkedcount = 0;
				for (var i = 0; i < checkboxgroup.length; i++) {
				checkedcount += (checkboxgroup[i].checked) ? 1 : 0;
			}
			if (checkedcount > limit) {
				console.log("You can select maximum of " + limit + " checkbox.");
				alert("Are you sure about that? Just 1 checkbox!1");
				this.checked = false;
			}
		}
	}
}