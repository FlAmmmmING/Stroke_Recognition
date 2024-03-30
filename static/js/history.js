if (has_work === "True") {
    let show_masterpiece = document.getElementById("masterpieces");
    for (let i = 0; i < file_name_arr.length; i++) {
        let image = document.createElement("img");
        // video.src = `{{ url_for('static', filename='data/${username}/Video/${file_name_arr[i]}) }`;
        file_name_arr[i] = file_name_arr[i].trim(" ");
        image.src = "../data/" + username + "/GIF/" + file_name_arr[i];
        image.style = "max-width: 400px; height: auto; margin-right: 10px;";
        show_masterpiece.appendChild(image);
    }
}
else {
    let no_masterpiece = document.getElementById("masterpieces");
    no_masterpiece.innerHTML = "目前无作品";
}
// let show_myhistory = document.getElementById("myhistory");
// let img = document.createElement('img');
// img.src = 'data:image/gif;base64,' + bin_picture_list;
// img.style = "max-width: 400px; height: auto; margin-right: 10px;";
// show_myhistory.appendChild(img);
if (has_history === "True") {
    let show_myhistory = document.getElementById("myhistory");
    for (let i = 0; i < picture_list.length; i++) {
        let binaryString = picture_list[i];
        let img = document.createElement('img');
        img.src = 'data:image/gif;base64,' + binaryString;
        img.style = "max-width: 400px; height: auto; margin-right: 10px;";
        show_myhistory.appendChild(img);
    }
}
else {
    let no_history = document.getElementById("myhistory");
    no_history.innerHTML = "目前无历史";
}