#import libraries
import requests
import xml.etree.ElementTree as ET
import mysql.connector
from mysql.connector import errorcode


#get data from the url
url = "https://www.nicosia.org.cy/el-GR/rss/parkingspaces/"
response = requests.get(url)

#parse() method
tree = ET.fromstring(response.content)

#setting the map of the tree to extract data   
data = tree.findall('channel/item')


#setting the blueprint for all the parking data
class ParkingReading(): 
    def __init__(self, id, title, spaces, updatedon, description, geolocation_loc, geolocation_lat):
        self.id = id 
        self.title = title
        self.spaces = spaces
        self.updatedon = updatedon
        self.description = description
        self.geolocation_loc = geolocation_loc
        self.geolocation_lat = geolocation_lat
              
    def get_id(self):
        return self.id
   
    def get_title(self):
        return self.title
    
    def get_spaces(self):
        return self.spaces
    
    def get_updatedon(self):
        return self.updatedon
    
    def get_description(self):
        return self.description
    
    def get_geolocation_loc(self):
        return self.geolocation_loc
    
    def get_geolocation_lat(self):
        return self.geolocation_lat
    
    
    def set_id(self, id):
        self.id = id
    
    def set_title(self, title) :
        self.title = title
        
    def set_spaces(self, spaces):
        self.spaces = spaces
        
    def set_updatedon(self, updatedon):
        self.spaces = updatedon
        
    def set_description(self, description):
        self.description = description
        
    def set_geolocation_loc(self, geolocation_loc):
        self.geolocation_loc = geolocation_loc
        
    def set_geolocation_lat(self, geolocation_lat):
        self.geolocation_lat = geolocation_lat
        
        
       
#setting up mysql database and tables
db_name = "parkingdata"


#creating parking table on mysql
tables = {}
tables['parking'] = (
    " CREATE TABLE parking ("
    " parking_id int,"
    " title varchar(255),"
    " description varchar(255),"
    " geolocation_loc decimal(8,6),"
    " geolocation_lat decimal(8,6),"
    " PRIMARY KEY (parking_id))")

#parking_details table creation on mysql with a foreign key reference to parking table of parking_id
tables['parking_details'] = (
    " CREATE TABLE parking_details("
    " parking_details_id int NOT NULL AUTO_INCREMENT,"
    " parking_id int,"
    " spaces varchar(255),"
    " updatedon varchar(255),"
    " PRIMARY KEY (parking_details_id),"
    " FOREIGN KEY (parking_id) REFERENCES parking(parking_id))")


#establish connection with mysql and setting my cursor
cnx = mysql.connector.connect(user = 'root', password = 'Bigmanojo007')
cursor = cnx.cursor()


#creating database on mysql, also should not create again if it exist
def create_database(cursor):
    try:
        cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(db_name))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        
    try:
        cursor.execute("USE {}".format(db_name))
    except mysql.connector.Error as err:
        print("Database {} does not exist.".format(db_name))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(db_name))
            cnx.databae = db_name
        else:
            print(err)


#execute my cursor to create my database with a name parkingdata  
create_database(cursor)


#creating tables in my parkingdata database and should not create again if it exist
for table_name in tables:
    table_description = tables[table_name]
    try:
        print("Creating table {}: ".format(table_name), end ='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table already exists.")
        else:
            print(err.msg)
    else:
        print("OK")     


#a loop to iterate through the data from url and return them as text
for item in data:
    
    #an instance containing all the data of the elements 
    parkingReading = ParkingReading(item.find('id').text, item.find('title').text,
                                    item.find('spaces').text, item.find('updatedon').text,
                                    item.find('description').text, 
                                    item.find('geolocation').text[:9],
                                    item.find('geolocation').text[10:])
    
    
    #setting insert data into mysql tables BUT DO NOT re-insert if data in parking table exists
    #it can only insert into parking_details table 
    add_parking = ("INSERT IGNORE INTO parking "
                   "(parking_id, title, description, geolocation_loc, geolocation_lat) "
                   "VALUES (%s, %s, %s, %s, %s)")
    values = [parkingReading.get_id(), parkingReading.get_title(), parkingReading.get_description(),
          parkingReading.get_geolocation_loc(), parkingReading.get_geolocation_lat()]
    cursor.execute(add_parking, values)
               
    add_parking_details = ("INSERT INTO parking_details"
                           "(parking_id, spaces, updatedon)"
                           "VALUES (%s, %s, %s)")
    values = [parkingReading.get_id(), parkingReading.get_spaces(), parkingReading.get_updatedon()]
    cursor.execute(add_parking_details, values)


#commit, close cursor, and close connection
cnx.commit()    
cursor.close()
cnx.close()

    
    



    

            

            
