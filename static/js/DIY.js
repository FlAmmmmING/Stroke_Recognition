const N = 100;
const pixel_size = 8;

var isClicked = false;
var isDrawing = false;
let start_x, start_y, end_x, end_y;

// 空间控制
let radio1 = document.getElementById("a1");
let radio6 = document.getElementById("a6");
let radio3 = document.getElementById("a3");

// 优先级设置
let dx = [-1, -1, 1, 1, 1, -1, 0, 0];
let dy = [1, -1, 1, -1, 0, 0, 1, -1];
// 用来实现操作撤销的
var history_rollback = [];
// 读取后端已经存储好的数据
let cnt = 0;
// 这是第几个图片
let picture_number = 0;
// 这里存放的是本次扫描的所有文字的map
Stroke_Data_Full = Stroke_Data_String.substring(1, Stroke_Data_String.length - 1).split(',').map(str => parseInt(str));
// 显示画板
// 100 * 100 的像素点map，在初始状态下，我们需要导入后台的短笔画
let map = Array(N).fill().map(() => Array(N));
let st = Array(N).fill().map(() => Array(N));

let canvas = document.getElementById("c1");
let ctx = canvas.getContext("2d");
canvas.width = N * pixel_size;
canvas.height = N * pixel_size;

let generate_stroke = document.getElementById('generate_stroke');
init();

// 存放的是笔画的像素点坐标
var ret_arr = [];
// 存放的是所有的笔画像素点
var full_character = [];
let radioButtons = document.querySelectorAll('input[type="radio"][name="modify"]');
radioButtons.forEach(function (radioButton) {
    radioButton.addEventListener('click', function () {
        switch (this.value) {
            case 'action1':
                // console.log("执行1号");
                canvas.addEventListener('click', option1);
                // canvas.removeEventListener('click', option2);
                canvas.removeEventListener('click', option3);
                canvas.removeEventListener('click', option6);
                canvas.removeEventListener('click', click_stroke);
                isClicked = false;
                inv_available_start_point()
                break;
            // case 'action2':
            //     canvas.addEventListener('click', option2);
            //     canvas.removeEventListener('click', option1);
            //     canvas.removeEventListener('click', option3);
            //     canvas.removeEventListener('click', option6);
            // console.log("执行2号");
            // break;
            case 'action3':
                canvas.addEventListener('click', option3);
                canvas.removeEventListener('click', option1);
                // canvas.removeEventListener('click', option2);
                canvas.removeEventListener('click', option6);
                canvas.removeEventListener('click', click_stroke);
                isClicked = false;
                inv_available_start_point()
                // console.log("执行3号");
                break;
            // case 'action4':
            //     available_start_point();
            //     canvas.removeEventListener('click', option1);
            //     // canvas.removeEventListener('click', option2);
            //     canvas.removeEventListener('click', option3);
            //     canvas.removeEventListener('click', option6);
            //     canvas.removeEventListener('click', click_stroke);
            //     // console.log("执行4号");
            //     break;
            // case 'action5':
            //     canvas.removeEventListener('click', option1);
            //     // canvas.removeEventListener('click', option2);
            //     canvas.removeEventListener('click', option3);
            //     canvas.removeEventListener('click', option6);
            //     canvas.removeEventListener('click', click_stroke);
            //     inv_available_start_point()
            //     // console.log("执行5号");
            //     break;
            case 'action6':
                canvas.addEventListener('click', option6);
                canvas.removeEventListener('click', option1);
                // canvas.removeEventListener('click', option2);
                canvas.removeEventListener('click', option3);
                canvas.removeEventListener('click', click_stroke);
                isClicked = false;
                inv_available_start_point()
                // console.log("执行5号");
                break;
        }
    })
})
// 添加事件
// canvas.addEventListener("click", detect);

