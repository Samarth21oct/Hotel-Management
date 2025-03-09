import mysql.connector as sql
import random
from datetime import datetime

# Database connection and handling class
class Database:
    def __init__(self):# Connect to MySQL database
        self.sq = sql.connect(host='localhost', user='root', passwd='durga21oct', database='hotel_')
        self.cur = self.sq.cursor()

    def execute_query(self, query, values=None):
        self.cur.execute(query, values) if values else self.cur.execute(query)
        self.sq.commit()

    def fetch_query(self, query, values=None):
        self.cur.execute(query, values) if values else self.cur.execute(query)
        return self.cur.fetchall()

    def close(self):
        self.sq.close()

class Hotel:# Hotel class for handling guest check-in, room service, and checkout
    def __init__(self):
        self.db = Database()

    def assign_room(self):# Assign a random available room number
        occupied_rooms = [room[0] for room in self.db.fetch_query('SELECT ROOM_NO FROM cust')]
        room_number = random.randint(1, 1000)
        while room_number in occupied_rooms:
            room_number = random.randint(1, 1000)
        return room_number

    def guest_info(self):# Collect and store guest information
        guest_id = int(input("Enter Guest ID: "))
        f_name = input("Enter First Name: ")
        l_name = input("Enter Last Name: ")
        country = input("Enter Country: ")
        phone_no = int(input("Enter Phone Number: "))
        proof = input("Enter ID Proof: ")
        # Room type selection
        print("Select Room Type:\n1. Maharaja (Triple Bed, Jacuzzi, All-inclusive)\n2. Deluxe (Two Bed, Jacuzzi, No Pool)\n3. Non-Deluxe (Basic Two Bed, Non-AC)")
        choice = int(input("Enter choice: "))
        room_type = "Maharaja" if choice == 1 else "Deluxe" if choice == 2 else "Non-Deluxe"
        room_no = self.assign_room()
        # Insert guest details into database
        self.db.execute_query(
            'INSERT INTO cust (ID, FIRST_NAME, LAST_NAME, COUNTRY, PH_NO, ID_PROOF, ROOM, ROOM_NO, CHECK_IN) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE())',
            (guest_id, f_name, l_name, country, phone_no, proof, room_type, room_no)
        )
        # Initialize guest service info
        self.db.execute_query(
            'INSERT INTO info (ID, FIRST_NAME, SWIMMING, ROOM_SERVICE, BILL, CHECK_OUT) VALUES (%s, %s, %s, %s, %s, NULL)',
            (guest_id, f_name, 0, 0, 0)
        )
        print("Room Assigned: ", room_no)

 # Process guest checkout and update revenue
    def checkout(self):
        guest_id = int(input("Enter Guest ID: "))
        guest_data = self.db.fetch_query('SELECT CHECK_IN, ROOM FROM cust WHERE ID = %s', (guest_id,))
        
        if not guest_data:
            print("Guest not found.")
            return
        
        self.db.execute_query('UPDATE info SET CHECK_OUT = CURDATE() WHERE ID = %s', (guest_id,))

        # Fetch checkout date and bill amount
        check_out_date = self.db.fetch_query('SELECT CHECK_OUT FROM info WHERE ID = %s', (guest_id,))[0][0]
        bill = self.db.fetch_query('SELECT BILL FROM info WHERE ID = %s', (guest_id,))[0][0]
        room_service_revenue = self.db.fetch_query('SELECT ROOM_SERVICE FROM info WHERE ID = %s', (guest_id,))[0][0]

        # Calculate room revenue (Total - Room Service)
        room_revenue = bill - room_service_revenue

        # Check if revenue for the date exists, update or insert
        existing_revenue = self.db.fetch_query('SELECT * FROM revenue WHERE DATE = CURDATE()')
        
        if existing_revenue:
            self.db.execute_query(
                'UPDATE revenue SET TOTAL_PROFIT = TOTAL_PROFIT + %s, ROOM_SERVICE_REVENUE = ROOM_SERVICE_REVENUE + %s, ROOM_REVENUE = ROOM_REVENUE + %s WHERE DATE = CURDATE()',
                (bill, room_service_revenue, room_revenue)
            )
        else:
            self.db.execute_query(
                'INSERT INTO revenue (DATE, TOTAL_PROFIT, ROOM_SERVICE_REVENUE, ROOM_REVENUE) VALUES (CURDATE(), %s, %s, %s)',
                (bill, room_service_revenue, room_revenue)
            )

        print("%16s%16s" % ("CHECK-OUT DATE", "TOTAL BILL"))
        print("%16s%16s" % (check_out_date, bill))
        print("Guest Checked Out Successfully")

#Room service method to use room services
    def room_service(self):
        guest_id = int(input("Enter Guest ID: "))
        guest_data = self.db.fetch_query('SELECT ROOM FROM cust WHERE ID = %s', (guest_id,))

        if not guest_data:
            print("Guest not found.")
            return

        room_type = guest_data[0][0]

        services = {
            "Maharaja": {"1": "In-Room Dining", "2": "Pool Access", "3": "Gym Access"},
            "Deluxe": {"1": "In-Room Dining", "2": "Gym Access"},
            "Non-Deluxe": {"1": "In-Room Dining"}
        }

        print("\nAvailable Room Services for", room_type)
        for key, value in services[room_type].items():
            print(f"{key}. {value}")

        choice = input("Enter service number: ")
        
        if choice in services[room_type]:
            selected_service = services[room_type][choice]
            service_cost = {"In-Room Dining": 500, "Pool Access": 700, "Gym Access": 600}

            self.db.execute_query(
                'UPDATE info SET ROOM_SERVICE = ROOM_SERVICE + %s, BILL = BILL + %s WHERE ID = %s',
                (service_cost[selected_service], service_cost[selected_service], guest_id)
            )

            print(f"Service '{selected_service}' added successfully! Charge: ₹{service_cost[selected_service]:,.2f}")
        else:
            print("Invalid selection.")

