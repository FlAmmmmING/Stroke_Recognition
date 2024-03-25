// 链接数据库
const mysql = require('mysql');


// 这里保证和flask里面的一样
const conn = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '123456',
    database: 'stroke_database'
});

// 数据库链接
conn.connect(err => {
    if (err) {
        console.log('连接失败' + err.stack);
        return;
    }
    console.log('连接成功');
});
conn.query("select * from Customer", (err, result) => {
    if (err) {
        console.log('查询失败' + err.stack);
        return;
    }
    console.log(result);
})
conn.end();