function init() {
    // 清除状态
    isDrawing = false;
    isClicked = false;
    // 清除history_rollback()
    generate_stroke.textContent = "笔画方向笔画方向顺序指定(Ctrl+Q)";
    history_rollback = [];
    // 清除当前笔画
    ret_arr = [];
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < N; i++) {
        // let str = "";
        for (let j = 0; j < N; j++) {
            ctx.beginPath();
            ctx.rect(pixel_size * j, pixel_size * i, pixel_size, pixel_size);
            if (Stroke_Data_Full[cnt] === 0) {
                map[j][i] = 0;
                // 这里是笔画
                ctx.fillStyle = "#000000";
            } else if (Stroke_Data_Full[cnt] === 128) {
                map[j][i] = 128;
                // 这里是背景
                ctx.fillStyle = '#808080';
            } else {
                // 这里是骨架
                map[j][i] = 255
                ctx.fillStyle = '#ffffff';
            }
            cnt++;
            ctx.fill();
            // str += map[i][j].toString() + ' ';
        }
        // console.log(str);
        // let first = document.getElementById("back");
        let last = document.getElementById("upload");
        // if (cnt === N * N) {
        //     first.textContent = "这已经是第一张图片";
        // } else {
        //     first.textContent = "退回至上一个图片";
        // }
        if (picture_number + 1 === Stroke_Data_Full.length / (100 * 100)) {
            // last.textContent = "跳转至历史界面(Ctrl+Y)";
            last.textContent = "上传骨架，生成视频(Ctrl+Y)";
        } else {
            last.textContent = "上传骨架，生成视频(Ctrl+Y)";
        }
    }
}

function generate_current_picture() {
    for (let i = 0; i < N; i++) {
        for (let j = 0; j < N; j++) {
            ctx.beginPath();
            ctx.rect(pixel_size * i, pixel_size * j, pixel_size, pixel_size);
            // 白色表示没有被编辑的骨架
            // 黑色表示原本书法文字
            // 灰色表示原本的背景颜色
            // 红色表示用于骨架桥接的时候选择的短笔画桥截图 map[i, j] = 1
            // 紫色表示已经操作完毕的骨架 map[i, j] = 2
            // 黄色表示这个笔画的开头，即方向 map[i, j] = 3
            // 蓝色表示创建骨架的地点 map[i, j] = 4
            // 绿色表示这个笔画的可选起点 map[i, j] = 5
            switch (map[i][j]) {
                case 255:
                    ctx.fillStyle = '#ffffff';
                    break;
                case 0:
                    ctx.fillStyle = '#000000';
                    break;
                case 128:
                    ctx.fillStyle = '#808080';
                    break;
                case 1:
                    ctx.fillStyle = '#ff0000';
                    break;
                case 2:
                    ctx.fillStyle = '#a300ff';
                    break;
                case 3:
                    ctx.fillStyle = '#fff400';
                    break;
                case 4:
                    ctx.fillStyle = '#0048ff';
                    break;
                case 5:
                    ctx.fillStyle = "#11ff00";
                    break;
            }
            ctx.fill();
        }
    }
}

function single_pixel_modify(x, y) {
    // ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (map[Math.floor(x / pixel_size)][Math.floor(y / pixel_size)] === 0 || map[Math.floor(x / pixel_size)][Math.floor(y / pixel_size)] === 255) {
        add_history();
        map[Math.floor(x / pixel_size)][Math.floor(y / pixel_size)] = 255 - map[Math.floor(x / pixel_size)][Math.floor(y / pixel_size)];
        console.log(Math.floor(x / pixel_size) + " " + Math.floor(y / pixel_size));
        console.log("is: " + (255 - map[Math.floor(x / pixel_size)][Math.floor(y / pixel_size)]));
        generate_current_picture();
    }
}

// function skeleton_bridge(x, y) {
//     ctx.clearRect(0, 0, canvas.width, canvas.height);
//     if (map[Math.floor(x / pixel_size)][Math.floor(y / pixel_size)] === 255) {
//         map[Math.floor(x / pixel_size)][Math.floor(y / pixel_size)] = 1;
//         let queue = [];
//         // 寻找这个骨架的全部，并且染色染成红色
//         // 广度优先搜索
//         console.log(Math.floor(x / pixel_size).toString() + "." + Math.floor(y / pixel_size).toString());
//         queue.push([Math.floor(x / pixel_size), Math.floor(y / pixel_size)]);
//         while (queue.length) {
//             let now = queue.shift();
//             let now_x = now[0];
//             let now_y = now[1];
//             for (let i = 0; i < 8; i++) {
//                 let xx = now_x + dx[i];
//                 let yy = now_y + dy[i];
//                 if (map[xx][yy] === 255) {
//                     map[xx][yy] = 1;
//                     queue.push([xx, yy]);
//                 }
//             }
//             // console.log(now_x);
//         }
//
//         // console.log(Math.floor(x / pixel_size));
//         // console.log(Math.floor(y / pixel_size));
//
//     }
//     generate_current_picture();
// }

