var user_list = [@uslist@];
var count = 1000; // сколько групп можно получить за запрос
var req_cnt = 0; // счетчик запросов
var l_index = 0; //  индекс списка
var resp = []; // список групп
var user_errors = []; // список ошибок
while (req_cnt < 25 && l_index < user_list.length) {
    var api_resp = API.groups.get({"user_id": user_list[l_index],  "count": count});
    req_cnt = req_cnt + 1;
    if (api_resp) {
        var k = api_resp.count/count;
        if (k <= 1 || (k > 1 && req_cnt + k - 1 <= 25)) {
    	    resp = resp + api_resp.items;
    	    var offset = 1; // счетчик offset
            while (k > 1) {
            	var api_resp = API.@method@({"user_id": user_list[l_index],  "count":count, "offset": offset*count});
                resp = resp + api_resp.items;
                req_cnt = req_cnt + 1;
                k = k - 1;
                offset = offset + 1;
            }
            l_index = l_index + 1;
        }
    } else {
    	user_errors.push(user_list[l_index]);
    	l_index = l_index + 1;
    }
}
return {"items": resp,"users_processed": l_index, "user_errors": user_errors};