var user_id = @uid@; // uid
var offset = @offset@; // смещение
var count = 1000; // сколько записей можно получить за запрос
var req_cnt = 0; // счетчик запросов к API
var resp = []; // собираемый список
var l = count; // длина ответа от API (начальное значение)
while (req_cnt<25 && l==count){
    var api_resp = API.@method@({"user_id": user_id, "count": count, "offset": offset}).items;
    resp=resp+api_resp;
    l = api_resp.length;
    req_cnt = req_cnt+1;
    offset = offset + count;
}
return {"items": resp};