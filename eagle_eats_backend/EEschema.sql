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
    foreign key (account_id) references account(id) on delete cascade
);

create table driver(
    account_id integer primary key,
    state text not null,
    license_id text not null,
    foreign key (account_id) references account(id) on delete cascade,
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
    operation text check(operation in ('Breakfast', 'Lunch', 'Dinner', 'Closed')),
    schedule_id integer default null,
    menu_id integer default null,
    foreign key (account_id) references account(id) on delete cascade,
    foreign key (schedule_id) references schedule(id) on delete set null,
    foreign key (menu_id) references menu(id) on delete set null
);

create table schedule(
    id integer primary key autoincrement,
    name text not null
);

create table kitchen_weekly_schedule(
    schedule_id integer not null,
    day_of_week integer check(day_of_week between 1 and 7), --Sunday:1, Saturday:7

    isClosed boolean, --admin toggle for full day closure

    breakfast_open text,
    breakfast_closed text,
    lunch_open text,
    lunch_closed text,
    dinner_open text,
    dinner_closed text,

    foreign key (schedule_id) references schedule(id) on delete cascade,
    primary key(schedule_id, day_of_week)
);

create table menu(
    id integer primary key autoincrement,
    name text not null
);
create table item(
    id integer,
    image_path text,
    name text not null,
    price decimal(5,2) not null
);
create table menu_item(
    menu_id integer,
    item_id integer,
    primary key (menu_id, item_id),
    foreign key (menu_id) references menu(id) on delete cascade,
    foreign key (item_id) references item(id) on delete cascade
);