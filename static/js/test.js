import { createRequire } from 'module';
const require = createRequire(import.meta.url);


const fs = require('fs');

const filePath = '../data/202110310195/Short_Skeleton_data.csv';

fs.readFile(filePath, 'utf-8', (err, data) => {
    if (err) {
        console.error("error");
        return;
    }
    // console.log(data);
    csvToArray(data);
});

function csvToArray(csvData) {
    let lines = csvData.split("\n");
    var result = [];
    for (let i = 0; i < lines.length; i++) {
        var row = lines[i].split(',');
        result.push(row);
    }
    for (var i = 0; i < 13; i++) {
        for (var j = 0; j < 100 * 100; j++) {
            process.stdout.write(result[i][j] + ' ');
        }
        console.log();
    }
}