function delete_skeleton(x, y) {
    add_history();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (map[Math.floor(x / pixel_size)][Math.floor(y / pixel_size)] === 255) {
        map[Math.floor(x / pixel_size)][Math.floor(y / pixel_size)] = 0;
        let queue = [];
        // 寻找这个骨架的全部，并且染色染成红色
        // 广度优先搜索
        // console.log(Math.floor(x / pixel_size).toString() + "." + Math.floor(y / pixel_size).toString());
        queue.push([Math.floor(x / pixel_size), Math.floor(y / pixel_size)]);
        while (queue.length) {
            let now = queue.shift();
            let now_x = now[0];
            let now_y = now[1];
            for (let i = 0; i < 8; i++) {
                let xx = now_x + dx[i];
                let yy = now_y + dy[i];
                if (map[xx][yy] === 255) {
                    map[xx][yy] = 0;
                    queue.push([xx, yy]);
                }
            }
            // console.log(now_x);
        }

        // console.log(Math.floor(x / pixel_size));
        // console.log(Math.floor(y / pixel_size));

    }
    generate_current_picture();
}

// 第一个操作
function option1(event) {
    // 鼠标点击，获取(x, y)位置
    // generate_current_picture();
    let x = event.clientX - canvas.getBoundingClientRect().left;
    let y = event.clientY - canvas.getBoundingClientRect().top;
    single_pixel_modify(x, y);
}


// 第二个操作
// function option2(event) {
//     // 鼠标点击，获取(x, y)位置
//     // generate_current_picture();
//     let x = event.clientX - canvas.getBoundingClientRect().left;
//     let y = event.clientY - canvas.getBoundingClientRect().top;
//     skeleton_bridge(x, y);
// }

function option3(event) {
    // generate_current_picture();
    let x = event.clientX - canvas.getBoundingClientRect().left;
    let y = event.clientY - canvas.getBoundingClientRect().top;
    delete_skeleton(x, y);
}


function option6(event) {
    let x = event.clientX - canvas.getBoundingClientRect().left;
    let y = event.clientY - canvas.getBoundingClientRect().top;
    x = Math.floor(x / pixel_size);
    y = Math.floor(y / pixel_size);
    if (map[x][y] !== 0 && map[x][y] !== 4) return;
    if (!isDrawing) {
        add_history();
        start_x = x;
        start_y = y;
        map[start_x][start_y] = 4;
    } else {
        end_x = x;
        end_y = y;
        let fx = end_x - start_x;
        let fy = end_y - start_y;
        map[start_x][start_y] = 255;
        map[end_x][end_y] = 255;
        console.log(start_x);
        console.log(start_y);
        console.log(end_x);
        console.log(end_y);
        let now_x = start_x;
        let now_y = start_y;
        let max_d = Math.max(Math.abs(fx), Math.abs(fy));
        let p = 0;
        while (Math.abs(now_x - end_x) > 1.5 || Math.abs(now_y - end_y) > 1.5 && p <= max_d) {
            p++;
            now_x += fx / max_d;
            now_y += fy / max_d;
            map[Math.round(now_x)][Math.round(now_y)] = 255;
            console.log(now_x);
            console.log(now_y);
        }
        // map[end_x][end_y] = 1;
        // ctx.beginPath();
        // ctx.moveTo(start_x, start_y);
        // ctx.strokeStyle = "#ffffff";
    }
    isDrawing ^= 1;
    generate_current_picture();
}

let reset = document.getElementById('reset');
reset.addEventListener('click', function () {
    cnt -= N * N;
    init();
})

let rollback = document.getElementById('roll_back');
rollback.addEventListener('click', function () {
    if (history_rollback.length === 0) return;
    console.log(history_rollback.length);
    let history = history_rollback.pop();
    map = history[0];
    ret_arr = history[1];
    generate_current_picture();
})

// 添加历史
function add_history() {
    history_rollback.push([deepCopy(map), deepCopy(ret_arr)]);
    console.log("adding");
}

