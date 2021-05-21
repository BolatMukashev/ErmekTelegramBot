//таблица Районы
var table_shops_id = '';
var table_shops = SpreadsheetApp.openById(table_shops_id);

//таблица Сотрудники
var table_workers_id = '';
var table_workers = SpreadsheetApp.openById(table_workers_id);

//лист Доступ
var workers_access_sheet = table_workers.getSheetByName('Доступ');

//лист Сотрудники
var workers_first_sheet = table_workers.getSheetByName('Лист1');

//получить элементы, которые есть в листе1, но нет в листе2
Array.prototype.diff = function(a) {
  return this.filter(function(i) {return a.indexOf(i) < 0;});
};

//буквенные индексы для столбцов
const alf = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO',
'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ', 'BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BG', 'BH',
'BI', 'BJ', 'BK', 'BL', 'BM', 'BN', 'BO', 'BP', 'BQ', 'BR', 'BS', 'BT', 'BU', 'BV', 'BW', 'BX', 'BY', 'BZ']

//получить названия всех районов в таблице Магазины
function getAllDistrictsNamesInShopsTable() {
  var districts = table_shops.getSheets();
  let all_districts_in_shops_table = [];
  for (i = 0; i < districts.length; i++) {
    thisSheet = districts[i];
    sheetName = thisSheet.getName();
    all_districts_in_shops_table.push(sheetName);
  }
  return all_districts_in_shops_table;
}

//получить названия всех районов из таблицы Сотрудники, лист Доступ
function getAllDistrictsNamesInWorkersTable(){
  let districts_in_workers_table = [];
  let data = workers_access_sheet.getDataRange().getValues();
  for (row = 1; row < data.length; row++) {
    let district_name = data[row][0];
    if (district_name){
      districts_in_workers_table.push(district_name);
    }
  }
  return districts_in_workers_table;
}

//основная функция
function updateAccessTable() {

  //получаем имена районов из двух таблиц
  let districts_in_shops_table = getAllDistrictsNamesInShopsTable();
  let districts_in_access_list = getAllDistrictsNamesInWorkersTable();

  //конвертируем названия из списка Доступ в формат: [район]
  let all_districts_in_access_table_list = [];
  for (i = 0; i < districts_in_access_list.length; i++){
    all_districts_in_access_table_list.push([districts_in_access_list[i]]);
  }

  //получаем список новых районов
  let new_districts = districts_in_shops_table.diff(districts_in_access_list);

  //конвертируем названия из списка Новые районы в формат: [район]
  let new_districts_list = [];
  for (i = 0; i < new_districts.length; i++){
    new_districts_list.push([new_districts[i]]);
  }

  //добавляем в лист Доступ новые районы
  if (new_districts_list.length > 0){
    let old_districts = [];
    districts_in_access_list.forEach(function(item){
      old_districts.push([item]);
    })
    let updated_districts_names_list = old_districts.concat(new_districts_list);
    console.log(updated_districts_names_list);
    workers_access_sheet.getRange(`A2:A${updated_districts_names_list.length + 1}`).setValues(updated_districts_names_list);
  }

  // удаляем лишние районы из таблицы Доступ
  let deleted_districts = districts_in_access_list.diff(districts_in_shops_table);
  if (deleted_districts.length > 0){
    for (i = 0; i < deleted_districts.length; i++) {
      let districts_in_access_list = getAllDistrictsNamesInWorkersTable();
      let x = districts_in_access_list.indexOf(deleted_districts[i]) + 2;
      workers_access_sheet.deleteRow(x);
    }
  }

  // добавляем галочки
  let sheet_access_list_columns = workers_access_sheet.getDataRange().getNumColumns();
  let sheet_access_list_rows = workers_access_sheet.getDataRange().getNumRows();
  if (sheet_access_list_rows > 1 && sheet_access_list_columns > 1){
    workers_access_sheet.getRange(`B2:${alf[sheet_access_list_columns - 1]}${sheet_access_list_rows}`).insertCheckboxes();
  }
}

