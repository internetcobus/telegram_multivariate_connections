import json
import pymssql

class DBHelper:
    def __init__(self):
        server = "winsqls02.cpt.wa.co.za"
        user = "invantageTimesheet_user"
        password = "Time$heet1"
        
        self.conn = pymssql.connect(server, user, password, "InvantageTimesheets")
        self.cursor = self.conn.cursor()

    def get_all_data(self):
        cur = self.conn.cursor()
        print('getting data')
        cur.execute("SELECT * FROM TelegramBot_LinkOwners")
        
        row_headers=[x[0] for x in cur.description] #this will extract row headers
        rv = cur.fetchall()
        json_data=[]
        for result in rv:
            json_data.append(dict(zip(row_headers,result)))
        return json.dumps(json_data)

    def add_linkUsers(self, primOwner, primOwnerName):
        stmt = "SELECT COUNT(LinkOwner) as ct FROM TelegramBot_LinkOwners WHERE LinkOwner = %s"
        args = (primOwner, )
        self.cursor.execute(stmt, args)
        recordCt = [x[0] for x in self.cursor]       


        if recordCt[0] == 0:
            return "An existing contact has to invite you before you can create link codes."
        
        stmt = "INSERT INTO TelegramBot_LinkOwners (PrimaryOwner, PrimaryOwnerName) VALUES (%s, %s)"
        args = (primOwner, primOwnerName)
        self.cursor.execute(stmt, args)
        self.conn.commit()
        return('success')


    def get_owner_requests(self, owner):
        stmt = "SELECT LinkCode FROM TelegramBot_LinkOwners WHERE PrimaryOwner = %s AND LinkConfirmed IS NULL"
        args = (owner, )
        self.cursor.execute(stmt, args)
        return [x[0] for x in self.cursor]       


    def get_owner_connections(self, owner):
        args = (owner, )
        cur = self.conn.cursor()
        cur.execute("SELECT LinkOwnerName, CAST(LinkConfirmedDate as nvarchar(100)) as LinkConfirmedDate FROM TelegramBot_LinkOwners WHERE PrimaryOwner = %s AND LinkConfirmed IS NOT NULL", args)       
        row_headers=[x[0] for x in cur.description] #this will extract row headers
        rv = cur.fetchall()
        json_data=[]
        for result in rv:
            json_data.append(dict(zip(row_headers,result)))
        return json.dumps(json_data)        


    def confirm_code(self, code, linkOwner, linkOwnerName):
        stmt = "SELECT PrimaryOwner, PrimaryOwnerName FROM TelegramBot_LinkOwners WHERE LinkCode = %s AND LinkConfirmed IS NULL"
        args = (code, )
        self.cursor.execute(stmt, args)
        primOwner = [[x[0],x[1]] for x in self.cursor]
        if len(primOwner) == 0:
            return "Error0"

        if str(linkOwner) == str(primOwner[0][0]):
            return "Error1"

        stmt = "UPDATE TelegramBot_LinkOwners SET LinkOwner = %s, LinkOwnerName = %s, LinkConfirmedDate = GETDATE(), LinkConfirmed = 1 WHERE LinkCode = %s"
        args = (linkOwner, linkOwnerName, code)
        self.cursor.execute(stmt, args)
        self.conn.commit()
        
        return(primOwner[0])

    def add_item(self, item_text, owner):
        stmt = "INSERT INTO items (description, owner) VALUES (?, ?)"
        args = (item_text, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()


    def delete_item(self, item_text, owner):
        stmt = "DELETE FROM items WHERE description = (?) AND owner = (?)"
        args = (item_text, owner )
        self.conn.execute(stmt, args)
        self.conn.commit()


    def get_items(self, owner):
        stmt = "SELECT description FROM items WHERE owner = (?)"
        args = (owner, )
        return [x[0] for x in self.conn.execute(stmt, args)]
