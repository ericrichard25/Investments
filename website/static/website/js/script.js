
// start .toggle hide function
$(document).ready(function(){
  $('.toggle').hide();
});
// end .toggle hide function

// start user panel toggle
$("#user_panel_label").click(function(e) {
  $("#user_panel").slideToggle("fast");
});
// end user panel toggle

// start user panel close
$(".user_panel_close").click(function(e) {
  $("#user_panel").slideToggle("fast");
});
// end user panel close

// start analyster panel toggle
$("#analyster_panel_label").click(function(e) {
  $("#analyster_panel").slideToggle("fast");
});
// end analyster panel toggle

// start analyster panel close
$(".analyster_panel_close").click(function(e) {
  $("#analyster_panel").slideToggle("fast");
});
// end analyster panel close

// start quintile panel toggle
$("#quintile_panel_label").click(function(e) {
  $("#quintile_panel").slideToggle("fast");
});
// end quintile panel toggle

// start quintile panel close
$(".quintile_panel_close").click(function(e) {
  $("#quintile_panel").slideToggle("fast");
});
// end quintile panel close

// start pop()
function pop() {
    alert("Hello! I am an alert box from remote js file!!")
}
// end pop()

// start form submission ajax
$('form').submit(function(e){
  e.preventDefault();
  // Add User button
  if (e.target[8].innerText == "Add User") {
    $.ajax({
      url: 'add_user',
      method: 'post',
      data: $(this).serialize(),
      success: function(serverResponse){
        $("#user_panel").html(serverResponse);
        // separate ajax get request to retrieve last user created
        $.ajax({
          url: 'get_new_user',
          method: 'get',
          dataType: 'json',
          success: function(getResponse){
            let first_name = getResponse["first_name"]
            let last_name = getResponse["last_name"]
            $("#users_table").append(`<p class='messages'>New user ${first_name} ${last_name} created</p>`)
          },
          error: function(){
            alert("get error")
          }
        }) // end ajax get request
      },
      error: function(){
        alert("post error")      }
    }) // end ajax post request
  } // end Add User button
}); // end form submission ajax

// hover feature for navbar and footer
$( ".navbar a" ).hover(function() {
    $( this ).fadeOut( 100 );
    $( this ).fadeIn( 500 );
  });
// end hover feature for navbar and footer

  // add class "dataTable" to any table to access DataTable() function. scrollX needed to shrink the table a bit
//   $(document).ready(function() {
//     $('.dataTable').DataTable(
//       {
//         "scrollX": true
//     }
//     );
// });

// select all checkboxes in analyster table
$('#selectAll').change(function () {
  $('tbody tr td input[type="checkbox"]').prop('checked', $(this).prop('checked'));
});
// end select all checkboxes in analyster table

// analysterSearchColumn() . . . selects search column
function analysterSearchColumn(){
  var column = $("#analysterColumnSelector option:selected").val();
  return column
}
// end analysterSearchColumn()

// start analyster column search
var table = $('#analysterTable').DataTable();
$('#analysterSearchTerm').on( 'keyup', function () {
    table
        .columns( analysterSearchColumn() )
        .search( this.value )
        .draw();
} );
// end analyster column search

// // my filter function
// $(document).ready(function(){
  
//   // displays filterGrid of clicked  column header
//   $(".grid thead tr th").click(function(){
//     showFilterOption(this);
//   });
  
// });

// function showFilterOption(thObject){
// var filterGrid = $(thObject).find(".filter");

// if (filterGrid.find("#ok")){
//   console.log("ok button")
// }

// // not sure why this is needed
// if (filterGrid.is(":visible")){
//   filterGrid.hide();
//   return;
// }

// // filterGrid pops up with all checkboxes checked but not sure what else this does
// var allSelected = true;

// // appends "Select All" checkbox at top
// filterGrid.append('<div><input id="all" type="checkbox" checked> Select All</div>');

// // grabs all tr's in table
// var $rows = $(thObject).parents("table").find("tbody tr");

// // need empty array to insert appended divs and not display duplicate values in filter box
// var check_duplicates = []
// var row_values = []
// var index = 0;

// $rows.each(function(ind, ele){
//   var td = $(ele).children()[$(thObject).attr("index")].innerText
//   row_values.push(td)
//   if (!check_duplicates.includes(td)){
//     filterGrid.append('<div class="gridDiv"><input class="grid-item" type="checkbox" checked>' + td + '</div>')
//     check_duplicates.push(td)
//   }
// });
// // end $rows.each loop

// // adds "Close" and "Ok" buttons at bottom of filterGrid
// filterGrid.append('<div><input id="close" type="button" value="Close"/><input id="ok" type="button" value="Ok"/></div>');
// filterGrid.show();

// var $closeBtn = filterGrid.find("#close");
// var $okBtn = filterGrid.find("#ok");
// var $checkElems = filterGrid.find("input[type='checkbox']");
// var $gridItems = filterGrid.find(".grid-item");
// var $gridDivs = filterGrid.find(".gridDiv")
// var $all = filterGrid.find("#all");
// var $filterGridRows = filterGrid.find(".grid-item")

// $closeBtn.click(function(){
//   filterGrid.hide()
//   return false
// })

// // "Select All" checkbox
// $all.change(function(){
//   var chked = $(this).is(":checked");
//   $gridItems.each(function(ind, ele){
//     $(ele).prop("checked", chked);
//   }) 
// })

// // individual gridFilter checkboxes
// $gridItems.click(function(event){
//   var chk = $(this).find("input[type='checkbox']");
//   $(chk).prop("checked",!$(chk).is(":checked"));
// });

// // start $okBtn.click()
// $okBtn.click(function(){
//   var $checkedGridItems = []
//   $gridDivs.each(function(idx, ele){
//     if ($(ele)[0]['firstChild']['checked'] == true){
//       $checkedGridItems.push($(ele)[0].innerText)
//     }
//   })

//   // loop to show and hide filtered rows
//   $rows.each(function(idx, ele){
//     td = $(ele).children()[$(thObject).attr("index")].innerText
//     if ($checkedGridItems.includes(td)){
//       $(ele).show()
//     }else if (td == null){
//       $(ele).hide()
//     }else if (td == ""){
//       $(ele).hide()
//     }else{
//       $(ele).hide()
//     } // end if
//   }) // end loop
//   filterGrid.hide()
//   return false
// })
// // end $okBtn.click()

// // when should filterGrid be emptied?
// // filterGrid.empty();

// $checkElems.click(function(event){
//   event.stopPropagation();
// });

// filterGrid.click(function(event){
//   event.stopPropagation();
// });

// return filterGrid;
// }
// // end my filter function

// start clearFilters()
function clearFilters(){

  // for now just refreshes page
  window.location.reload();

  // var $colsTh = $("#analysterTable thead tr th")
  // console.log($colsTh)
  // $colsTh.each(function(idx, ele){
  //   // console.log($(ele))
  //   filter = $(ele).click(function(){
  //     showFilterOption(this);
  //   });
  //   console.log(filter)
  // })

  // this unhides all rows but still need to clear filters
  // var $rows = $("#analysterTable").find("tbody tr");
  // $rows.each(function(idx, ele){
  //   $(ele).show()
  // })
  
  return false
}
// end clearFilters()