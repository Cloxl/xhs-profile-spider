function get_jc(text) {
    let obj = eval(`( ${text} )`);
    return JSON.stringify(obj, null, 4);
}