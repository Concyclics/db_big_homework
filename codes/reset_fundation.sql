#by concyclics
#for db_big_homework

#reset
drop database fundation;
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
	value float not null check (value>0),
	day date,
	primary key(code,date),
	foreign key(code) references funds(code)
		on delete cascade
		on update cascade
);

#clear
delete from funds;
delete from historys;

#insert funds
#['CSI1033','CSI1032','CSI1038','CSI1029','CSI1006','CSI1065']
insert into funds values('CSI1033');
insert into funds values('CSI1032');
insert into funds values('CSI1038');
insert into funds values('CSI1029');
insert into funds values('CSI1006');
insert into funds values('CSI1065');
