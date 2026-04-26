drop table if exists user;
drop table if exists driver;

pragma foreign_keys = on;

create table user(
    id integer primary key autoincrement,
    student_id integer unique,

    first_name text not null,
    last_name text not null,

    user_name text not null unique,
    hashed_password text not null
);

create table driver(
    id integer primary key autoincrement,

    first_name text not null,
    last_name text not null,

    user_name text not null,
    hashed_password text not null
);

create table kitchen(
    id integer primary key autoincrement,
    location text not null check(location in ('mcelroy commons', 'lions dinning hall', 'lover live')),
    menu_id integer not null,
    hashed_password text not null,
    foreign key (menu_id) references menu(id)
);