class Admin:
    def __init__(self, db):
        self.db = db

 # Display number of available and occupied rooms
    def show_empty_rooms(self):
        total_rooms = 1000 #Assuming Hotel as total 1000 rooms
        occupied_rooms = self.db.fetch_query('SELECT ROOM_NO FROM cust')
        occupied_count = len(occupied_rooms)
        empty_count = total_rooms - occupied_count

        room_types = self.db.fetch_query(
            "SELECT ROOM, COUNT(*) FROM cust GROUP BY ROOM"
        )

        print("\n========== ROOM OCCUPANCY REPORT ==========")
        print(f"Total Rooms: {total_rooms}")
        print(f"Occupied Rooms: {occupied_count}")
        print(f"Available Rooms: {empty_count}")

        print("\nOccupied Rooms Breakdown by Type:")
        if room_types:
            for room in room_types:
                print(f"- {room[0]} Rooms: {room[1]} occupied")
        else:
            print("No rooms are currently occupied.")

 # Display visitor details
    def show_visitor_info(self):
        visitors = self.db.fetch_query('SELECT * FROM cust')
        for visitor in visitors:
            print(visitor)

 # Calculate and display hotel profit details
    def calculate_profit(self):
        total_profit = self.db.fetch_query('SELECT SUM(BILL) FROM info')[0][0] or 0
        total_guests = self.db.fetch_query('SELECT COUNT(ID) FROM info')[0][0] or 0
        avg_bill = total_profit / total_guests if total_guests > 0 else 0
        room_service_revenue = self.db.fetch_query('SELECT SUM(ROOM_SERVICE) FROM info')[0][0] or 0
        total_room_revenue = total_profit - room_service_revenue

        revenue_by_room = self.db.fetch_query(
            "SELECT ROOM, SUM(BILL) FROM cust JOIN info ON cust.ID = info.ID GROUP BY ROOM"
        )

        print("\n========== HOTEL PROFIT REPORT ==========")
        print(f"Total Room Revenue: ₹ {total_room_revenue:,.2f}")
        print(f"Total Room Service Revenue: ₹ {room_service_revenue:,.2f}")
        print(f"Total Revenue: ₹ {total_profit:,.2f}")
        print(f"Total Guests Served: {total_guests}")
        print(f"Average Bill per Guest: ₹ {avg_bill:,.2f}")
        print("\nRevenue Breakdown by Room Type:")

        if revenue_by_room:
            for room in revenue_by_room:
                print(f"- {room[0]} Room: ₹ {room[1]:,.2f}")
        else:
            print("No revenue data available.")

    def display_bill(self):
        guest_id = int(input("Enter Guest ID: "))
        bill = self.db.fetch_query('SELECT BILL FROM info WHERE ID = %s', (guest_id,))
        if bill and bill[0][0] is not None:
            print("Total Bill: ₹", bill[0][0])
        else:
            print("Guest has not checked out yet.")

#Displays daily revenue of the hotel
    def show_daily_revenue(self):
        daily_revenue = self.db.fetch_query("SELECT * FROM revenue ORDER BY DATE DESC")
        
        if not daily_revenue:
            print("No revenue records found.")
            return

        print("\n========== DAILY REVENUE REPORT ==========")
        print("%12s%18s%22s%20s" % ("DATE", "TOTAL REVENUE", "ROOM SERVICE REVENUE", "ROOM REVENUE"))

        for record in daily_revenue:
            print("%12s%18s%22s%20s" % (record[0], record[1], record[2], record[3]))


if __name__ == "__main__":
    db = Database()
    hotel = Hotel()
    admin = Admin(db)
    
    while True:
        print("\nWelcome to Hotel Sapna Clarks Inn")
        print("Select Portal:\n1. Hotel Portal\n2. Admin Section\n3. Quit")
        portal = int(input("Enter choice: "))
        
        if portal == 1:
            while True:
                print("\nHotel Options:\n1. Enter Guest Details\n2. Display Menu\n3. Room Service\n4. Checkout\n5. Display Bill\n6. Back")
                choice = int(input("Enter choice: "))
                if choice == 1:
                    hotel.guest_info()
                elif choice == 2:
                    hotel.room_service()
                elif choice == 3:
                    print("Room Service Feature Coming Soon!")
                elif choice == 4:
                    hotel.checkout()
                elif choice == 5:
                    admin.display_bill()
                elif choice == 6:
                    break
                else:
                    print("Invalid choice")
        elif portal == 2:
            while True:
                print("\nAdmin Options:\n1. No. of Empty Rooms\n2. Visitor Info\n3. Total Profit\n4. Display Bill\n5. Back")
                choice = int(input("Enter choice: "))
                
                if choice == 1:
                    admin.show_empty_rooms()
                elif choice == 2:
                    admin.show_visitor_info()
                elif choice == 3:
                    admin.calculate_profit()
                elif choice == 4:
                    admin.display_bill()
                if choice == 5:
                    admin.show_daily_revenue()
                elif choice == 6:
                    break
                else:
                    print("Invalid choice")
        elif portal == 3:
            print("Thank you for visiting Hotel Sapna Clarks Inn")
            break
        else:
            print("Invalid choice")