let next = document.getElementById('next');
next.addEventListener('click', function () {
    picture_number++;
    init();
})

let upload = document.getElementById('upload');
upload.addEventListener('click', function (event) {
    if (ret_arr.length === 0) {
        alert("不可上传！您没有指定任何笔画顺序！");
        return;
    }
    full_character.push(ret_arr)
    fetch("/Stroke" + Username + 'DIY' + PictureName, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({array: [picture_number, ret_arr]})
    }).then(response => response.text()).then(data => {
        // console.log(data);
        if (picture_number + 1 === Stroke_Data_Full.length / (100 * 100))
            alert("已成功提交最后一张图片！请点击\"作品与历史\"查看生成视频以及历史视频！");
        else
            alert("提交成功！已经生成这个文字的视频！稍后请去作品与历史界面查看！");
    }).catch(error => {
        console.error('Error: ', error);
    })
    if (picture_number + 1 === Stroke_Data_Full.length / (100 * 100)) {
        console.log("已成功提交最后一张图片！请点击\"作品与历史\"查看生成视频以及历史视频！");
        return;
    }
    picture_number++;
    init();
})

function available_start_point() {
    for (let i = 0; i < N; i++) {
        for (let j = 0; j < N; j++) {
            // console.log(st[i][j]);
            if (map[i][j] === 255) {
                let cnt = 0;
                for (let k = 0; k < 8; k++) {
                    let xx = dx[k] + i;
                    let yy = dy[k] + j;
                    if (map[xx][yy] === 255 || map[xx][yy] === 5) {
                        cnt++;
                    }
                }
                if (cnt <= 1) map[i][j] = 5;
            }
        }
    }
    generate_current_picture();
}

function inv_available_start_point() {
    document.getElementById('generate_stroke').textContent = "笔画方向顺序指定(Ctrl+Q)";
    for (let i = 0; i < N; i++) {
        for (let j = 0; j < N; j++) {
            // console.log(st[i][j]);
            if (map[i][j] === 5) {
                map[i][j] = 255;
            }
        }
    }
    generate_current_picture();
}

// function option4(event) {
//     let x = event.clientX - canvas.getBoundingClientRect().left;
//     let y = event.clientY - canvas.getBoundingClientRect().top;
//     x = Math.floor(x / pixel_size);
//     y = Math.floor(y / pixel_size);
//     if (map[x][y] !== 5) return;
//     history_rollback.push(deepCopy(map));
//     console.log("yes");
//     let q = []
//     q.push([x, y]);
//     while (q.length !== 0) {
//         let now = q.shift();
//         let now_x = now[0];
//         let now_y = now[1];
//         map[now_x][now_y] = 2;
//         for (let i = 0; i < 8; i++) {
//             let xx = now_x + dx[i];
//             let yy = now_y + dy[i];
//             if (map[xx][yy] === 255 || map[xx][yy] === 5) {
//                 q.push([xx, yy]);
//             }
//         }
//     }
//     generate_current_picture();
// }
function click_stroke(event) {
    let x = event.clientX - canvas.getBoundingClientRect().left;
    let y = event.clientY - canvas.getBoundingClientRect().top;
    x = Math.floor(x / pixel_size);
    y = Math.floor(y / pixel_size);
    if (map[x][y] !== 5) return;
    history_rollback.push([deepCopy(map), deepCopy(ret_arr)]);
    console.log("yes");
    let q = [];
    q.push([x, y]);
    map[x][y] = 3;
    let A_Stroke = [[x, y]];
    while (q.length !== 0) {
        let now = q.shift();
        let now_x = now[0];
        let now_y = now[1];
        // 判断这骨架是不是已经到了next
        var has_next = false;
        for (let i = 0; i < 8; i++) {
            let xx = now_x + dx[i];
            let yy = now_y + dy[i];
            if (map[xx][yy] === 255 || map[xx][yy] === 5) {
                if (!has_next) {
                    has_next = true;
                    A_Stroke.push([xx, yy]);
                }
                q.push([xx, yy]);
                map[xx][yy] = 2;
            }
        }
    }
    ret_arr.push(A_Stroke);
    generate_current_picture();
}

