var user_id = "@uid@"; // uid
var offset = @offset@; // смещение
var fields = "@fields@"; // дополнительные поля (sex, bdate)
var count = 1000; // сколько записей можно получить за запрос
var req_cnt = 0; // счетчик запросов к API
var resp = []; // собираемый список
var l = count; // длина ответа от API (начальное значение)
var total_count = 0;
while (req_cnt<25 && l==count){
    var api_resp = API.@method@({"user_id": user_id, "group_id": user_id, "count": count, "offset": offset, "fields": fields});
    resp=resp+api_resp.items;
    l = api_resp.items.length;
    req_cnt = req_cnt+1;
    offset = offset + count;
    total_count = api_resp.count;
}
return {"items": resp, "total_count": total_count};