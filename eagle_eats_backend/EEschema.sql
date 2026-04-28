drop table if exists user;
drop table if exists driver;

pragma foreign_keys = on;

create table account(
    id integer primary key autoincrement,
    username text not null unique,
    hashed_password text not null,
    first_name text,
    last_name text,
    role text not null check(role in ('user', 'driver', 'kitchen', 'admin'))
);
create table user(
    account_id integer primary key,
    student_id integer not null unique,
    foreign key (account_id) references account(id)
);

create table driver(
    account_id integer primary key,
    state text not null,
    license_id text not null,
    foreign key (account_id) references account(id),
    unique(state, license_id)
);

create table kitchen(
    id integer primary key autoincrement,
    account_id integer not null unique,
    location text not null check(
        location in (
            'carney', 
            'lyons hall', 
            'lower live',
            'addies',
            'eagles nest'
            )
    ) unique,
    description text,
    isOperating boolean,
    menu_id integer,
    foreign key (account_id) references account(id)
    --foreign key (menu_id) references menu(id)
    --implement later ^
);

create table kitchen_weekly_schedule(
    id integer primary key autoincrement,
    kitchen_id integer not null,
    day_of_week integer check(day_of_week between 1 and 7), --Sunday:1, Saturday:7
    isClosed boolean, --admin toggle for full day closure

    breakfast_open text,
    breakfast_closed text,
    lunch_open text,
    lunch_closed text,
    dinner_open text,
    dinner_closed text,

    foreign key (kitchen_id) references kitchen(id),
    unique(kitchen_id, day_of_week)
);