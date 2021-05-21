//таблица Сотрудники
var table_workers_id = '';
var table_workers = SpreadsheetApp.openById(table_workers_id);

//лист Сотрудники
var sheet_workers = table_workers.getSheetByName('Лист1');

//лист Доступ
var workers_access_sheet = table_workers.getSheetByName('Доступ');

//получить элементы, которые есть в листе1, но нет в листе2
Array.prototype.diff = function(a) {
  return this.filter(function(i) {return a.indexOf(i) < 0;});
};

//буквенные индексы колонок в таблице
const alf = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO',
'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ', 'BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BG', 'BH',
'BI', 'BJ', 'BK', 'BL', 'BM', 'BN', 'BO', 'BP', 'BQ', 'BR', 'BS', 'BT', 'BU', 'BV', 'BW', 'BX', 'BY', 'BZ']

//получить все имена из листа Доступ
function getAllNamesInAccessList() {
  let data = workers_access_sheet.getDataRange().getValues();
  let workers_names = data[0];
  return workers_names.slice(1);
}

//получить все имена из листа Сотрудники
function getAllNamesInWorkersList(){
  let all_names_in_workers_list = [];
  let data = sheet_workers.getDataRange().getValues();
  for (row = 1; row < data.length; row++) {
    let worker_name = data[row][1];
    if (worker_name){
      all_names_in_workers_list.push(worker_name);
    }
  }
  return all_names_in_workers_list;
}

//получаем данные из таблицы Доступ в json формате
function getAccessDataInAccessList() {
  var data = workers_access_sheet.getDataRange().getValues();
  let usersAccessList = [];

  let workers_names = data[0];
  workers_names.splice(0, 1);
  workers_names.forEach(function(name){
    usersAccessList.push({name: name, access: []});
  })

  let districts_and_access_keys = data.slice(1);

  districts_and_access_keys.forEach(function(row) {
    row.forEach(function(item, i){
      if (i > 0 && item){
        usersAccessList[i - 1]['access'].push(row[0]);
      }
    })
  })
  return usersAccessList;
}

//получаем номер строки по имени работника
function getRowNumberByWorkerName(worker_name){
  let res = 0;
  let data = sheet_workers.getDataRange().getValues();
  data.forEach(function(item, i){
    if (item[1] === worker_name){
      return res = i + 1;
    }
  })
  return res;
}

//обновить данные в таблице Сотрудники -> Лист1
function updateAccessInWorkersList(){
  let accessData = getAccessDataInAccessList();
  accessData.forEach(function(item, i){
    let row_id = getRowNumberByWorkerName(item['name']);
    if (item['access'] !== []){
      let new_access_data = item['access'].join(', ');
      sheet_workers.getRange(`D${row_id}`).setValue(new_access_data);
    }
  })
}


// основная функция
function updateAccessList() {

  //получяем имена сотрудников из таблицы
  let names_in_workers_list = getAllNamesInWorkersList();
  let names_in_access_list = getAllNamesInAccessList();

  //получаем список новых сотрудников
  let new_workers = names_in_workers_list.diff(names_in_access_list);

  //добавление новых сотрудников в лист Доступ
  if (new_workers.length > 0){
    let updated_names_to_access_list = [names_in_access_list.concat(new_workers)];
    let count = updated_names_to_access_list[0].length;
    workers_access_sheet.getRange(`B1:${alf[count]}1`).setValues(updated_names_to_access_list);
  }

  //удаление лишних сотрудников из листа Доступ
  let deleted_workers = names_in_access_list.diff(names_in_workers_list);
  if (deleted_workers.length > 0){
    for (var el = 0; el < deleted_workers.length; el++) {
      let names_in_access_list = getAllNamesInAccessList();
      let x = names_in_access_list.indexOf(deleted_workers[el]) + 2;
      workers_access_sheet.deleteColumn(x);
    }
  }

  //добавление галочек
  let sheet_access_list_columns = workers_access_sheet.getDataRange().getNumColumns();
  let sheet_access_list_rows = workers_access_sheet.getDataRange().getNumRows();
  if (sheet_access_list_rows > 1 && sheet_access_list_columns > 1){
    workers_access_sheet.getRange(`B2:${alf[sheet_access_list_columns - 1]}${sheet_access_list_rows}`).insertCheckboxes();
  }

  //обновить данные о доступах в таблице Сотрудники -> Лист1
  updateAccessInWorkersList();
}