generate_stroke.addEventListener("click", function () {
    canvas.removeEventListener('click', option1);
    canvas.removeEventListener('click', option3);
    canvas.removeEventListener('click', option6);
    if (!isClicked) {
        available_start_point();
        radio1.checked = false;
        radio6.checked = false;
        radio3.checked = false;
        canvas.addEventListener('click', click_stroke);
        generate_stroke.textContent = "继续微调骨架";
    } else {
        inv_available_start_point();
        canvas.removeEventListener('click', click_stroke);
        generate_stroke.textContent = "笔画方向顺序指定(Ctrl+Q)";
    }
    isClicked ^= 1;
})

// 键盘监听
document.addEventListener('keydown', function (event) {
    if ((event.key === 'q' || event.key === 'Q') && event.ctrlKey) {
        canvas.removeEventListener('click', option1);
        canvas.removeEventListener('click', option3);
        canvas.removeEventListener('click', option6);
        if (!isClicked) {
            available_start_point();
            let radio1 = document.getElementById("a1");
            let radio6 = document.getElementById("a6");
            let radio3 = document.getElementById("a3");
            radio1.checked = false;
            radio6.checked = false;
            radio3.checked = false;
            canvas.addEventListener('click', click_stroke);
            generate_stroke.textContent = "继续微调骨架";
        } else {
            inv_available_start_point();
            canvas.removeEventListener('click', click_stroke);
            generate_stroke.textContent = "笔画方向顺序指定(Ctrl+Q)";
        }
        isClicked ^= 1;
    } else if ((event.key === 'y' || event.key === 'Y') && event.ctrlKey) {
        if (ret_arr.length === 0) {
            alert("不可上传！您没有指定任何笔画顺序！");
            return;
        }
        full_character.push(ret_arr)
        fetch("/Stroke" + Username + 'DIY' + PictureName, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({array: [picture_number, ret_arr]})
        }).then(response => response.text()).then(data => {
            // console.log(data);
            if (picture_number + 1 === Stroke_Data_Full.length / (100 * 100))
                alert("已成功提交最后一张图片！请点击\"作品与历史\"查看生成视频以及历史视频！");
            else
                alert("提交成功！已经生成这个文字的视频！稍后请去作品与历史界面查看！");
        }).catch(error => {
            console.error('Error: ', error);
        })
        if (picture_number + 1 === Stroke_Data_Full.length / (100 * 100)) {
            console.log("已成功提交最后一张图片！请点击\"作品与历史\"查看生成视频以及历史视频！");
            return;
        }
        picture_number++;
        init();
    } else if ((event.key === 'z' || event.key === 'Z') && event.ctrlKey) {
        if (history_rollback.length === 0) return;
        console.log(history_rollback.length);
        let history = history_rollback.pop();
        map = history[0];
        ret_arr = history[1];
        generate_current_picture();
    } else if ((event.key === 'r' || event.key === 'R') && event.ctrlKey) {
        cnt -= N * N;
        init();
    } else if (event.key === '1') {
        canvas.addEventListener('click', option1);
        canvas.removeEventListener('click', option3);
        canvas.removeEventListener('click', option6);
        canvas.removeEventListener('click', click_stroke);
        radio1.checked = true;
        inv_available_start_point();
        isClicked = false;
    } else if (event.key === '2') {
        canvas.removeEventListener('click', option1);
        canvas.removeEventListener('click', option3);
        canvas.addEventListener('click', option6);
        canvas.removeEventListener('click', click_stroke);
        radio6.checked = true;
        inv_available_start_point();
        isClicked = false;
    } else if (event.key === '3') {
        canvas.removeEventListener('click', option1);
        canvas.addEventListener('click', option3);
        canvas.removeEventListener('click', option6);
        canvas.removeEventListener('click', click_stroke);
        radio3.checked = true;
        inv_available_start_point();
        isClicked = false;
    }
});


// 深拷贝
function deepCopy(obj) {
    if (typeof obj !== 'object' || obj === null) {
        return obj; // 基本类型和 null 直接返回
    }
    let copy = Array.isArray(obj) ? [] : {}; // 创建目标对象，数组或对象
    for (let key in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, key)) {
            copy[key] = deepCopy(obj[key]); // 递归拷贝
        }
    }
    return copy; // 返回拷贝结果
}

// };

