# 本地书法数据库创建
create database stroke_database;
use stroke_database;

create table Customer (
    username varchar(255) primary key unique not null,
    password varchar(255) not null
);

create table PictureSet (
    pk int primary key not null auto_increment,
    username varchar(255) not null,
    PictureName varchar(255) unique not null,
    Picture longblob not null,
    CreateTime datetime not null,
    foreign key (username) references customer(username)
);

# 这里存放的是用户上传的生成视频
create table History (
    pk int primary key not null auto_increment,
    username varchar(255) not null,
    picture_name varchar(255) not null,
    picture_id int not null,
    Picture longblob not null,
    Picture_Stroke_list varchar(8192) not null,
    foreign key (username) references customer(username)
)
