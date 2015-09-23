#!/usr/bin/python
from datetime import date, datetime, timedelta
import MySQLdb

# Current time stamp
time_stmp=datetime.now().date()
print "Today is: %s" % time_stmp
count=1

# database connection and initialization
db = MySQLdb.connect("127.0.0.1","root","root","test" )
cursor = db.cursor()

try:
	
	# create maildomain table if not exist and it is used to save daily count for domains 
	
	cursor.execute("SHOW TABLES LIKE 'maildomain'")
	result = cursor.fetchone()
	if result:
		print "maildomain table exits."
	
	else:
		cursor.execute("CREATE TABLE IF NOT EXISTS maildomain (domain VARCHAR(200) NOT NULL, count INT NOT NULL, time VARCHAR(200) NOT NULL,CONSTRAINT pk_domain PRIMARY KEY (domain,time))")
		print "maildomain table created."
	
	# Count total domain for pervious day from maildomain table 
	
	pre_total=0
	cursor.execute("SELECT SUM(count) as TOTAL from maildomain")
	results=cursor.fetchone()[0]
	if results==None:
		print "Did not find any previous record yet"
	else:
		pre_total = int(results)	
	print "total domain up to yesterday: %d" % pre_total
	
	
	# Save daily domain count to maildomain table 
	
	cursor.execute("SELECT * from mailing")
	results = cursor.fetchall()
	
	for row in results[pre_total:]:
	    data=row[0].split('@');
	    domain=data[1];
	    #print "Domain: %s" % domain; 
	    cursor.execute("INSERT INTO maildomain (domain,count,time) VALUES ('%s','%d',CURDATE()) ON DUPLICATE KEY UPDATE count=count+1"  % (domain,count) )
	    db.commit()
	
	
	# Count total domain up to today within 30 days from maildomain table                                   
	
	today_total=0
	cursor.execute("SELECT SUM(count) as TOTAL from maildomain WHERE time >= (CURDATE() - INTERVAL 30 DAY)")
	results = cursor.fetchone()[0]
	if results==None:
		print "There is no record within 30 days." 
	else:	
		today_total = int(results)
	
	print "total domains up to today within 30 days: %d" % today_total
	
	
	# Get top 50 domains by count sorted by percentage growth of the last 30 days and compared to the total domain                                                     
	
	cursor.execute("SELECT domain, sum(count)* 100.0 / '%d' as mail_perct from maildomain WHERE time >= (CURDATE() - INTERVAL 30 DAY) GROUP BY domain ORDER BY mail_perct DESC LIMIT 50" % today_total)
	results = cursor.fetchall()
	#print final results
	if results ==():
		print "Cannot find TOP 50 Growing Domain in last 30 days!"
	else:  
		print "TOP 50 Growing Domain in last 30 days:"
		for row in results:
			print "%s ---- %.2f%%" % (row[0], row[1])	
  
# check if database has any table  
except:
	print "Error: unable to fetch data"

# disconnect from server
db.close()