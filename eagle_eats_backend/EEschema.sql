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
    account_id integer primary key,
    location text not null check(location in ('mcelroy commons', 'lions dinning hall', 'lower live')),
    menu_id integer not null,
    foreign key (account_id) references account(id),
    foreign key (menu_id) references menu(id)
);