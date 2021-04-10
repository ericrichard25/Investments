// https://embed.plnkr.co/plunk/w4z9A4
// filter columns
$(document).ready(function(){
  
  // displays filterGrid of clicked  column header
  $(".grid thead tr th").click(function(){
    showFilterOption(this);
  });
  
});
// arrayMap is the object that contains the elements to display or hide at the end
var arrayMap = {};

function showFilterOption(thObject){
var filterGrid = $(thObject).find(".filter");

// not sure why this is needed
if (filterGrid.is(":visible")){
  filterGrid.hide();
  return;
}

// not sure why this is needed
$(".filter").hide();

var index = 0;
// clears filterGrid each time it's closed
filterGrid.empty();
// filterGrid pops up with all checkboxes checked
var allSelected = true;
// appends "Select All" checkbox at top
filterGrid.append('<div><input id="all" type="checkbox" checked>Select All</div>');

// grabs all tr's in table
var $rows = $(thObject).parents("table").find("tbody tr");

// need empty array to insert appended divs and not display duplicate values in filter box
var check_duplicates = []

$rows.each(function(ind, ele){
  // inserts class="sorting_1" in all rows of column header that was clicked
  var currentTd = $(ele).children()[$(thObject).attr("index")];
  // console.log("***")
  // console.log(ele)
  // creates empty <div></div> in filterGrid for each row of table
  var div = document.createElement("div");
  // console.log(div)
  // inserts class="grid-item" into filterGrid divs
  div.classList.add("grid-item")
  // sets var str = "checked"
  var str = $(ele).is(":visible") ? 'checked' : '';
  // console.log(str)
  if ($(ele).is(":hidden")){
    allSelected = false;
  }
  // inserts <input> tag into filterGrid div
  div.innerHTML = '<input type="checkbox" '+str+' >'+currentTd.innerHTML;
  // console.log(div.innerHTML)
  if (!check_duplicates.includes(currentTd.innerHTML)){
    // appends each div to filterGrid
    filterGrid.append(div);
    check_duplicates.push(currentTd.innerHTML);
  }
  // // appends each div to filterGrid
  // filterGrid.append(div);
  // saves ele (entire <tr></tr> with class="sorting_1" for clicked column) into arrayMap
  arrayMap[index] = ele;
  // console.log(ele)
  index++;

  // console.log(arrayMap)
  // console.log("***")
  // console.log(arrayMap);
});
// end $rows.each loop

if (!allSelected){
  filterGrid.find("#all").removeAttr("checked");
}

// adds buttons at bottom of filterGrid
filterGrid.append('<div><input id="close" type="button" value="Close"/><input id="ok" type="button" value="Ok"/></div>');
filterGrid.show();

var $closeBtn = filterGrid.find("#close");
var $okBtn = filterGrid.find("#ok");
var $checkElems = filterGrid.find("input[type='checkbox']");
var $gridItems = filterGrid.find(".grid-item");
var $all = filterGrid.find("#all");

$closeBtn.click(function(){
  filterGrid.hide();
  return false;
});

$okBtn.click(function(){
  filterGrid.find(".grid-item").each(function(ind,ele){
    if ($(ele).find("input").is(":checked")){
      $(arrayMap[ind]).show();
    }else{
      $(arrayMap[ind]).hide();
    }
  });
  filterGrid.hide();
  return false;
});

$checkElems.click(function(event){
  event.stopPropagation();
});

$gridItems.click(function(event){
  var chk = $(this).find("input[type='checkbox']");
  $(chk).prop("checked",!$(chk).is(":checked"));
});

$all.change(function(){
  var chked = $(this).is(":checked");
  filterGrid.find(".grid-item [type='checkbox']").prop("checked",chked);
})

filterGrid.click(function(event){
  event.stopPropagation();
});

return filterGrid;
}
// end filter columns