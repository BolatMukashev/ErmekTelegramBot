var table_donor_id = '';
var table_donor = SpreadsheetApp.openById(table_donor_id);
var sheet_donor = table_donor.getSheetByName('Все');

var table_recipient_id = '';
var table_recipient = SpreadsheetApp.openById(table_recipient_id);
var sheet_recipient = table_recipient.getSheetByName('Лист1');

const states = ["Выполнен", "Отменен"]

function missionComplitted(){
  var data = sheet_donor.getDataRange().getValues();
  let splitted_products_list = {};
  for (var row = 0; row < data.length; row++) {
    let state = data[row][9];
    console.log(state);
    if (states.indexOf(state) != -1){

      let products_text = data[row][5];
      let products_list = products_text.split('\n');

      products_list.forEach(function(product, i) {
        const p_index = /\(\d+\)/;
        const regex1 = /.+📥/i;
        let res1 = regex1.exec(product);
        let product_name = res1[0].replace('📥', '').replace(p_index, '').trim();

        const regex2 = /📥 \d+ шт/;
        let res2 = regex2.exec(product);
        let count = Number(res2[0].replace('📥', '').replace('шт',''));

        splitted_products_list[product_name] = {'count': count, 'state': state};

        sheet_donor.getRange(`J${row+1}`).setValue(`${state} ✓`);
      })
    }
  }
  console.log(splitted_products_list);

  var data2 = sheet_recipient.getDataRange().getValues();
  for (var row = 0; row < data2.length; row++) {
    let original_product_name = data2[row][0];
    if (original_product_name in splitted_products_list) {
      if (splitted_products_list[original_product_name]['state'] === 'Выполнен'){
        let new_count = Number(data2[row][6]) - splitted_products_list[original_product_name]['count'];
        sheet_recipient.getRange(`G${row+1}`).setValue(new_count);
      }
      else if (splitted_products_list[original_product_name]['state'] === 'Отменен'){
        let new_count = Number(data2[row][5]) + splitted_products_list[original_product_name]['count'];
        let new_reserve_count = Number(data2[row][6]) - splitted_products_list[original_product_name]['count'];
        sheet_recipient.getRange(`F${row+1}`).setValue(new_count);
        sheet_recipient.getRange(`G${row+1}`).setValue(new_reserve_count);
      }
      else {}
    }
  }
}

/*
Принят, В работе, Выполнен, Отменен, -------------, Выполнен ✓, Отменен ✓
*/
