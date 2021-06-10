#by concyclics
#for db_big_homework

#reset
drop database if exists fundation;
create database fundation;
use fundation;

#基金表
create table funds
(
	code varchar(20),
	name varchar(255),
	found_date date,
	sharp_rate float,
	max_down float,
	volatility float,
	primary key(code)
);

#历史净值表
create table historys
(
	code varchar(20),
	value float not null check (value>=0),
	day date,
	primary key(code,day),
	foreign key(code) references funds(code)
		on delete cascade
		on update cascade
);

#clear
delete from funds;
delete from history;

#index
create index code_ind on funds(code);
create index code_ind on history(code);
create index value_ind on history(value);
create index day_ind on history(day);
